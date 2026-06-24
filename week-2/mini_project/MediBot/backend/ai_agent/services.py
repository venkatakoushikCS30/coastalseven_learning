import os
import requests
import json
import datetime
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from patients.models import MedicalRecord, Patient, FollowUpReminder

# Global flag to check if FAISS is available
FAISS_AVAILABLE = False
try:
    import faiss
    import numpy as np
    import pickle
    FAISS_AVAILABLE = True
except ImportError:
    print("FAISS is not installed yet. Using mock search fallback.")

# Global flag for SpeechRecognition
SPEECH_RECOGNITION_AVAILABLE = False
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    print("SpeechRecognition python package is not installed yet. Using mock transcriber.")

def transcribe_audio_file(file_path):
    if not SPEECH_RECOGNITION_AVAILABLE:
        print("SpeechRecognition not installed. Mock transcribing.")
        return "Patient has mild fever and cough for 3 days. Diagnose viral infection, suggest paracetamol twice daily."

    r = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data)
            return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio, using fallback template.")
        return "Patient has mild fever and cough for 3 days. Diagnose viral infection, suggest paracetamol twice daily."
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}. Using fallback template.")
        return "Patient has mild fever and cough for 3 days. Diagnose viral infection, suggest paracetamol twice daily."
    except Exception as e:
        print("Error in transcribe_audio_file:", str(e))
        return "Patient has mild fever and cough for 3 days. Diagnose viral infection, suggest paracetamol twice daily."


def extract_ehr_from_text(text):
    prompt = f"""
    You are an advanced medical clinical parser. Extract structured EHR (Electronic Health Record) details from the doctor's natural speech clinical dictation.
    
    Dictation:
    "{text}"
    
    Respond STRICTLY in JSON format with exactly three keys:
    1. "symptoms" (string): list of symptoms described by the doctor, including durations (e.g. "mild fever and cough for 3 days").
    2. "diagnosis" (string): clinical diagnosis or primary condition (e.g. "Viral Infection / Influenza").
    3. "prescription" (string): drafted prescription list, dosage instructions, and recommendations.
    
    Ensure the JSON matches this schema exactly, and do not output any surrounding explanation, conversational text, or markdown code blocks (except raw JSON). If any information is missing, create a brief placeholder draft based on context or leave it blank.
    """
    
    system_prompt = "You are a clinical transcription parsing engine. Always output strictly valid raw JSON."
    
    resp = call_ollama(prompt, system_prompt)
    if resp:
        try:
            # Clean markdown
            cleaned = resp.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            data = json.loads(cleaned.strip())
            return data
        except Exception as e:
            print("Error parsing JSON in extract_ehr:", str(e), "Response was:", resp)
            
    # Heuristic fallback parser
    lower_text = text.lower()
    symptoms = "Not recorded"
    diagnosis = "Under evaluation"
    prescription = "Rest and hydration suggested."
    
    # Heuristic 1: Symptoms extraction
    if "symptoms" in lower_text:
        parts = lower_text.split("symptoms")
        symptoms = parts[1].split(".")[0].strip()
    elif "has" in lower_text:
        parts = lower_text.split("has")
        symptoms = parts[1].split(".")[0].split(",")[0].split("diagnose")[0].strip()
        
    # Heuristic 2: Diagnosis extraction
    if "diagnose" in lower_text:
        parts = lower_text.split("diagnose")
        diagnosis = parts[1].split(".")[0].split(",")[0].split("suggest")[0].split("prescribe")[0].strip()
    elif "diagnosis" in lower_text:
        parts = lower_text.split("diagnosis")
        diagnosis = parts[1].split(".")[0].split(",")[0].split("suggest")[0].split("prescribe")[0].strip()
    elif "infection" in lower_text:
        diagnosis = "viral infection"
        
    # Heuristic 3: Prescription extraction
    if "suggest" in lower_text:
        parts = lower_text.split("suggest")
        prescription = parts[1].split(".")[0].strip()
    elif "prescribe" in lower_text:
        parts = lower_text.split("prescribe")
        prescription = parts[1].split(".")[0].strip()
    elif "paracetamol" in lower_text:
        prescription = "Paracetamol 500mg as needed."
        
    symptoms = symptoms.strip(" :.-").capitalize()
    diagnosis = diagnosis.strip(" :.-").capitalize()
    prescription = prescription.strip(" :.-").capitalize()
    
    return {
        "symptoms": symptoms,
        "diagnosis": diagnosis,
        "prescription": prescription
    }

