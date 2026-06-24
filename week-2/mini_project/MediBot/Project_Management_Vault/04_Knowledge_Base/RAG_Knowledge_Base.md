# RAG Knowledge Base

MediBot relies heavily on a technique called **RAG (Retrieval-Augmented Generation)** to provide accurate, hospital-specific answers to users.

## How it Works
Instead of relying solely on the LLM's pre-trained knowledge, the system:
1. Takes the user's question.
2. Converts it into a vector embedding.
3. Searches our vector databases (**ChromaDB** / **FAISS**) for the most relevant text chunks.
4. Feeds those text chunks to the LLM along with the user's question to generate a factual response.

## Knowledge Base Files
The source of truth for the embeddings are plain `.txt` files located in the `knowledge_base/` directory:

- **`billing_and_insurance.txt`**: Guidelines on accepted insurance and billing processes.
- **`hospital_faqs.txt`**: General information (visiting hours, parking, etc).
- **`patient_policies_and_rights.txt`**: Legal rights and privacy policies.
- **`pharmacy_and_prescriptions.txt`**: Protocols for prescribing and picking up medications.
- **`specialty_procedures_and_labs.txt`**: Details on specific medical procedures.
- **`symptom_triage_guidelines.txt`**: Clinical guidelines for evaluating user symptoms safely.

## Updates
Whenever hospital policies change, these `.txt` files should be updated. A script in the backend (likely inside the [[AI_Agent_App]]) must then be run to re-embed the new text into the vector stores.
