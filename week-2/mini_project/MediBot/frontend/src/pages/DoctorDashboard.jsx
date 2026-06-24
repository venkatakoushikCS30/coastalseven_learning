import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  Users, Plus, Search, Mic, MicOff, Sparkles, ClipboardList, LogOut, Check,
  Calendar, User, RefreshCw, AlertCircle, FileText, ChevronRight, Activity, Mail
} from 'lucide-react';

const DoctorDashboard = () => {
  const [patients, setPatients] = useState([]);
  const [masterPatients, setMasterPatients] = useState([]);
  const [reminders, setReminders] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [searchLoading, setSearchLoading] = useState(false);
  const [error, setError] = useState('');
  const [aiUsageCount, setAiUsageCount] = useState(0);

  // New Patient Form State
  const [showAddPatient, setShowAddPatient] = useState(false);
  const [newName, setNewName] = useState('');
  const [newAge, setNewAge] = useState('');
  const [newGender, setNewGender] = useState('Male');
  const [newEmail, setNewEmail] = useState('');
  const [emailingRecordId, setEmailingRecordId] = useState(null);

  // Edit Patient Form State
  const [showEditPatient, setShowEditPatient] = useState(false);
  const [editName, setEditName] = useState('');
  const [editAge, setEditAge] = useState('');
  const [editGender, setEditGender] = useState('Male');
  const [editEmail, setEditEmail] = useState('');
  const [editPatientSaving, setEditPatientSaving] = useState(false);

  // New Record Form State
  const [showAddRecord, setShowAddRecord] = useState(false);
  const [symptoms, setSymptoms] = useState('');
  const [diagnosis, setDiagnosis] = useState('');
  const [prescription, setPrescription] = useState('');
  const [notes, setNotes] = useState('');
  const [summary, setSummary] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [saveLoading, setSaveLoading] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [isDictatingEHR, setIsDictatingEHR] = useState(false);
  const [dictationLoading, setDictationLoading] = useState(false);
  const [dictationText, setDictationText] = useState('');

  // Web Speech API Voice States
  const [isRecordingSymptoms, setIsRecordingSymptoms] = useState(false);
  const [isRecordingNotes, setIsRecordingNotes] = useState(false);
  
  const navigate = useNavigate();
  const token = localStorage.getItem('token');

  // Profile Tab State
  const [activeTab, setActiveTab] = useState('patients');
  const [profileCompleted, setProfileCompleted] = useState(true);
  const [profileSpecialization, setProfileSpecialization] = useState('');
  const [profileStudy, setProfileStudy] = useState('');
  const [profileHours, setProfileHours] = useState('');
  const [profileUsername, setProfileUsername] = useState('');
  const [profileEmail, setProfileEmail] = useState('');
  const [profileStatusMsg, setProfileStatusMsg] = useState({ type: '', text: '' });
  const [profileSaving, setProfileSaving] = useState(false);

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    fetchDashboardData();
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    try {
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };
      const res = await axios.get('http://localhost:8000/api/auth/profile/', config);
      const spec = res.data.specialization || '';
      const std = res.data.study || '';
      const hrs = res.data.available_hours || '';

      setProfileSpecialization(spec);
      setProfileStudy(std);
      setProfileHours(hrs);
      setProfileUsername(res.data.username || '');
      setProfileEmail(res.data.email || '');

      const isCompleted = spec.trim() !== '' && std.trim() !== '' && hrs.trim() !== '';
      setProfileCompleted(isCompleted);

      if (!isCompleted) {
        setActiveTab('profile');
      }

      // Refresh fullName display if first_name/last_name exists
      if (res.data.first_name || res.data.last_name) {
        const full = `${res.data.first_name || ''} ${res.data.last_name || ''}`.trim() || res.data.username;
        localStorage.setItem('fullName', full);
      }
    } catch (err) {
      console.error("Failed to load doctor profile:", err);
    }
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setProfileSaving(true);
    setProfileStatusMsg({ type: '', text: '' });
    try {
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };
      const payload = {
        specialization: profileSpecialization,
        study: profileStudy,
        available_hours: profileHours
      };
      const res = await axios.put('http://localhost:8000/api/auth/profile/', payload, config);
      
      const spec = res.data.specialization || '';
      const std = res.data.study || '';
      const hrs = res.data.available_hours || '';

      setProfileSpecialization(spec);
      setProfileStudy(std);
      setProfileHours(hrs);

      const isCompleted = spec.trim() !== '' && std.trim() !== '' && hrs.trim() !== '';
      setProfileCompleted(isCompleted);

      if (isCompleted) {
        setProfileStatusMsg({ type: 'success', text: 'Profile updated successfully! Clinical access is now unlocked.' });
      } else {
        setProfileStatusMsg({ type: 'success', text: 'Profile updated, but some fields are still missing. Please fill all fields to unlock dashboard.' });
      }
    } catch (err) {
      console.error(err);
      setProfileStatusMsg({ type: 'error', text: 'Failed to update profile. Please try again.' });
    } finally {
      setProfileSaving(false);
    }
  };

  const fetchDashboardData = async () => {
    setLoading(true);
    setError('');
    try {
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      const [patientsRes, remindersRes] = await Promise.all([
        axios.get('http://localhost:8000/api/patients/', config),
        axios.get('http://localhost:8000/api/reminders/', config)
      ]);

      setPatients(patientsRes.data);
      setMasterPatients(patientsRes.data);
      setReminders(remindersRes.data);
      
      // Calculate mock AI Usage count from records containing summaries
      let count = 0;
      patientsRes.data.forEach(p => {
        if (p.records) {
          p.records.forEach(r => {
            if (r.summary) count++;
          });
        }
      });
      setAiUsageCount(count);

      // Select first patient by default if available
      if (patientsRes.data.length > 0 && !selectedPatient) {
        setSelectedPatient(patientsRes.data[0]);
      }
    } catch (err) {
      console.error(err);
      setError('Failed to sync dashboard data. Check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  // Handle automatic and debounced patient search (unified Name & Semantic Search)
  useEffect(() => {
    let active = true;
    let timerId = null;

    const performSearch = async () => {
      // Handle empty search: instantly reset list to master list
      if (!searchQuery.trim()) {
        setPatients(masterPatients);
        if (masterPatients.length > 0) {
          const isSelectedStillVisible = masterPatients.some(p => p.id === selectedPatient?.id);
          if (!isSelectedStillVisible && (!selectedPatient || !selectedPatient.isSearchResult)) {
            setSelectedPatient(masterPatients[0]);
          }
        } else {
          setSelectedPatient(null);
        }
        setSearchLoading(false);
        return;
      }

      // Step 1: Instantly run local Name Search to ensure 0ms lag
      const nameMatches = masterPatients.filter(p =>
        p.name.toLowerCase().includes(searchQuery.toLowerCase())
      ).map(p => {
        // Enriched with 1.0 (100%) relevance score for instant local name matches
        const enrichedRecords = p.records && p.records.length > 0 
          ? p.records.map((r, idx) => idx === 0 ? { ...r, relevanceScore: 1.0 } : r) 
          : [{ id: 'name-match', relevanceScore: 1.0, created_at: new Date().toISOString() }];
        return {
          ...p,
          isSearchResult: true,
          records: enrichedRecords
        };
      });
      
      if (active) {
        setPatients(nameMatches);
        if (nameMatches.length > 0) {
          const isSelectedStillVisible = nameMatches.some(p => p.id === selectedPatient?.id);
          if (!isSelectedStillVisible) {
            setSelectedPatient(nameMatches[0]);
          }
        } else {
          setSelectedPatient(null);
        }
      }

      // Step 2: Run debounced Backend RAG AI Search to match symptoms/diagnoses
      setSearchLoading(true);
      timerId = setTimeout(async () => {
        try {
          const config = {
            headers: { Authorization: `Bearer ${token}` }
          };
          const res = await axios.post('http://localhost:8000/api/ai/search/', {
            query: searchQuery
          }, config);

          if (active) {
            const searchResults = res.data.results || [];
            
            // Map RAG results and enrich with full historical records from our local cache
            const mappedPatients = searchResults.map(r => {
              const matchedPatient = masterPatients.find(p => p.id === r.patient_id);
              const fullRecords = matchedPatient ? matchedPatient.records : [];
              const enrichedRecords = fullRecords.map(rec => {
                if (rec.id === r.record_id) {
                  return {
                    ...rec,
                    relevanceScore: r.score
                  };
                }
                return rec;
              });

              const finalRecords = enrichedRecords.length > 0 ? enrichedRecords : [{
                id: r.record_id,
                symptoms: r.symptoms,
                diagnosis: r.diagnosis,
                prescription: r.prescription,
                notes: r.notes,
                summary: r.summary,
                created_at: new Date().toISOString(),
                relevanceScore: r.score
              }];

              return {
                id: r.patient_id,
                name: r.patient_name,
                age: matchedPatient ? matchedPatient.age : 0,
                gender: matchedPatient ? matchedPatient.gender : 'Unknown',
                isSearchResult: true,
                records: finalRecords
              };
            });

            // Step 3: Merge Name Matches & RAG Semantic Matches without duplicates
            const merged = [...nameMatches];
            mappedPatients.forEach(ragPatient => {
              const existingIndex = merged.findIndex(p => p.id === ragPatient.id);
              if (existingIndex === -1) {
                merged.push(ragPatient);
              } else {
                // If it already matches by name, merge the relevance score into its records, keeping the highest score
                const patientWithRecords = masterPatients.find(p => p.id === ragPatient.id) || merged[existingIndex];
                const updatedRecords = patientWithRecords.records.map(rec => {
                  const ragRec = ragPatient.records.find(r => r.id === rec.id);
                  if (ragRec && ragRec.relevanceScore !== undefined) {
                    const currentScore = rec.relevanceScore || 0;
                    return { ...rec, relevanceScore: Math.max(currentScore, ragRec.relevanceScore) };
                  }
                  return rec;
                });
                merged[existingIndex] = {
                  ...patientWithRecords,
                  isSearchResult: true,
                  records: updatedRecords
                };
              }
            });

            setPatients(merged);
            
            if (merged.length > 0) {
              const isSelectedStillVisible = merged.some(p => p.id === selectedPatient?.id);
              if (!isSelectedStillVisible) {
                setSelectedPatient(merged[0]);
              }
            } else {
              setSelectedPatient(null);
            }
          }
        } catch (err) {
          console.error("RAG search failed:", err);
        } finally {
          if (active) {
            setSearchLoading(false);
          }
        }
      }, 300); // 300ms debounce delay
    };

    performSearch();

    return () => {
      active = false;
      if (timerId) clearTimeout(timerId);
    };
  }, [searchQuery, masterPatients]);

  const handleAddPatient = async (e) => {
    e.preventDefault();
    try {
       const config = {
         headers: { Authorization: `Bearer ${token}` }
       };

       const res = await axios.post('http://localhost:8000/api/patients/', {
         name: newName,
         age: parseInt(newAge),
         gender: newGender,
         email: newEmail
       }, config);

       setShowAddPatient(false);
       setNewName('');
       setNewAge('');
       setNewEmail('');
       
       const updatedListRes = await axios.get('http://localhost:8000/api/patients/', config);
       setPatients(updatedListRes.data);
       setMasterPatients(updatedListRes.data);
       const newlyCreated = updatedListRes.data.find(p => p.id === res.data.id) || res.data;
       setSelectedPatient(newlyCreated);
     } catch (err) {
       console.error(err);
       alert('Error creating patient profile.');
     }
    };

  const handleStartEditPatient = (patient) => {
    setEditName(patient.name);
    setEditAge(patient.age);
    setEditGender(patient.gender);
    setEditEmail(patient.email || '');
    setShowEditPatient(true);
  };

  const handleSavePatientEdit = async (e) => {
    e.preventDefault();
    setEditPatientSaving(true);
    try {
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };
      const payload = {
        name: editName,
        age: parseInt(editAge),
        gender: editGender,
        email: editEmail
      };
      const res = await axios.patch(`http://localhost:8000/api/patients/${selectedPatient.id}/`, payload, config);
      
      setShowEditPatient(false);
      await fetchDashboardData();
      
      // Update selectedPatient local state with updated fields from response
      setSelectedPatient(prev => ({ ...prev, ...res.data }));
    } catch (err) {
      console.error(err);
      alert('Error updating patient profile.');
    } finally {
      setEditPatientSaving(false);
    }
  };

  const handleDeletePatient = async () => {
    if (!window.confirm(`Are you sure you want to delete patient ${selectedPatient.name}? All their consultations will also be deleted.`)) return;
    
    setEditPatientSaving(true);
    try {
      const config = { headers: { Authorization: `Bearer ${token}` } };
      await axios.delete(`http://localhost:8000/api/patients/${selectedPatient.id}/`, config);
      setShowEditPatient(false);
      setSelectedPatient(null);
      fetchDashboardData();
    } catch (err) {
      console.error(err);
      alert('Error deleting patient.');
    } finally {
      setEditPatientSaving(false);
    }
  };

  const handleGenerateSummary = async () => {
    if (!symptoms && !diagnosis) {
      alert('Please fill out Symptoms or Diagnosis before generating summary.');
      return;
    }

    setAiLoading(true);
    try {
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      const res = await axios.post('http://localhost:8000/api/ai/summary/', {
        symptoms,
        diagnosis,
        prescription,
        notes
      }, config);

      setSummary(res.data.summary);
      setAiUsageCount(prev => prev + 1);
    } catch (err) {
      console.error(err);
      alert('Failed to generate summary via local LLM.');
    } finally {
      setAiLoading(false);
    }
  };

  const handleStartEditRecord = (record) => {
    setEditingRecord(record);
    setSymptoms(record.symptoms);
    setDiagnosis(record.diagnosis);
    setPrescription(record.prescription);
    setNotes(record.notes || '');
    setSummary(record.summary || '');
    setShowAddRecord(true);
  };

  const handleCancelRecordEdit = () => {
    setEditingRecord(null);
    setSymptoms('');
    setDiagnosis('');
    setPrescription('');
    setNotes('');
    setSummary('');
    setIsDictatingEHR(false);
    setDictationText('');
    setDictationLoading(false);
    if (window.activeEHRRecognition) {
      window.activeEHRRecognition.stop();
    }
    setShowAddRecord(false);
  };

  const handleToggleEHRDictation = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech recognition is not supported in this browser. Please try Google Chrome or Microsoft Edge.');
      return;
    }

    if (isDictatingEHR) {
      if (window.activeEHRRecognition) {
        window.activeEHRRecognition.stop();
      }
      setIsDictatingEHR(false);
      if (dictationText.trim()) {
        handleParseEHRText(dictationText);
      }
      return;
    }

    setDictationText('');
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsDictatingEHR(true);
    };

    recognition.onerror = (e) => {
      console.error(e);
      setIsDictatingEHR(false);
    };

    recognition.onend = () => {
      setIsDictatingEHR(false);
    };

    recognition.onresult = (e) => {
      let finalTranscript = '';
      for (let i = e.resultIndex; i < e.results.length; ++i) {
        if (e.results[i].isFinal) {
          finalTranscript += e.results[i][0].transcript + ' ';
        }
      }
      if (finalTranscript) {
        setDictationText(prev => prev ? prev + finalTranscript : finalTranscript);
      }
    };

    window.activeEHRRecognition = recognition;
    recognition.start();
  };

  const handleParseEHRText = async (textToParse) => {
    setDictationLoading(true);
    try {
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      const res = await axios.post('http://localhost:8000/api/ai/text-to-ehr/', {
        text: textToParse
      }, config);

      if (res.data) {
        setSymptoms(res.data.symptoms || '');
        setDiagnosis(res.data.diagnosis || '');
        setPrescription(res.data.prescription || '');
      }
    } catch (err) {
      console.error(err);
      alert('AI failed to parse the natural dictation text.');
    } finally {
      setDictationLoading(false);
    }
  };

  const handleDownloadPrescription = async (recordId) => {
    try {
      const config = {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      };
      const res = await axios.get(`http://localhost:8000/api/records/${recordId}/pdf/`, config);
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `prescription_${recordId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert('Failed to compile and download prescription PDF.');
    }
  };

  const handleEmailPrescription = async (recordId) => {
    setEmailingRecordId(recordId);
    try {
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };
      const res = await axios.post(`http://localhost:8000/api/records/${recordId}/send-email/`, {}, config);
      alert(res.data.detail || 'Prescription successfully sent to patient email.');
    } catch (err) {
      console.error(err);
      const errorMsg = err.response?.data?.detail || 'Failed to email prescription.';
      alert(errorMsg);
    } finally {
      setEmailingRecordId(null);
    }
  };

  const handleSaveRecord = async (e) => {
    e.preventDefault();
    if (!selectedPatient) return;

    setSaveLoading(true);
    try {
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      const payload = {
        patient: selectedPatient.id,
        symptoms,
        diagnosis,
        prescription,
        notes,
        summary
      };

      if (editingRecord) {
        await axios.patch(`http://localhost:8000/api/records/${editingRecord.id}/`, payload, config);
      } else {
        await axios.post('http://localhost:8000/api/records/', payload, config);
      }

      handleCancelRecordEdit();
      fetchDashboardData();
      
      const patientsRes = await axios.get('http://localhost:8000/api/patients/', config);
      const updatedPatient = patientsRes.data.find(p => p.id === selectedPatient.id);
      if (updatedPatient) {
        setSelectedPatient(updatedPatient);
      }
    } catch (err) {
      console.error(err);
      alert('Error saving medical record.');
    } finally {
      setSaveLoading(false);
    }
  };

  const handleDeleteRecord = async () => {
    if (!editingRecord) return;
    if (!window.confirm(`Are you sure you want to delete this consultation record?`)) return;
    
    setSaveLoading(true);
    try {
      const config = { headers: { Authorization: `Bearer ${token}` } };
      await axios.delete(`http://localhost:8000/api/records/${editingRecord.id}/`, config);
      handleCancelRecordEdit();
      fetchDashboardData();
      
      const patientsRes = await axios.get('http://localhost:8000/api/patients/', config);
      const updatedPatient = patientsRes.data.find(p => p.id === selectedPatient.id);
      if (updatedPatient) setSelectedPatient(updatedPatient);
    } catch (err) {
      console.error(err);
      alert('Error deleting medical record.');
    } finally {
      setSaveLoading(false);
    }
  };

  const toggleSpeechRecognition = (field) => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech recognition is not supported in this browser. Please try Google Chrome or Microsoft Edge.');
      return;
    }

    const isSymptoms = field === 'symptoms';
    const isRecording = isSymptoms ? isRecordingSymptoms : isRecordingNotes;
    
    if (isRecording) {
      if (window.activeRecognition) {
        window.activeRecognition.stop();
      }
      if (isSymptoms) setIsRecordingSymptoms(false);
      else setIsRecordingNotes(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      if (isSymptoms) setIsRecordingSymptoms(true);
      else setIsRecordingNotes(true);
    };

    recognition.onerror = (e) => {
      console.error(e);
      if (isSymptoms) setIsRecordingSymptoms(false);
      else setIsRecordingNotes(false);
    };

    recognition.onend = () => {
      if (isSymptoms) setIsRecordingSymptoms(false);
      else setIsRecordingNotes(false);
    };

    recognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript;
      if (isSymptoms) {
        setSymptoms(prev => prev ? `${prev} ${transcript}` : transcript);
      } else {
        setNotes(prev => prev ? `${prev} ${transcript}` : transcript);
      }
    };

    window.activeRecognition = recognition;
    recognition.start();
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  return (
    <div className="flex flex-col h-full">
      {/* Top Navbar */}
      <nav className="dashboard-nav">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center" style={{
            width: '2.5rem',
            height: '2.5rem',
            background: 'linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%)',
            borderRadius: '0.5rem'
          }}>
            <Activity style={{ width: '1.25rem', height: '1.25rem', color: '#fff' }} />
          </div>
          <div>
            <h1 className="font-bold text-lg text-white" style={{ fontSize: '1rem' }}>MediAssist Dashboard</h1>
            <span className="logo-sub" style={{ fontSize: '0.65rem' }}>Clinical AI Portal</span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-sm text-slate-300">
            Dr. <strong className="text-white">{localStorage.getItem('fullName')}</strong>
          </span>
          <button 
            onClick={handleLogout}
            className="btn btn-danger"
            style={{ padding: '0.45rem 1rem', fontSize: '0.75rem' }}
          >
            <LogOut style={{ width: '0.9rem', height: '0.9rem', marginRight: '0.35rem' }} />
            <span>Logout</span>
          </button>
        </div>
      </nav>

      {/* Tab Switcher */}
      <div className="dashboard-tab-bar">
        <div className="dashboard-tabs-container">
          <button
            onClick={() => setActiveTab('patients')}
            disabled={!profileCompleted}
            className={`dashboard-tab-btn ${activeTab === 'patients' ? 'active' : ''}`}
            style={{
              opacity: profileCompleted ? 1 : 0.5,
              cursor: profileCompleted ? 'pointer' : 'not-allowed'
            }}
            title={!profileCompleted ? "Please complete your profile to access clinical dashboard" : ""}
          >
            <ClipboardList style={{ width: '1.1rem', height: '1.1rem' }} />
            <span>Patients & Consultations</span>
            {!profileCompleted && <span style={{ fontSize: '0.65rem', marginLeft: '0.25rem' }}>🔒</span>}
          </button>
          <button
            onClick={() => setActiveTab('profile')}
            className={`dashboard-tab-btn ${activeTab === 'profile' ? 'active' : ''}`}
          >
            <User style={{ width: '1.1rem', height: '1.1rem' }} />
            <span>My Profile</span>
          </button>
        </div>
      </div>

      {activeTab === 'patients' ? (
        <>
          {/* Analytics Summary */}
          <div className="analytics-grid">
            <div className="glass-panel p-4 flex items-center gap-4">
              <div className="flex items-center justify-center text-indigo-400" style={{
                width: '2.5rem', height: '2.5rem', backgroundColor: 'rgba(99, 102, 241, 0.1)', border: '1px solid rgba(99, 102, 241, 0.2)', borderRadius: '0.5rem'
              }}>
                <Users style={{ width: '1.25rem', height: '1.25rem' }} />
              </div>
              <div>
                <span className="form-label" style={{ fontSize: '0.65rem' }}>Total Patients</span>
                <span className="text-xl font-bold text-white block mt-0.5">{masterPatients.length}</span>
              </div>
            </div>

            <div className="glass-panel p-4 flex items-center gap-4">
              <div className="flex items-center justify-center text-emerald-400" style={{
                width: '2.5rem', height: '2.5rem', backgroundColor: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.2)', borderRadius: '0.5rem'
              }}>
                <Sparkles style={{ width: '1.25rem', height: '1.25rem' }} />
              </div>
              <div>
                <span className="form-label" style={{ fontSize: '0.65rem' }}>AI Summaries</span>
                <span className="text-xl font-bold text-white block mt-0.5">{aiUsageCount}</span>
              </div>
            </div>

            <div className="glass-panel p-4 flex items-center gap-4">
              <div className="flex items-center justify-center text-cyan-400" style={{
                width: '2.5rem', height: '2.5rem', backgroundColor: 'rgba(6, 182, 212, 0.1)', border: '1px solid rgba(6, 182, 212, 0.2)', borderRadius: '0.5rem'
              }}>
                <Calendar style={{ width: '1.25rem', height: '1.25rem' }} />
              </div>
              <div>
                <span className="form-label" style={{ fontSize: '0.65rem' }}>Follow-up Alerts</span>
                <span className="text-xl font-bold text-white block mt-0.5">{reminders.filter(r => r.status === 'PENDING').length}</span>
              </div>
            </div>
          </div>

          {/* Main Grid Section */}
          <div className="dashboard-main-grid">
            
            {/* Left Side: Patient List */}
            <div className="dashboard-col-left">
              <div className="patient-list-card glass-panel space-y-4">
                <div className="flex justify-between items-center mb-2">
                  <h2 className="section-title flex items-center gap-2">
                    <ClipboardList style={{ width: '1rem', height: '1rem', color: 'var(--primary)' }} />
                    Patient Profiles
                  </h2>
                  <button 
                    onClick={() => setShowAddPatient(true)}
                    className="btn btn-primary"
                    style={{ padding: '0.4rem', borderRadius: '0.5rem' }}
                  >
                    <Plus style={{ width: '1rem', height: '1rem' }} />
                  </button>
                </div>

                {/* Search Panel */}
                <form onSubmit={e => e.preventDefault()} className="flex flex-col gap-2">
                  <div className="input-with-icon relative">
                    <span className="input-icon-slot">
                      <Search style={{ width: '1rem', height: '1rem' }} />
                    </span>
                    <input 
                      type="text" 
                      value={searchQuery}
                      onChange={e => setSearchQuery(e.target.value)}
                      placeholder="Search by name, symptoms, or diagnoses..."
                      className="form-control"
                      style={{ paddingRight: searchQuery ? '2.25rem' : '1rem' }}
                    />
                    {searchQuery && (
                      <button
                        type="button"
                        onClick={() => setSearchQuery('')}
                        style={{
                          position: 'absolute',
                          right: '0.75rem',
                          top: '50%',
                          transform: 'translateY(-50%)',
                          background: 'none',
                          border: 'none',
                          cursor: 'pointer',
                          color: '#94a3b8',
                          padding: '0.25rem',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          zIndex: 10
                        }}
                        className="hover:text-white transition-colors"
                        title="Clear search"
                      >
                        <span style={{ fontSize: '0.8rem', fontWeight: 'bold' }}>✕</span>
                      </button>
                    )}
                  </div>
                  <div className="flex items-center justify-between" style={{ padding: '0 0.25rem' }}>
                    <span className="text-slate-500 font-medium" style={{ fontSize: '0.65rem' }}>
                      {searchQuery.trim() ? (
                        <span className="text-indigo-400 font-semibold">
                          Found {patients.length} {patients.length === 1 ? 'match' : 'matches'}
                        </span>
                      ) : (
                        `Showing all ${patients.length} patients`
                      )}
                    </span>
                    {searchQuery.trim() && (
                      <div className="flex items-center gap-1.5 font-medium" style={{ fontSize: '0.65rem' }}>
                        {searchLoading ? (
                          <>
                            <RefreshCw className="animate-spin text-indigo-400" style={{ width: '0.75rem', height: '0.75rem' }} />
                            <span className="text-indigo-300">Searching records...</span>
                          </>
                        ) : (
                          <span className="text-slate-500 flex items-center gap-1">
                            <Sparkles style={{ width: '0.65rem', height: '0.65rem', color: 'var(--primary)' }} />
                            AI Scanned
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </form>

                {/* Patients List Body */}
                <div className="flex-1 overflow-y-auto space-y-2 pr-1 relative" style={{ minHeight: '150px' }}>
                  {searchLoading && patients.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-12 gap-2 text-center">
                      <RefreshCw className="animate-spin text-indigo-400" style={{ width: '1.25rem', height: '1.25rem' }} />
                      <span className="text-[11px] text-slate-400">Scanning clinical records...</span>
                    </div>
                  ) : loading && patients.length === 0 ? (
                    <div className="text-center text-slate-500 text-xs mt-8">Syncing profiles...</div>
                  ) : patients.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-12 text-center text-slate-500 gap-2">
                      <AlertCircle className="text-slate-500" style={{ width: '1.5rem', height: '1.5rem' }} />
                      <span className="text-xs">No matching patients found.</span>
                      <span className="text-[10px] text-slate-600 max-w-[220px]">
                        Try searching for another name, symptom, or diagnosis (e.g. fever, migraine).
                      </span>
                    </div>
                  ) : (
                    patients.map(patient => (
                      <button
                        key={patient.id}
                        onClick={() => setSelectedPatient(patient)}
                        className={`list-item-btn ${selectedPatient?.id === patient.id ? 'active' : ''}`}
                        style={{ marginBottom: '0.5rem' }}
                      >
                        <div>
                          <div className="font-semibold text-xs text-white flex items-center gap-1.5" style={{ fontSize: '0.8rem' }}>
                            {patient.name}
                            {patient.isSearchResult && (
                              <span className="badge-info" style={{ fontSize: '0.55rem', padding: '0.05rem 0.25rem' }}>
                                Relevance: {Math.round((patient.records?.find(r => r.relevanceScore !== undefined)?.relevanceScore || 1) * 100)}%
                              </span>
                            )}
                          </div>
                          <div className="text-slate-400 mt-1" style={{ fontSize: '0.65rem' }}>
                            Age: {patient.age} • Gender: {patient.gender}
                          </div>
                        </div>
                        <ChevronRight style={{ width: '0.9rem', height: '0.9rem', color: 'var(--text-muted)' }} />
                      </button>
                    ))
                  )}
                </div>
              </div>
            </div>

            {/* Right Side: Consultation logs & Form */}
            <div className="dashboard-col-right">
              
              <div className="patient-detail-card glass-panel">
                {selectedPatient ? (
                  <div className="flex flex-col h-full">
                    {/* Header detail */}
                    <div className="patient-detail-header">
                      <div className="flex items-center gap-3">
                        <div className="flex items-center justify-center text-indigo-400" style={{
                          width: '2.5rem', height: '2.5rem', backgroundColor: 'rgba(99, 102, 241, 0.1)', border: '1px solid rgba(99, 102, 241, 0.2)', borderRadius: '0.5rem'
                        }}>
                          <User style={{ width: '1.25rem', height: '1.25rem' }} />
                        </div>
                        <div>
                          <h2 className="font-bold text-white text-base leading-tight" style={{ fontSize: '1rem' }}>{selectedPatient.name}</h2>
                          <span className="text-slate-400 mt-0.5 block" style={{ fontSize: '0.7rem' }}>
                            ID: #{selectedPatient.id} • {selectedPatient.gender}, {selectedPatient.age} years old{selectedPatient.email ? ` • ${selectedPatient.email}` : ''}
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleStartEditPatient(selectedPatient)}
                          className="btn btn-secondary"
                          style={{ padding: '0.5rem 1rem', fontSize: '0.75rem', borderRadius: '0.5rem' }}
                        >
                          Edit Profile
                        </button>
                        <button
                          onClick={() => setShowAddRecord(true)}
                          className="btn btn-primary"
                          style={{ padding: '0.5rem 1rem', fontSize: '0.75rem' }}
                        >
                          <Plus style={{ width: '1rem', height: '1rem', marginRight: '0.35rem' }} />
                          <span>New Consultation</span>
                        </button>
                      </div>
                    </div>

                    {/* Patient Case Files */}
                    <div className="patient-case-files">
                      <h3 className="form-label mb-3" style={{ fontSize: '0.65rem' }}>Case History Files</h3>
                      
                      {!selectedPatient.records || selectedPatient.records.length === 0 ? (
                        <div className="text-center text-slate-500 text-xs mt-12">
                          No clinical logs on file. Click "New Consultation" to append a case.
                        </div>
                      ) : (
                        selectedPatient.records.map((record, index) => (
                          <div key={record.id || index} className="case-file-log">
                            <div className="case-file-log-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <span className="font-semibold text-indigo-400 flex items-center gap-1.5" style={{ fontSize: '0.75rem' }}>
                                <FileText style={{ width: '0.9rem', height: '0.9rem' }} />
                                Consultation Log #{record.id || 'Draft'}
                              </span>
                              <div className="flex items-center gap-2">
                                {record.id && (
                                  <>
                                    <button 
                                      onClick={() => handleDownloadPrescription(record.id)}
                                      className="btn btn-secondary flex items-center gap-1"
                                      style={{ padding: '0.15rem 0.5rem', fontSize: '0.65rem', borderRadius: '0.35rem', color: 'var(--accent)' }}
                                    >
                                      <FileText style={{ width: '0.75rem', height: '0.75rem' }} />
                                      Download PDF
                                    </button>
                                    <button 
                                      onClick={() => handleEmailPrescription(record.id)}
                                      disabled={emailingRecordId !== null}
                                      className="btn btn-secondary flex items-center gap-1"
                                      style={{ padding: '0.15rem 0.5rem', fontSize: '0.65rem', borderRadius: '0.35rem', color: 'var(--primary)' }}
                                    >
                                      {emailingRecordId === record.id ? (
                                        <>
                                          <RefreshCw className="animate-spin" style={{ width: '0.75rem', height: '0.75rem' }} />
                                          <span>Sending...</span>
                                        </>
                                      ) : (
                                        <>
                                          <Mail style={{ width: '0.75rem', height: '0.75rem' }} />
                                          <span>Email Patient</span>
                                        </>
                                      )}
                                    </button>
                                  </>
                                )}
                                <button 
                                  onClick={() => handleStartEditRecord(record)}
                                  className="btn btn-secondary"
                                  style={{ padding: '0.15rem 0.5rem', fontSize: '0.65rem', borderRadius: '0.35rem' }}
                                >
                                  Edit Log
                                </button>
                                <span>{new Date(record.created_at).toLocaleDateString()}</span>
                              </div>
                            </div>

                            <div className="grid grid-cols-2 lg-grid-cols-1 gap-4 mb-4">
                              <div>
                                <strong className="text-slate-300 block mb-1" style={{ fontSize: '0.7rem' }}>Presented Symptoms:</strong>
                                <p className="p-3 font-sans text-slate-400" style={{ backgroundColor: 'rgba(0,0,0,0.2)', border: '1px solid var(--border-light)', borderRadius: '0.5rem', fontSize: '0.75rem' }}>{record.symptoms}</p>
                              </div>
                              <div>
                                <strong className="text-slate-300 block mb-1" style={{ fontSize: '0.7rem' }}>Clinical Diagnosis:</strong>
                                <p className="p-3 font-sans text-slate-400 font-semibold" style={{ backgroundColor: 'rgba(0,0,0,0.2)', border: '1px solid var(--border-light)', borderRadius: '0.5rem', fontSize: '0.75rem' }}>{record.diagnosis}</p>
                              </div>
                            </div>

                            <div className="mb-4">
                              <strong className="text-slate-300 block mb-1" style={{ fontSize: '0.7rem' }}>Prescribed Medication & Plan:</strong>
                              <p className="p-3 font-sans text-slate-400" style={{ backgroundColor: 'rgba(0,0,0,0.2)', border: '1px solid var(--border-light)', borderRadius: '0.5rem', fontSize: '0.75rem', whiteSpace: 'pre-line' }}>{record.prescription}</p>
                            </div>

                            {record.notes && (
                              <div className="mb-4">
                                <strong className="text-slate-300 block mb-1" style={{ fontSize: '0.7rem' }}>Clinical Notes:</strong>
                                <p className="p-3 font-sans text-slate-400" style={{ backgroundColor: 'rgba(0,0,0,0.2)', border: '1px solid var(--border-light)', borderRadius: '0.5rem', fontSize: '0.75rem' }}>{record.notes}</p>
                              </div>
                            )}

                            {record.summary && (
                              <div className="consultation-summary-ai mt-2">
                                <strong className="text-indigo-400 flex items-center gap-1 mb-1 font-semibold" style={{ fontSize: '0.75rem' }}>
                                  <Sparkles style={{ width: '0.85rem', height: '0.85rem', color: 'var(--primary)' }} />
                                  AI Generated Summary & Guidance
                                </strong>
                                <p className="font-sans" style={{ fontSize: '0.75rem', lineHeight: '1.5' }}>{record.summary}</p>
                              </div>
                            )}
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-slate-500 text-xs mt-24">
                    Select a patient profile to view logs or add a new consultation.
                  </div>
                )}
              </div>
            </div>
          </div>
        </>
      ) : (
        /* Profile Tab View */
        <div className="flex-1 p-6 overflow-y-auto max-w-2xl mx-auto w-full">
          <div className="glass-panel p-6 space-y-6 mt-6">
            <div className="border-b border-slate-800 pb-4">
              <h2 className="section-title flex items-center gap-2" style={{ margin: 0 }}>
                <User style={{ width: '1.25rem', height: '1.25rem', color: 'var(--primary)' }} />
                Doctor Professional Profile
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Manage your clinical specialization, educational credentials, and daily availability hours.
              </p>
            </div>

            {!profileCompleted && (
              <div className="p-4 rounded-xl flex items-start gap-3 text-xs bg-rose-500/15 border border-rose-500/35 text-rose-300 mb-4">
                <AlertCircle style={{ width: '1.25rem', height: '1.25rem', flexShrink: 0, marginTop: '1px', color: 'var(--danger)' }} />
                <div>
                  <strong className="block font-bold mb-1">Clinical Dashboard Access Locked</strong>
                  Please complete your clinical profile details (Clinical Specialization, Education/Credentials, and Available Hours) below to unlock full clinical access and start adding patient consultation logs.
                </div>
              </div>
            )}

            {profileStatusMsg.text && (
              <div className={`p-4 rounded-lg flex items-center gap-3 text-xs ${
                profileStatusMsg.type === 'success' 
                  ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400' 
                  : 'bg-rose-500/10 border border-rose-500/20 text-rose-400'
              }`}>
                <AlertCircle style={{ width: '1.1rem', height: '1.1rem' }} />
                <span>{profileStatusMsg.text}</span>
              </div>
            )}

            <form onSubmit={handleSaveProfile} className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="form-group">
                  <label className="form-label">Doctor Name</label>
                  <input 
                    type="text" 
                    disabled 
                    value={"Dr. " + (localStorage.getItem('fullName') || '')} 
                    className="form-control"
                    style={{ opacity: 0.7, cursor: 'not-allowed', backgroundColor: 'rgba(255, 255, 255, 0.05)', color: '#fff' }}
                  />
                  <span className="text-[10px] text-slate-500 mt-1 block">Full name displayed next to the Logout button.</span>
                </div>

                <div className="form-group">
                  <label className="form-label">Email Address</label>
                  <input 
                    type="email" 
                    disabled 
                    value={profileEmail} 
                    className="form-control"
                    style={{ opacity: 0.7, cursor: 'not-allowed', backgroundColor: 'rgba(255, 255, 255, 0.05)', color: '#fff' }}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div className="form-group">
                  <label className="form-label">Username</label>
                  <input 
                    type="text" 
                    disabled 
                    value={profileUsername} 
                    className="form-control"
                    style={{ opacity: 0.7, cursor: 'not-allowed', backgroundColor: 'rgba(255, 255, 255, 0.05)', color: '#fff' }}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Clinical Specialization</label>
                  <input 
                    type="text" 
                    required 
                    value={profileSpecialization} 
                    onChange={e => setProfileSpecialization(e.target.value)}
                    placeholder="e.g. Neurologist, Dermatologist, Cardiologist" 
                    className="form-control"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div className="form-group">
                  <label className="form-label">Education / Credentials</label>
                  <input 
                    type="text" 
                    required 
                    value={profileStudy} 
                    onChange={e => setProfileStudy(e.target.value)}
                    placeholder="e.g. MBBS, MD, FRCS" 
                    className="form-control"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Approx Daily Available Hours</label>
                  <input 
                    type="text" 
                    required 
                    value={profileHours} 
                    onChange={e => setProfileHours(e.target.value)}
                    placeholder="e.g. 9 AM - 5 PM (Mon-Fri) or 4 hours daily" 
                    className="form-control"
                  />
                </div>
              </div>

              <div className="flex justify-end pt-4 border-t border-slate-800">
                <button 
                  type="submit" 
                  disabled={profileSaving}
                  className="btn btn-primary flex items-center gap-2"
                  style={{ padding: '0.6rem 2rem', fontSize: '0.8rem' }}
                >
                  {profileSaving ? (
                    <>
                      <RefreshCw className="animate-spin" style={{ width: '0.9rem', height: '0.9rem' }} />
                      <span>Saving Changes...</span>
                    </>
                  ) : (
                    <>
                      <Check style={{ width: '0.9rem', height: '0.9rem' }} />
                      <span>Save Profile Details</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Dialog Modals */}
      
      {/* 1. Add Patient Modal */}
      {showAddPatient && (
        <div className="modal-overlay">
          <div className="modal-content glass-panel" style={{ maxWidth: '380px', padding: '1.5rem' }}>
            <h3 className="font-bold text-lg text-white mb-4">Create Patient Profile</h3>
            
            <form onSubmit={handleAddPatient} className="flex flex-col gap-4">
              <div className="form-group">
                <label className="form-label">Patient Name</label>
                <input 
                  type="text" 
                  required 
                  value={newName} 
                  onChange={e => setNewName(e.target.value)}
                  placeholder="Full Name" 
                  className="form-control"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Email Address</label>
                <input 
                  type="email" 
                  value={newEmail} 
                  onChange={e => setNewEmail(e.target.value)}
                  placeholder="patient@example.com (optional)" 
                  className="form-control"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="form-group">
                  <label className="form-label">Age</label>
                  <input 
                    type="number" 
                    required 
                    value={newAge} 
                    onChange={e => setNewAge(e.target.value)}
                    placeholder="e.g. 35" 
                    className="form-control"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Gender</label>
                  <select 
                    value={newGender} 
                    onChange={e => setNewGender(e.target.value)}
                    className="form-control"
                    style={{ backgroundColor: 'var(--bg-body)' }}
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>

              <div className="flex gap-3 justify-end mt-4">
                <button 
                  type="button" 
                  onClick={() => setShowAddPatient(false)}
                  className="btn btn-secondary"
                  style={{ padding: '0.5rem 1rem', fontSize: '0.75rem' }}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  style={{ padding: '0.5rem 1rem', fontSize: '0.75rem' }}
                >
                  Save Profile
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 1.5. Edit Patient Modal */}
      {showEditPatient && selectedPatient && (
        <div className="modal-overlay">
          <div className="modal-content glass-panel" style={{ maxWidth: '380px', padding: '1.5rem' }}>
            <h3 className="font-bold text-lg text-white mb-4">Edit Patient Profile</h3>
            
            <form onSubmit={handleSavePatientEdit} className="flex flex-col gap-4">
              <div className="form-group">
                <label className="form-label">Patient Name</label>
                <input 
                  type="text" 
                  required 
                  value={editName} 
                  onChange={e => setEditName(e.target.value)}
                  placeholder="Full Name" 
                  className="form-control"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Email Address</label>
                <input 
                  type="email" 
                  value={editEmail} 
                  onChange={e => setEditEmail(e.target.value)}
                  placeholder="patient@example.com (optional)" 
                  className="form-control"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="form-group">
                  <label className="form-label">Age</label>
                  <input 
                    type="number" 
                    required 
                    value={editAge} 
                    onChange={e => setEditAge(e.target.value)}
                    placeholder="e.g. 35" 
                    className="form-control"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Gender</label>
                  <select 
                    value={editGender} 
                    onChange={e => setEditGender(e.target.value)}
                    className="form-control"
                    style={{ backgroundColor: 'var(--bg-body)' }}
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-between items-center mt-4">
                <button 
                  type="button" 
                  onClick={handleDeletePatient}
                  className="btn btn-danger"
                  style={{ padding: '0.5rem 1rem', fontSize: '0.75rem' }}
                  disabled={editPatientSaving}
                >
                  Delete Patient
                </button>
                <div className="flex gap-3">
                  <button 
                    type="button" 
                    onClick={() => setShowEditPatient(false)}
                    className="btn btn-secondary"
                    style={{ padding: '0.5rem 1rem', fontSize: '0.75rem' }}
                  >
                    Cancel
                  </button>
                  <button 
                    type="submit" 
                    disabled={editPatientSaving}
                    className="btn btn-primary"
                    style={{ padding: '0.5rem 1.5rem', fontSize: '0.75rem' }}
                  >
                    {editPatientSaving ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 2. Add Consultation / Medical Record Modal */}
      {showAddRecord && selectedPatient && (
        <div className="modal-overlay">
          <div className="modal-content glass-panel" style={{ maxWidth: '850px', padding: '2rem' }}>
            <h3 className="font-bold text-lg text-white mb-4 flex items-center gap-2" style={{ borderBottom: '1px solid var(--border-light)', paddingBottom: '0.75rem' }}>
              <FileText style={{ width: '1.25rem', height: '1.25rem', color: 'var(--primary)' }} />
              {editingRecord ? `Edit Consultation Record #${editingRecord.id}` : 'New Consultation Record'} — {selectedPatient.name}
            </h3>

            <form onSubmit={handleSaveRecord} className="flex flex-col gap-5 mt-4">
              
              {/* Voice-to-EHR Dictation Box */}
              <div className="p-4 rounded-xl" style={{ backgroundColor: 'rgba(99, 102, 241, 0.04)', border: '1px solid rgba(99, 102, 241, 0.15)', borderRadius: '0.75rem' }}>
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <Sparkles style={{ width: '1rem', height: '1rem', color: 'var(--primary)' }} />
                    <strong style={{ fontSize: '0.8rem', color: 'var(--text-primary)' }}>Natural Voice-to-EHR Structured Dictation</strong>
                  </div>
                  <button
                    type="button"
                    onClick={handleToggleEHRDictation}
                    className={`btn ${isDictatingEHR ? 'mic-btn-active' : 'btn-secondary'}`}
                    style={{ padding: '0.35rem 0.75rem', fontSize: '0.7rem', display: 'flex', alignItems: 'center', gap: '0.35rem', borderRadius: '0.5rem' }}
                  >
                    {isDictatingEHR ? <MicOff style={{ width: '0.85rem', height: '0.85rem' }} /> : <Mic style={{ width: '0.85rem', height: '0.85rem' }} />}
                    <span>{isDictatingEHR ? 'Stop & Auto-Fill EHR' : 'Start Structured Dictation'}</span>
                  </button>
                </div>
                {isDictatingEHR && (
                  <div className="mt-3 p-3 font-sans text-slate-300" style={{ backgroundColor: 'rgba(0,0,0,0.25)', border: '1px solid var(--border-light)', borderRadius: '0.5rem', fontSize: '0.75rem', minHeight: '50px' }}>
                     <div className="flex items-center gap-1.5 mb-1.5">
                       <span className="w-1.5 h-1.5 bg-rose-500 rounded-full animate-pulse" style={{ display: 'inline-block' }}></span>
                       <span className="text-[9px] text-rose-400 font-bold uppercase tracking-wider">Listening naturally... Speak symptoms, diagnosis, and prescription draft</span>
                     </div>
                     <p>{dictationText || 'Speak now (e.g., "Patient has severe headache and fever for 2 days. Diagnose viral infection, suggest paracetamol twice daily for 3 days")...'}</p>
                  </div>
                )}
                {dictationLoading && (
                  <div className="mt-3 flex items-center gap-2 text-xs text-indigo-300">
                    <RefreshCw className="animate-spin" style={{ width: '0.85rem', height: '0.85rem' }} />
                    <span>AI is structuring dictation into EHR fields...</span>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-2 lg-grid-cols-1 gap-6">
                
                {/* Left Inputs */}
                <div className="flex flex-col gap-4">
                  <div className="form-group">
                    <label className="form-label flex justify-between items-center" style={{ display: 'flex', width: '100%' }}>
                      <span>Symptoms</span>
                      <button
                        type="button"
                        onClick={() => toggleSpeechRecognition('symptoms')}
                        className={`btn btn-secondary ${isRecordingSymptoms ? 'mic-btn-active' : ''}`}
                        style={{ padding: '0.2rem 0.5rem', fontSize: '0.65rem', display: 'flex', alignItems: 'center', gap: '0.25rem', borderRadius: '0.35rem' }}
                      >
                        {isRecordingSymptoms ? <MicOff style={{ width: '0.75rem', height: '0.75rem' }} /> : <Mic style={{ width: '0.75rem', height: '0.75rem' }} />}
                        <span>{isRecordingSymptoms ? "Stop Mic" : "Speak Info"}</span>
                      </button>
                    </label>
                    <textarea 
                      required 
                      rows={3}
                      value={symptoms} 
                      onChange={e => setSymptoms(e.target.value)}
                      placeholder="Enter patient symptoms (or click voice dictation)..." 
                      className="form-control"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Clinical Diagnosis</label>
                    <input 
                      type="text" 
                      required 
                      value={diagnosis} 
                      onChange={e => setDiagnosis(e.target.value)}
                      placeholder="e.g. Acute Viral Fever / Migraine" 
                      className="form-control"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Prescription (Dosage & Instructions)</label>
                    <textarea 
                      required 
                      rows={3}
                      value={prescription} 
                      onChange={e => setPrescription(e.target.value)}
                      placeholder="Paracetamol 650mg - 1 tablet 3x daily..." 
                      className="form-control"
                    />
                  </div>
                </div>

                {/* Right Inputs */}
                <div className="flex flex-col gap-4">
                  <div className="form-group">
                    <label className="form-label flex justify-between items-center" style={{ display: 'flex', width: '100%' }}>
                      <span>Additional Clinical Notes (Optional)</span>
                      <button
                        type="button"
                        onClick={() => toggleSpeechRecognition('notes')}
                        className={`btn btn-secondary ${isRecordingNotes ? 'mic-btn-active' : ''}`}
                        style={{ padding: '0.2rem 0.5rem', fontSize: '0.65rem', display: 'flex', alignItems: 'center', gap: '0.25rem', borderRadius: '0.35rem' }}
                      >
                        {isRecordingNotes ? <MicOff style={{ width: '0.75rem', height: '0.75rem' }} /> : <Mic style={{ width: '0.75rem', height: '0.75rem' }} />}
                        <span>{isRecordingNotes ? "Stop Mic" : "Speak Info"}</span>
                      </button>
                    </label>
                    <textarea 
                      rows={2}
                      value={notes} 
                      onChange={e => setNotes(e.target.value)}
                      placeholder="Pre-existing conditions, allergies, precautions..." 
                      className="form-control"
                    />
                  </div>

                  <div className="form-group flex-1 flex flex-col justify-end" style={{ minHeight: '140px' }}>
                    <div className="flex justify-between items-center mb-1">
                      <label className="form-label flex items-center gap-1">
                        <Sparkles style={{ width: '0.85rem', height: '0.85rem', color: 'var(--primary)' }} />
                        AI Summary Generator
                      </label>
                      <button
                        type="button"
                        onClick={handleGenerateSummary}
                        disabled={aiLoading || (!symptoms && !diagnosis)}
                        className="btn btn-secondary flex items-center gap-1.5"
                        style={{ padding: '0.35rem 0.65rem', fontSize: '0.65rem', border: '1px solid rgba(99, 102, 241, 0.25)', color: 'var(--primary)' }}
                      >
                        {aiLoading ? (
                          <>
                            <RefreshCw className="animate-spin" style={{ width: '0.75rem', height: '0.75rem' }} />
                            <span>Thinking...</span>
                          </>
                        ) : (
                          <>
                            <Sparkles style={{ width: '0.75rem', height: '0.75rem' }} />
                            <span>Generate AI Summary</span>
                          </>
                        )}
                      </button>
                    </div>

                    <textarea 
                      rows={3}
                      value={summary}
                      onChange={e => setSummary(e.target.value)}
                      placeholder="Summary and follow-up guidance will be generated by AI here..." 
                      className="form-control"
                      style={{
                        backgroundColor: 'rgba(99, 102, 241, 0.03)',
                        borderColor: 'rgba(99, 102, 241, 0.15)',
                        color: '#c7d2fe'
                      }}
                    />
                  </div>
                </div>

              </div>

              <div className="flex justify-between items-center mt-4" style={{ borderTop: '1px solid var(--border-light)', paddingTop: '1.25rem' }}>
                {editingRecord ? (
                  <button 
                    type="button" 
                    onClick={handleDeleteRecord}
                    className="btn btn-danger"
                    style={{ padding: '0.5rem 1.25rem', fontSize: '0.75rem' }}
                    disabled={saveLoading}
                  >
                    Delete Record
                  </button>
                ) : (
                  <div></div>
                )}
                <div className="flex gap-3">
                  <button 
                    type="button" 
                    onClick={handleCancelRecordEdit}
                    className="btn btn-secondary"
                    style={{ padding: '0.5rem 1.25rem', fontSize: '0.75rem' }}
                  >
                    Cancel
                  </button>
                  <button 
                    type="submit" 
                    disabled={saveLoading}
                    className="btn btn-primary flex items-center gap-2"
                    style={{ padding: '0.5rem 1.5rem', fontSize: '0.75rem' }}
                  >
                    {saveLoading ? (
                      <span className="animate-spin" style={{
                        display: 'inline-block',
                        width: '1rem',
                        height: '1rem',
                        border: '2px solid rgba(255,255,255,0.3)',
                        borderTopColor: '#fff',
                        borderRadius: '50%'
                      }}></span>
                    ) : (
                      <>
                        <Check style={{ width: '1rem', height: '1rem' }} />
                        <span>Save Record</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};

export default DoctorDashboard;