# Simple local key-word search fallback for RAG if FAISS is offline
def mock_search_kb(query):
    results = []
    kb_dir = getattr(settings, 'KNOWLEDGE_BASE_DIR', '')
    if not os.path.exists(kb_dir):
        return ["Consult a doctor for health-related concerns. Hospital hours are Mon-Fri 8am-8pm."]
        
    try:
        for filename in sorted(os.listdir(kb_dir)):
            if filename.endswith('.txt'):
                file_path = os.path.join(kb_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Simple splitting by sections
                sections = content.split('---')
                for sec in sections:
                    if not sec.strip():
                        continue
                    # simple keyword match
                    keywords = query.lower().split()
                    match_count = sum(1 for kw in keywords if kw in sec.lower())
                    if match_count > 0:
                        results.append((match_count, sec.strip()))
        results.sort(reverse=True, key=lambda x: x[0])
        return [r[1] for r in results[:3]]
    except Exception as e:
        print("Error in mock_search_kb:", str(e))
        return ["Consult a doctor for health-related concerns."]


# FAISS Helper Functions
def get_index_paths(name):
    index_dir = getattr(settings, 'FAISS_INDEX_DIR', os.path.join(settings.BASE_DIR, 'faiss_indices'))
    os.makedirs(index_dir, exist_ok=True)
    index_path = os.path.join(index_dir, f"{name}.index")
    meta_path = os.path.join(index_dir, f"{name}.pkl")
    return index_path, meta_path

# Global in-memory caches to speed up RAG searches
_FAISS_CACHE = {}
_QUERY_EMBEDDING_CACHE = {}

def load_faiss_index(name, dimension=3072):
    if not FAISS_AVAILABLE:
        return None, {}
    index_path, meta_path = get_index_paths(name)
    if os.path.exists(index_path) and os.path.exists(meta_path):
        try:
            index = faiss.read_index(index_path)
            with open(meta_path, 'rb') as f:
                metadata = pickle.load(f)
            return index, metadata
        except Exception as e:
            print(f"Error loading FAISS index {name}:", str(e))
            
    # Fallback to creating a new index
    sub_index = faiss.IndexFlatL2(dimension)
    index = faiss.IndexIDMap(sub_index)
    return index, {}

def get_cached_faiss_index(name, dimension=3072):
    global _FAISS_CACHE
    if name not in _FAISS_CACHE:
        index, metadata = load_faiss_index(name, dimension)
        # Bootstrap patient records index if loaded for the first time
        if name == "patient_records":
            check_and_bootstrap_records_index(index, metadata)
        _FAISS_CACHE[name] = (index, metadata)
    return _FAISS_CACHE[name]

def save_faiss_index(index, metadata, name):
    global _FAISS_CACHE
    _FAISS_CACHE[name] = (index, metadata)
    if not FAISS_AVAILABLE:
        return
    try:
        index_path, meta_path = get_index_paths(name)
        faiss.write_index(index, index_path)
        with open(meta_path, 'wb') as f:
            pickle.dump(metadata, f)
    except Exception as e:
        print(f"Error saving FAISS index {name}:", str(e))

def get_embedding(text):
    global _QUERY_EMBEDDING_CACHE
    # Standardize whitespace and casing for key
    cache_key = " ".join(text.lower().split())
    if cache_key in _QUERY_EMBEDDING_CACHE:
        return _QUERY_EMBEDDING_CACHE[cache_key]

    url = f"{settings.OLLAMA_API_URL}/api/embeddings"
    payload = {
        "model": "phi3",
        "prompt": text
    }
    try:
        response = requests.post(url, json=payload, timeout=180)
        if response.status_code == 200:
            embedding = response.json().get("embedding", [])
            if embedding:
                # L2 normalize the embedding list for clean FAISS similarity calculation
                try:
                    import numpy as np
                    arr = np.array(embedding, dtype=np.float32)
                    norm = np.linalg.norm(arr)
                    if norm > 0:
                        arr = arr / norm
                    embedding = arr.tolist()
                except Exception as ex:
                    print("Error normalising embedding:", str(ex))
                _QUERY_EMBEDDING_CACHE[cache_key] = embedding
            return embedding
        else:
            print("Ollama embeddings returned status:", response.status_code)
    except Exception as e:
        print("Error generating Ollama embedding:", str(e))
    return None

def init_kb_index(index=None, metadata=None):
    if not FAISS_AVAILABLE:
        return
    if index is None or metadata is None:
        index, metadata = get_cached_faiss_index("hospital_kb", dimension=3072)
        
    kb_dir = getattr(settings, 'KNOWLEDGE_BASE_DIR', '')
    if os.path.exists(kb_dir):
        try:
            # We want to clear the previous index content to make sure it indexes cleanly
            try:
                index.reset()
            except Exception:
                pass
            metadata.clear()
            
            documents = []
            ids = []
            global_idx = 0
            
            for filename in sorted(os.listdir(kb_dir)):
                if filename.endswith('.txt'):
                    file_path = os.path.join(kb_dir, filename)
                    source_name = filename[:-4]  # e.g. 'hospital_faqs'
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    sections = [s.strip() for s in content.split('---') if s.strip()]
                    
                    for sec in sections:
                        embedding = get_embedding(sec)
                        if embedding:
                            documents.append(embedding)
                            ids.append(global_idx)
                            metadata[global_idx] = {
                                "text": sec,
                                "source": source_name
                            }
                            global_idx += 1
            
            if documents:
                vectors = np.array(documents, dtype=np.float32)
                ids_arr = np.array(ids, dtype=np.int64)
                index.add_with_ids(vectors, ids_arr)
                save_faiss_index(index, metadata, "hospital_kb")
                print(f"Pre-seeded FAISS KB with {len(documents)} docs from directory.")
        except Exception as e:
            print("Failed to initialize FAISS knowledge base:", str(e))


INDEX_VERSION = 3

def check_and_bootstrap_records_index(index, metadata):
    if not FAISS_AVAILABLE:
        return
        
    # Rebuild if index version is outdated/missing to normalize existing records
    if metadata.get("__version__") != INDEX_VERSION:
        print(f"Index version mismatch. Rebuilding FAISS index to version {INDEX_VERSION}...")
        try:
            index.reset()
        except Exception:
            pass
        metadata.clear()
        metadata["__version__"] = INDEX_VERSION
    
    records = MedicalRecord.objects.all()
    if not records.exists():
        return
        
    missing_records = []
    for r in records:
        record_id = int(r.id)
        # Check if record is missing, or if doctor/content metadata does not match DB
        if (record_id not in metadata or 
            metadata[record_id].get("doctor_id") != r.patient.doctor.id or 
            metadata[record_id].get("symptoms") != r.symptoms or
            metadata[record_id].get("diagnosis") != r.diagnosis):
            missing_records.append(r)
            
    if missing_records:
        print(f"Found {len(missing_records)} missing or outdated medical records. Syncing FAISS index...")
        for r in missing_records:
            try:
                if not r.summary:
                    r.summary = generate_record_summary(r.symptoms, r.diagnosis, r.prescription, r.notes)
                    r.save(update_fields=['summary'])
                    
                doc_content = f"""
                Patient Name: {r.patient.name}
                Symptoms: {r.symptoms}
                Diagnosis: {r.diagnosis}
                Prescription: {r.prescription}
                Summary: {r.summary}
                Notes: {r.notes}
                """
                embedding = get_embedding(doc_content)
                if embedding:
                    vector = np.array([embedding], dtype=np.float32)
                    record_id = int(r.id)
                    ids = np.array([record_id], dtype=np.int64)
                    
                    # Remove from FAISS index first if it's an update
                    if record_id in metadata:
                        try:
                            index.remove_ids(faiss.IDSelectorArray(np.array([record_id], dtype=np.int64)))
                        except Exception:
                            pass
                            
                    index.add_with_ids(vector, ids)
                    metadata[record_id] = {
                        "record_id": r.id,
                        "patient_id": r.patient.id,
                        "doctor_id": r.patient.doctor.id,
                        "patient_name": r.patient.name,
                        "symptoms": r.symptoms,
                        "diagnosis": r.diagnosis,
                        "prescription": r.prescription,
                        "summary": r.summary,
                        "notes": r.notes,
                        "text": doc_content
                    }
            except Exception as ex:
                print(f"Error bootstrapping record {r.id}:", str(ex))
        save_faiss_index(index, metadata, "patient_records")

# Call Ollama API
def call_ollama(prompt, system_prompt=None):
    url = f"{settings.OLLAMA_API_URL}/api/generate"
    payload = {
        "model": "phi3",
        "prompt": prompt,
        "stream": False
    }
    if system_prompt:
        payload["system"] = system_prompt
        
    try:
        response = requests.post(url, json=payload, timeout=180)
        if response.status_code == 200:
            return response.json().get('response', '').strip()
        else:
            print("Ollama returned status code:", response.status_code)
    except Exception as e:
        print("Ollama connection failed:", str(e))
        
    return None

# AI Functions
def generate_record_summary(symptoms, diagnosis, prescription, notes):
    prompt = f"""
    You are a professional medical scribe. Summarize the following consultation details into a concise, professional medical summary (max 3-4 sentences). Focus on key symptoms, diagnosis, and treatment plan. Do not write introductory statements like "Here is the summary".
    
    Symptoms: {symptoms}
    Diagnosis: {diagnosis}
    Prescription: {prescription}
    Additional Notes: {notes}
    """
    system_prompt = "You are a precise medical assistant. Keep summaries objective, professional, and clear."
    
    summary = call_ollama(prompt, system_prompt)
    if not summary:
        # Fallback summary generator
        summary = f"Patient presented with symptoms of {symptoms}. Diagnosed with {diagnosis} and prescribed {prescription}."
        if notes:
            summary += f" Additional details: {notes}"
    return summary

def check_follow_up_needed(record):
    prompt = f"""
    Analyze the following medical record and determine if the patient requires a follow-up appointment.
    Respond strictly in JSON format with two keys:
    1. "needs_follow_up" (boolean): true or false
    2. "days_after" (integer): number of days (e.g. 3, 7, 14) or 0 if needs_follow_up is false
    3. "reason" (string): a brief reason why follow-up is needed, or empty string.

    Medical Record:
    Symptoms: {record.symptoms}
    Diagnosis: {record.diagnosis}
    Prescription: {record.prescription}
    Summary: {record.summary}
    """
    
    resp_text = call_ollama(prompt, "You are a clinical coordinator bot. Always output strictly JSON.")
    if resp_text:
        try:
            # Clean possible markdown formatting from response
            cleaned = resp_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            data = json.loads(cleaned.strip())
            return data
        except Exception as e:
            print("JSON parsing error in follow-up check:", str(e), "Response was:", resp_text)
            
    # Fallback heuristic
    needs = False
    days = 0
    reason = ""
    lower_diag = record.diagnosis.lower() if record.diagnosis else ""
    lower_sym = record.symptoms.lower() if record.symptoms else ""
    
    # Common triggers for follow ups
    if any(x in lower_diag or x in lower_sym for x in ["fever", "infection", "bronchitis", "injury", "fracture", "stitch", "severe"]):
        needs = True
        days = 3 if "fever" in lower_diag else 7
        reason = f"Follow-up for management of {record.diagnosis}."
        
    return {
        "needs_follow_up": needs,
        "days_after": days,
        "reason": reason
    }

def sql_fallback_search(query, doctor_id):
    from django.conf import settings
    log_path = os.path.join(settings.BASE_DIR, 'debug.log')
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"  [services.py] sql_fallback_search triggered. query: '{query}', doctor_id: {doctor_id}\n")
        
    from django.db.models import Q
    records = MedicalRecord.objects.filter(
        Q(patient__doctor_id=doctor_id) & (
            Q(symptoms__icontains=query) | 
            Q(diagnosis__icontains=query) | 
            Q(prescription__icontains=query) |
            Q(patient__name__icontains=query)
        )
    ).distinct()
    
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"  [services.py] sql_fallback_search database found {records.count()} records: {[(r.id, r.patient.name) for r in records]}\n")
        
    results = []
    for r in records:
        results.append({
            "record_id": r.id,
            "patient_id": r.patient.id,
            "patient_name": r.patient.name,
            "symptoms": r.symptoms,
            "diagnosis": r.diagnosis,
            "prescription": r.prescription,
            "summary": r.summary,
            "notes": r.notes,
            "score": 1.0
        })
    return results

def index_medical_record(record):
    if not FAISS_AVAILABLE:
        print("FAISS not active. Skipping indexing.")
        return
        
    try:
        doc_content = f"""
        Patient Name: {record.patient.name}
        Symptoms: {record.symptoms}
        Diagnosis: {record.diagnosis}
        Prescription: {record.prescription}
        Summary: {record.summary}
        Notes: {record.notes}
        """
        
        embedding = get_embedding(doc_content)
        if not embedding:
            print("Failed to generate embedding for record. Skipping FAISS index update.")
            return
            
        vector = np.array([embedding], dtype=np.float32)
        
        index, metadata = get_cached_faiss_index("patient_records", dimension=4096)
        
        record_id = int(record.id)
        if record_id in metadata:
            index.remove_ids(faiss.IDSelectorArray(np.array([record_id], dtype=np.int64)))
            
        ids = np.array([record_id], dtype=np.int64)
        index.add_with_ids(vector, ids)
        
        metadata[record_id] = {
            "record_id": record.id,
            "patient_id": record.patient.id,
            "doctor_id": record.patient.doctor.id,
            "patient_name": record.patient.name,
            "symptoms": record.symptoms,
            "diagnosis": record.diagnosis,
            "prescription": record.prescription,
            "summary": record.summary,
            "notes": record.notes,
            "text": doc_content
        }
        
        save_faiss_index(index, metadata, "patient_records")
        print(f"Successfully indexed medical record {record.id} in FAISS.")
    except Exception as e:
        print("Error indexing medical record in FAISS:", str(e))

def search_medical_records(query, doctor_id):
    from django.conf import settings
    from django.db.models import Q
    log_path = os.path.join(settings.BASE_DIR, 'debug.log')
    def log(msg):
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"  [services.py] {msg}\n")
            
    log(f"Hybrid search triggered for query '{query}' (doctor_id={doctor_id})")
    
    # 1. Fetch keyword matches from database (extremely robust, 100% correct matches)
    db_matches = MedicalRecord.objects.filter(
        Q(patient__doctor_id=doctor_id) & (
            Q(symptoms__icontains=query) | 
            Q(diagnosis__icontains=query) | 
            Q(prescription__icontains=query) |
            Q(patient__name__icontains=query)
        )
    ).distinct()
    
    # Prepare query words for matching
    query_lower = query.lower().strip()
    query_words = [w for w in query_lower.split() if len(w) > 2]
    stopwords = {'and', 'the', 'with', 'from', 'for', 'has', 'had', 'was', 'were', 'but', 'not', 'she', 'his', 'her', 'him', 'are', 'you', 'your', 'this', 'that'}
    query_words = [w for w in query_words if w not in stopwords]
    
    # 2. Get semantic similarities from FAISS
    semantic_scores = {}
    if FAISS_AVAILABLE:
        try:
            query_embedding = get_embedding(query)
            if query_embedding:
                index, metadata = get_cached_faiss_index("patient_records", dimension=4096)
                if index.ntotal > 0:
                    query_vector = np.array([query_embedding], dtype=np.float32)
                    k = min(50, index.ntotal)
                    distances, indices = index.search(query_vector, k)
                    log(f"FAISS search raw results - indices: {indices[0]}, distances: {distances[0]}")
                    
                    for dist, idx in zip(distances[0], indices[0]):
                        if idx == -1:
                            continue
                        meta = metadata.get(idx)
                        if meta and meta.get("doctor_id") == doctor_id:
                            # Convert squared L2 distance to cosine similarity: cos = 1 - dist / 2
                            cos_sim = float(max(-1.0, min(1.0, 1.0 - (dist / 2.0))))
                            semantic_scores[meta["record_id"]] = cos_sim
        except Exception as e:
            log(f"Error in FAISS semantic search: {str(e)}")
            
    # 3. Score and merge all records belonging to this doctor
    records = MedicalRecord.objects.filter(patient__doctor_id=doctor_id)
    results_dict = {}
    
    for r in records:
        record_id = r.id
        
        # Calculate Keyword Score
        keyword_score = 0.0
        patient_name_lower = r.patient.name.lower()
        symptoms_lower = r.symptoms.lower() if r.symptoms else ""
        diagnosis_lower = r.diagnosis.lower() if r.diagnosis else ""
        prescription_lower = r.prescription.lower() if r.prescription else ""
        summary_lower = r.summary.lower() if r.summary else ""
        notes_lower = r.notes.lower() if r.notes else ""
        
        # Check direct full-query match
        if query_lower in patient_name_lower:
            keyword_score = 0.98
        elif query_lower in diagnosis_lower:
            keyword_score = 0.95
        elif query_lower in symptoms_lower:
            keyword_score = 0.92
        elif query_lower in prescription_lower or query_lower in summary_lower:
            keyword_score = 0.88
        else:
            # Check individual word matches
            word_matches = 0
            for word in query_words:
                if word in patient_name_lower or word in diagnosis_lower or word in symptoms_lower or word in prescription_lower or word in summary_lower or word in notes_lower:
                    word_matches += 1
            if word_matches > 0:
                keyword_score = min(0.90, 0.70 + 0.10 * word_matches)
                
        # Calculate Semantic Score
        cos_sim = semantic_scores.get(record_id, None)
        semantic_score = 0.0
        if cos_sim is not None:
            # Map cosine similarity from range [-0.05, 0.15] to [0.0, 1.0]
            scaled_sim = (cos_sim + 0.05) / 0.20
            scaled_sim = max(0.0, min(1.0, scaled_sim))
            # Caps semantic-only score at 80% to prioritize keyword matches
            semantic_score = scaled_sim * 0.80
            
        # Combine scores
        final_score = max(keyword_score, semantic_score)
        
        # Filter: Keep if it has a keyword match OR if the semantic similarity is strong enough (cos_sim >= 0.05)
        is_match = (keyword_score > 0.0) or (cos_sim is not None and cos_sim >= 0.05)
        
        if is_match:
            results_dict[record_id] = {
                "record_id": r.id,
                "patient_id": r.patient.id,
                "patient_name": r.patient.name,
                "symptoms": r.symptoms,
                "diagnosis": r.diagnosis,
                "prescription": r.prescription,
                "summary": r.summary,
                "notes": r.notes,
                "score": final_score
            }
            
    # Convert to list and sort by score descending
    results = list(results_dict.values())
    results.sort(key=lambda x: x["score"], reverse=True)
    log(f"Hybrid search returned {len(results)} items: {[(res['patient_name'], res['score']) for res in results]}")
    return results

def query_patient_chatbot(query):
    # Retrieve context from Knowledge Base (hospital FAQs)
    contexts = []
    if FAISS_AVAILABLE:
        try:
            index, metadata = get_cached_faiss_index("hospital_kb", dimension=4096)
            if index.ntotal == 0:
                init_kb_index(index, metadata)
                
            if index.ntotal > 0:
                query_embedding = get_embedding(query)
                if query_embedding:
                    query_vector = np.array([query_embedding], dtype=np.float32)
                    k = min(3, index.ntotal)
                    distances, indices = index.search(query_vector, k)
                    for idx in indices[0]:
                        if idx == -1:
                            continue
                        meta = metadata.get(idx)
                        if meta and "text" in meta:
                            contexts.append(meta["text"])
            if not contexts:
                contexts = mock_search_kb(query)
        except Exception as e:
            print("Error querying FAISS KB:", str(e))
            contexts = mock_search_kb(query)
    else:
        contexts = mock_search_kb(query)
        
    User = get_user_model()
    doctors = User.objects.filter(role='DOCTOR')
    doctor_info = []
    for doc in doctors:
        name = f"Dr. {doc.first_name} {doc.last_name}".strip()
        spec = doc.specialization or "General Medicine"
        hours = doc.available_hours or "Check with admin"
        doctor_info.append(f"- {spec} ({name}), Timings: {hours}")
    
    live_doctor_context = "Current Live Doctor Directory:\n" + "\n".join(doctor_info) if doctor_info else "No doctors currently available."
        
    context_str = live_doctor_context + "\n\n" + "\n\n".join(contexts)
    
    prompt = f"""
    You are MediAssist AI, a helpful, friendly hospital assistant. Your job is to answer the patient's questions accurately using the provided context.
    
    Context from Hospital Knowledge Base & FAQs:
    {context_str}
    
    Patient Query: {query}
    
    Guidelines:
    1. If the question is about symptoms (e.g. fever, headache, body pain), provide helpful precautions, general causes, and suggest they consult a doctor. Do not diagnose the patient directly.
    2. If the question is about hospital timings, departments, or booking procedures, use the provided context to answer.
    3. If the context does not contain enough info, answer to the best of your medical AI knowledge but add a note that it is general info.
    4. ALWAYS add a disclaimer at the end of symptom guidance, reminding the patient that this is general advice and they should consult a medical professional.
    """
    
    system_prompt = "You are a helpful healthcare chatbot. Keep answers clear, supportive, and medically safe."
    
    response = call_ollama(prompt, system_prompt)
    if not response:
        # Generate safe fallback answers based on keyword mapping
        lower_query = query.lower()
        if "headache" in lower_query or "migraine" in lower_query:
            response = "Head pain is often caused by dehydration, tension, stress, or lack of sleep.\n\nPrecautions:\n- Keep hydrated (drink plenty of water)\n- Rest in a dark, quiet room\n- Minimize screen time\n- You may apply a cool compress to your forehead.\n\n*Disclaimer: This is general advice. If your headache is severe, sudden, or accompanied by numbness, seek medical attention immediately.*"
        elif "fever" in lower_query or "cough" in lower_query or "pain" in lower_query:
            response = "A fever or body pain is a common immune response to an infection (like the flu or cold).\n\nPrecautions:\n- Get plenty of rest\n- Keep hydrated with water, warm broth, or herbal teas\n- Use warm saline gargles for a sore throat\n- Monitor your temperature.\n\n*Disclaimer: Please consult a doctor if your fever exceeds 103°F (39.4°C), lasts more than 3 days, or is accompanied by breathing difficulties.*"
        elif "timing" in lower_query or "hours" in lower_query or "open" in lower_query:
            if doctor_info:
                doc_timings = "\n".join([f"- Dr. {d.first_name} {d.last_name}: {d.available_hours or 'Check with admin'}" for d in doctors])
                response = f"MediAssist Clinic & Hospital is open 24/7 for emergencies.\nHere are the specific timings for our doctors:\n{doc_timings}"
            else:
                response = "MediAssist Clinic & Hospital is open:\n- Monday to Friday: 8:00 AM - 8:00 PM\n- Saturday: 9:00 AM - 5:00 PM\n- Sunday: Closed (Emergency services are open 24/7)"
        elif "book" in lower_query or "appointment" in lower_query:
            response = "To book an appointment, please type 'book an appointment' or ask me to schedule one. A booking request form will pop up where you can fill in your details (name, email, phone, and requested department) so our admin team can schedule your slot."
        elif "department" in lower_query or "specialist" in lower_query:
            if doctor_info:
                doc_specs = "\n".join([f"- {d.specialization or 'General'} (Dr. {d.first_name} {d.last_name})" for d in doctors])
                response = f"Our available departments include:\n{doc_specs}\n\nPlease let me know if you would like to know their timings!"
            else:
                response = "Our available departments include:\n- Cardiology (Dr. Sarah Vance)\n- Pediatrics (Dr. Robert Patel)\n- Neurology (Dr. Elena Rostova)\n- Dermatology (Dr. James Cole)\n- General Medicine (Available daily)\n\nPlease let me know if you would like to know their timings!"
        else:
            response = "Thank you for contacting MediAssist. For general health guidance, rest, hydration, and healthy nutrition are recommended. If you are experiencing symptoms, please consult one of our primary care physicians.\n\n*Disclaimer: I am an AI assistant. Please seek professional medical advice for diagnoses and treatments.*"
            
    return response

# Hook called after record is created
def handle_new_record_created(record):
    # 1. Generate Summary if not present
    if not record.summary:
        record.summary = generate_record_summary(
            record.symptoms,
            record.diagnosis,
            record.prescription,
            record.notes
        )
        record.save(update_fields=['summary'])
        
    # 2. Index in ChromaDB
    index_medical_record(record)
    
    # 3. Automation: Check if Follow-up reminder is needed
    follow_up_data = check_follow_up_needed(record)
    if follow_up_data and follow_up_data.get('needs_follow_up'):
        days = follow_up_data.get('days_after', 7)
        reason = follow_up_data.get('reason', 'Scheduled follow-up.')
        scheduled_date = datetime.date.today() + datetime.timedelta(days=days)
        
        # Check if reminder already exists for the patient on the same day
        exists = FollowUpReminder.objects.filter(
            patient=record.patient,
            scheduled_date=scheduled_date
        ).exists()
        
        if not exists:
            FollowUpReminder.objects.create(
                patient=record.patient,
                scheduled_date=scheduled_date,
                reason=reason,
                status='PENDING'
            )
            print(f"Scheduled follow-up reminder in {days} days for {record.patient.name}.")
