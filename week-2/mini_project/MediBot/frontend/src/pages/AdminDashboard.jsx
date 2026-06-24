import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  Users, UserPlus, LogOut, MessageSquare, Clipboard, AlertCircle, CheckCircle, 
  ShieldAlert, Clock, Calendar
} from 'lucide-react';

const AdminDashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [chatLogs, setChatLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Registration Form State
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [regLoading, setRegLoading] = useState(false);
  const [regError, setRegError] = useState('');

  // Appointments & Scheduling State
  const [appointments, setAppointments] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [selectedAppt, setSelectedAppt] = useState(null);
  const [showApptsModal, setShowApptsModal] = useState(false);
  const [schedDate, setSchedDate] = useState('');
  const [schedDay, setSchedDay] = useState('');
  const [schedTime, setSchedTime] = useState('');
  const [schedDoctorId, setSchedDoctorId] = useState('');
  const [schedSaving, setSchedSaving] = useState(false);
  const [schedSuccessMsg, setSchedSuccessMsg] = useState('');
  const [schedError, setSchedError] = useState('');

  // Edit Doctor State
  const [showEditDoctorModal, setShowEditDoctorModal] = useState(false);
  const [editingDoctor, setEditingDoctor] = useState(null);
  const [editDocData, setEditDocData] = useState({ specialization: '', study: '', available_hours: '', email: '' });
  const [editDocSaving, setEditDocSaving] = useState(false);
  const [editDocError, setEditDocError] = useState('');
  const [editDocSuccess, setEditDocSuccess] = useState('');

  const navigate = useNavigate();
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');

  useEffect(() => {
    // Check permission
    if (!token || role !== 'ADMIN') {
      navigate('/login');
      return;
    }
    
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError('');
    try {
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      const [analyticsRes, chatLogsRes, apptsRes, doctorsRes] = await Promise.all([
        axios.get('http://localhost:8000/api/admin/analytics/', config),
        axios.get('http://localhost:8000/api/chatbot/history/', config),
        axios.get('http://localhost:8000/api/appointments/', config),
        axios.get('http://localhost:8000/api/auth/doctors/', config)
      ]);

      setAnalytics(analyticsRes.data);
      setChatLogs(chatLogsRes.data);
      setAppointments(apptsRes.data);
      setDoctors(doctorsRes.data);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch dashboard data. Please make sure the backend is active.');
    } finally {
      setLoading(false);
    }
  };

  const handleDateChange = (val) => {
    setSchedDate(val);
    if (val) {
      const parts = val.split('-');
      if (parts.length === 3) {
        const year = parseInt(parts[0], 10);
        const month = parseInt(parts[1], 10) - 1;
        const day = parseInt(parts[2], 10);
        const localDate = new Date(year, month, day);
        const dayName = localDate.toLocaleDateString('en-US', { weekday: 'long' });
        setSchedDay(dayName);
      }
    } else {
      setSchedDay('');
    }
  };

  const handleSelectAppointment = (appt) => {
    setSelectedAppt(appt);
    setSchedDate(appt.scheduled_date || '');
    setSchedDay(appt.scheduled_day || '');
    setSchedTime(appt.scheduled_time || '');
    
    // Determine doctors list for this doctor_type
    const filteredDocs = doctors.filter(doc => 
      doc.specialization && 
      doc.specialization.toLowerCase() === appt.doctor_type.toLowerCase()
    );
    const fallbackDocs = filteredDocs.length > 0 ? filteredDocs : doctors;
    
    // Set initial doctor ID
    if (appt.assigned_doctor) {
      setSchedDoctorId(appt.assigned_doctor);
    } else if (fallbackDocs.length > 0) {
      setSchedDoctorId(fallbackDocs[0].id);
    } else {
      setSchedDoctorId('');
    }
    
    setSchedSuccessMsg('');
    setSchedError('');
  };

  const handleConfirmSchedule = async (e) => {
    e.preventDefault();
    if (!selectedAppt) return;
    if (!schedDate || !schedDay || !schedTime || !schedDoctorId) {
      setSchedError('Please fill out all scheduling fields.');
      return;
    }

    setSchedSaving(true);
    setSchedError('');
    setSchedSuccessMsg('');

    try {
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      await axios.patch(
        `http://localhost:8000/api/appointments/${selectedAppt.id}/`, 
        {
          scheduled_date: schedDate,
          scheduled_day: schedDay,
          scheduled_time: schedTime,
          assigned_doctor: parseInt(schedDoctorId, 10),
          status: 'CONFIRMED'
        },
        config
      );

      setSchedSuccessMsg('Appointment successfully scheduled and confirmed! Email confirmation sent.');
      fetchDashboardData();
      
      setTimeout(() => {
        setSelectedAppt(null);
        setSchedSuccessMsg('');
      }, 3000);
      
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data) {
        setSchedError(JSON.stringify(err.response.data));
      } else {
        setSchedError('Failed to confirm appointment scheduling.');
      }
    } finally {
      setSchedSaving(false);
    }
  };

  const handleRegisterDoctor = async (e) => {
    e.preventDefault();
    setRegError('');
    setSuccessMsg('');
    setRegLoading(true);

    try {
      await axios.post('http://localhost:8000/api/auth/register/', {
        username,
        email,
        password,
        role: 'DOCTOR',
        first_name: firstName,
        last_name: lastName
      });

      setSuccessMsg(`Doctor @${username} registered successfully.`);
      // Reset form
      setUsername('');
      setEmail('');
      setPassword('');
      setFirstName('');
      setLastName('');
      
      fetchDashboardData();
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data) {
        const errors = err.response.data;
        if (typeof errors === 'object') {
          const firstKey = Object.keys(errors)[0];
          setRegError(`${firstKey}: ${errors[firstKey][0]}`);
        } else {
          setRegError('Registration failed.');
        }
      } else {
        setRegError('Failed to contact server.');
      }
    } finally {
      setRegLoading(false);
    }
  };

  const handleEditDoctorClick = (doc) => {
    setEditingDoctor(doc);
    setEditDocData({
      specialization: doc.specialization || '',
      study: doc.study || '',
      available_hours: doc.available_hours || '',
      email: doc.email || ''
    });
    setEditDocError('');
    setEditDocSuccess('');
    setShowEditDoctorModal(true);
  };

  const handleSaveDoctorProfile = async (e) => {
    e.preventDefault();
    setEditDocSaving(true);
    setEditDocError('');
    setEditDocSuccess('');

    try {
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      await axios.patch(
        `http://localhost:8000/api/auth/doctors/${editingDoctor.id}/`, 
        editDocData,
        config
      );

      setEditDocSuccess('Doctor profile updated successfully!');
      fetchDashboardData();
      
      setTimeout(() => {
        setShowEditDoctorModal(false);
        setEditingDoctor(null);
        setEditDocSuccess('');
      }, 2000);
      
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data) {
        setEditDocError(JSON.stringify(err.response.data));
      } else {
        setEditDocError('Failed to update doctor profile.');
      }
    } finally {
      setEditDocSaving(false);
    }
  };

  const handleDeleteDoctor = async () => {
    if (!window.confirm(`Are you sure you want to delete ${editingDoctor.first_name ? `Dr. ${editingDoctor.first_name} ${editingDoctor.last_name}` : editingDoctor.username}? This cannot be undone.`)) {
      return;
    }
    
    setEditDocSaving(true);
    setEditDocError('');

    try {
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      await axios.delete(
        `http://localhost:8000/api/auth/doctors/${editingDoctor.id}/`, 
        config
      );

      fetchDashboardData();
      setShowEditDoctorModal(false);
      setEditingDoctor(null);
      
    } catch (err) {
      console.error(err);
      setEditDocError('Failed to delete doctor. They may be linked to existing records.');
    } finally {
      setEditDocSaving(false);
    }
  };

  const handleClearChatLogs = async () => {
    if (!window.confirm("Are you sure you want to clear all patient chat history logs? This action cannot be undone.")) {
      return;
    }

    try {
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      await axios.delete('http://localhost:8000/api/chatbot/history/', config);
      setChatLogs([]);
      fetchDashboardData();
    } catch (err) {
      console.error(err);
      alert("Failed to clear chat logs.");
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  if (loading && !analytics) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <div className="text-center space-y-4" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
          <span className="animate-spin" style={{
            display: 'inline-block',
            width: '3rem',
            height: '3rem',
            border: '4px solid rgba(99,102,241,0.2)',
            borderTopColor: 'var(--primary)',
            borderRadius: '50%'
          }}></span>
          <p className="text-slate-400 text-sm">Loading Administration Console...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen" style={{ paddingBottom: '3rem' }}>
      
      {/* Top Navbar */}
      <nav className="dashboard-nav">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center text-white" style={{
            width: '2.5rem',
            height: '2.5rem',
            background: 'linear-gradient(135deg, var(--primary) 0%, var(--danger) 100%)',
            borderRadius: '0.5rem'
          }}>
            <ShieldAlert style={{ width: '1.25rem', height: '1.25rem' }} />
          </div>
          <div>
            <h1 className="font-bold text-lg text-white" style={{ fontSize: '1rem' }}>MediAssist Admin</h1>
            <span className="logo-sub" style={{ fontSize: '0.65rem' }}>System Control Center</span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-sm text-slate-300">
            Welcome, <strong className="text-white">{localStorage.getItem('fullName')}</strong>
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

      {/* Statistics Grid */}
      <div className="admin-analytics-grid">
        <div className="glass-panel p-5 flex items-center gap-4">
          <div className="flex items-center justify-center text-indigo-400" style={{
            width: '2.75rem', height: '2.75rem', backgroundColor: 'rgba(99, 102, 241, 0.1)', border: '1px solid rgba(99, 102, 241, 0.2)', borderRadius: '0.5rem'
          }}>
            <Users style={{ width: '1.5rem', height: '1.5rem' }} />
          </div>
          <div>
            <span className="form-label" style={{ fontSize: '0.65rem' }}>Total Doctors</span>
            <h3 className="text-2xl font-bold text-white block mt-0.5">{analytics?.total_doctors || 0}</h3>
          </div>
        </div>

        <div className="glass-panel p-5 flex items-center gap-4">
          <div className="flex items-center justify-center text-emerald-400" style={{
            width: '2.75rem', height: '2.75rem', backgroundColor: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.2)', borderRadius: '0.5rem'
          }}>
            <Users style={{ width: '1.5rem', height: '1.5rem' }} />
          </div>
          <div>
            <span className="form-label" style={{ fontSize: '0.65rem' }}>Total Patients</span>
            <h3 className="text-2xl font-bold text-white block mt-0.5">{analytics?.total_patients || 0}</h3>
          </div>
        </div>

        <div className="glass-panel p-5 flex items-center gap-4">
          <div className="flex items-center justify-center text-cyan-400" style={{
            width: '2.75rem', height: '2.75rem', backgroundColor: 'rgba(6, 182, 212, 0.1)', border: '1px solid rgba(6, 182, 212, 0.2)', borderRadius: '0.5rem'
          }}>
            <Clipboard style={{ width: '1.5rem', height: '1.5rem' }} />
          </div>
          <div>
            <span className="form-label" style={{ fontSize: '0.65rem' }}>Medical Records</span>
            <h3 className="text-2xl font-bold text-white block mt-0.5">{analytics?.total_records || 0}</h3>
          </div>
        </div>

        <div className="glass-panel p-5 flex items-center gap-4">
          <div className="flex items-center justify-center text-purple-400" style={{
            width: '2.75rem', height: '2.75rem', backgroundColor: 'rgba(168, 85, 247, 0.1)', border: '1px solid rgba(168, 85, 247, 0.2)', borderRadius: '0.5rem'
          }}>
            <MessageSquare style={{ width: '1.5rem', height: '1.5rem' }} />
          </div>
          <div>
            <span className="form-label" style={{ fontSize: '0.65rem' }}>Chatbot Queries</span>
            <h3 className="text-2xl font-bold text-white block mt-0.5">{analytics?.total_chats || 0}</h3>
          </div>
        </div>
      </div>

      {/* Appointment Booking Management Banner */}
      {(() => {
        const pendingCount = appointments.filter(app => app.status === 'PENDING').length;
        return (
          <div className="px-6 mb-6" style={{ width: '100%' }}>
            <div className="glass-panel p-5 flex items-center justify-between gap-4" style={{
              background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(9, 13, 22, 0.6) 100%)',
              borderLeft: '4px solid var(--primary)',
            }}>
              <div className="flex items-center gap-4">
                <div className="flex items-center justify-center text-indigo-400" style={{
                  width: '3rem', height: '3rem', backgroundColor: 'rgba(99, 102, 241, 0.15)', border: '1px solid rgba(99, 102, 241, 0.3)', borderRadius: '50%'
                }}>
                  <Calendar style={{ width: '1.5rem', height: '1.5rem' }} />
                </div>
                <div>
                  <h2 className="font-bold text-white text-lg leading-tight" style={{ fontSize: '1.1rem' }}>Patient Appointment Manager</h2>
                  <p className="text-slate-400 text-xs mt-1">
                    {pendingCount > 0 
                      ? `There are currently ${pendingCount} pending appointment requests waiting to be scheduled.`
                      : 'All appointments have been successfully scheduled and confirmed.'
                    }
                  </p>
                </div>
              </div>
              <button 
                onClick={() => setShowApptsModal(true)} 
                className={`btn ${pendingCount > 0 ? 'btn-primary' : 'btn-secondary'} flex items-center gap-2`}
                style={{ padding: '0.65rem 1.25rem' }}
              >
                <span>Manage Appointments</span>
                {pendingCount > 0 && (
                  <span className="badge-danger" style={{ 
                    padding: '0.15rem 0.45rem', 
                    borderRadius: '9999px', 
                    fontSize: '0.65rem',
                    backgroundColor: 'var(--danger)',
                    color: '#fff',
                    fontWeight: 'bold'
                  }}>
                    {pendingCount}
                  </span>
                )}
              </button>
            </div>
          </div>
        );
      })()}

      {/* Main Grid Panels */}
      <div className="dashboard-main-grid">
        
        {/* Register Doctor */}
        <div className="dashboard-col-left">
          <div className="glass-panel p-6">
            <h2 className="section-title flex items-center gap-2 mb-6">
              <UserPlus style={{ width: '1.15rem', height: '1.15rem', color: 'var(--primary)' }} />
              Register New Doctor
            </h2>

            {regError && (
              <div className="alert-box alert-danger mb-4" style={{ padding: '0.75rem', borderRadius: '0.5rem' }}>
                <AlertCircle style={{ width: '1.1rem', height: '1.1rem', flexShrink: 0 }} />
                <span style={{ fontSize: '0.75rem' }}>{regError}</span>
              </div>
            )}

            {successMsg && (
              <div className="alert-box alert-success mb-4" style={{ padding: '0.75rem', borderRadius: '0.5rem' }}>
                <CheckCircle style={{ width: '1.1rem', height: '1.1rem', flexShrink: 0 }} />
                <span style={{ fontSize: '0.75rem' }}>{successMsg}</span>
              </div>
            )}

            <form onSubmit={handleRegisterDoctor} className="flex flex-col gap-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="form-group">
                  <label className="form-label" style={{ fontSize: '0.6rem' }}>First Name</label>
                  <input 
                    type="text" 
                    required 
                    value={firstName} 
                    onChange={e => setFirstName(e.target.value)}
                    placeholder="John" 
                    className="form-control"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label" style={{ fontSize: '0.6rem' }}>Last Name</label>
                  <input 
                    type="text" 
                    required 
                    value={lastName} 
                    onChange={e => setLastName(e.target.value)}
                    placeholder="Doe" 
                    className="form-control"
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label" style={{ fontSize: '0.6rem' }}>Username</label>
                <input 
                  type="text" 
                  required 
                  value={username} 
                  onChange={e => setUsername(e.target.value)}
                  placeholder="doctor_name" 
                  className="form-control"
                />
              </div>

              <div className="form-group">
                <label className="form-label" style={{ fontSize: '0.6rem' }}>Email Address</label>
                <input 
                  type="email" 
                  required 
                  value={email} 
                  onChange={e => setEmail(e.target.value)}
                  placeholder="dr.john@mediassist.com" 
                  className="form-control"
                />
              </div>

              <div className="form-group">
                <label className="form-label" style={{ fontSize: '0.6rem' }}>Access Password</label>
                <input 
                  type="password" 
                  required 
                  value={password} 
                  onChange={e => setPassword(e.target.value)}
                  placeholder="••••••••" 
                  className="form-control"
                />
              </div>

              <button 
                type="submit" 
                disabled={regLoading}
                className="btn btn-primary w-full mt-2"
                style={{ padding: '0.7rem' }}
              >
                {regLoading ? (
                  <span className="animate-spin" style={{
                    display: 'inline-block',
                    width: '1.15rem',
                    height: '1.15rem',
                    border: '2px solid rgba(255,255,255,0.3)',
                    borderTopColor: '#fff',
                    borderRadius: '50%'
                  }}></span>
                ) : (
                  <div className="flex items-center justify-center gap-2">
                    <UserPlus style={{ width: '1.1rem', height: '1.1rem' }} />
                    <span>Register Account</span>
                  </div>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Chat Logs */}
        <div className="dashboard-col-right">
          <div className="glass-panel p-6 flex flex-col" style={{ height: '550px' }}>
            <div className="flex justify-between items-center mb-6">
              <h2 className="section-title flex items-center gap-2">
                <MessageSquare style={{ width: '1.15rem', height: '1.15rem', color: 'var(--primary)' }} />
                Patient Chat History Logs
              </h2>
              <div className="flex items-center gap-3">
                {chatLogs.length > 0 && (
                  <button 
                    onClick={handleClearChatLogs}
                    className="btn btn-danger"
                    style={{ padding: '0.25rem 0.75rem', fontSize: '0.7rem', minHeight: 'auto' }}
                  >
                    Clear Logs
                  </button>
                )}
                <span className="badge-info" style={{ padding: '0.25rem 0.65rem' }}>Live Feed</span>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto space-y-4 pr-1">
              {chatLogs.length === 0 ? (
                <div className="text-center text-slate-500 text-sm mt-24">
                  No patient chat conversations recorded yet.
                </div>
              ) : (
                chatLogs.map(log => (
                  <div key={log.id} className="case-file-log" style={{ padding: '1rem', marginBottom: '0.75rem' }}>
                    <div className="case-file-log-header" style={{ marginBottom: '0.5rem' }}>
                      <span className="font-semibold text-indigo-400">Query Log #{log.id}</span>
                      <span>{new Date(log.timestamp).toLocaleString()}</span>
                    </div>
                    <div style={{ marginBottom: '0.5rem' }}>
                      <strong className="text-indigo-300 font-medium" style={{ fontSize: '0.65rem' }}>Patient Ask:</strong>
                      <p className="p-2 font-mono text-slate-400 mt-1" style={{ backgroundColor: 'rgba(0,0,0,0.25)', border: '1px solid var(--border-light)', borderRadius: '0.35rem', fontSize: '0.7rem' }}>{log.message}</p>
                    </div>
                    <div>
                      <strong className="text-emerald-400 font-medium" style={{ fontSize: '0.65rem' }}>MediAssist AI Answer:</strong>
                      <p className="p-2 font-mono text-slate-400 mt-1" style={{ backgroundColor: 'rgba(0,0,0,0.25)', border: '1px solid var(--border-light)', borderRadius: '0.35rem', fontSize: '0.7rem', whiteSpace: 'pre-line' }}>{log.response}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

      </div>

      {/* Registered Doctors Directory */}
      <div className="px-6 mt-6 mb-6" style={{ width: '100%' }}>
        <div className="glass-panel p-6">
          <h2 className="section-title flex items-center gap-2 mb-6">
            <Users style={{ width: '1.25rem', height: '1.25rem', color: 'var(--primary)' }} />
            Registered Doctors Directory
          </h2>

          {doctors.length === 0 ? (
            <div className="text-center text-slate-500 text-sm py-8">
              No doctors registered in the system yet.
            </div>
          ) : (
            <div className="grid gap-6" style={{ 
              gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))'
            }}>
              {doctors.map(doc => {
                const docName = `Dr. ${doc.first_name} ${doc.last_name}`.trim() || `Dr. ${doc.username}`;
                return (
                  <div key={doc.id} className="glass-card-interactive p-5 flex flex-col justify-between" style={{
                    background: 'rgba(9, 13, 22, 0.4)',
                    border: '1px solid var(--border-light)'
                  }}>
                    <div>
                      <div className="flex items-center gap-3 mb-4">
                        <div className="flex items-center justify-center font-bold text-white text-sm" style={{
                          width: '2.5rem',
                          height: '2.5rem',
                          background: 'linear-gradient(135deg, var(--primary) 0%, #a5b4fc 100%)',
                          borderRadius: '50%'
                        }}>
                          {doc.first_name ? doc.first_name[0].toUpperCase() : doc.username[0].toUpperCase()}
                        </div>
                        <div className="text-left">
                          <h3 className="font-bold text-white text-sm leading-tight">{docName}</h3>
                          <span className="text-slate-400 text-xs">{doc.email}</span>
                        </div>
                      </div>

                      <div className="space-y-2 text-xs pt-3" style={{ 
                        borderTop: '1px solid var(--border-light)',
                        marginTop: '0.75rem' 
                      }}>
                        <div className="flex justify-between">
                          <span className="text-slate-500">Specialization:</span>
                          <span className="text-indigo-300 font-medium">{doc.specialization || 'Not Set'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-500">Credentials:</span>
                          <span className="text-white font-medium">{doc.study || 'Not Set'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-500">Availability:</span>
                          <span className="text-emerald-400 font-medium">{doc.available_hours || 'Not Set'}</span>
                        </div>
                      </div>
                      
                      <button 
                        onClick={() => handleEditDoctorClick(doc)}
                        className="btn btn-secondary mt-4 w-full"
                        style={{ padding: '0.4rem', fontSize: '0.75rem' }}
                      >
                        Edit Profile
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Appointment Scheduling Modal */}
      {showApptsModal && (
        <div className="modal-overlay" style={{ zIndex: 100 }}>
          <div className="modal-content glass-panel" style={{ 
            maxWidth: '900px', 
            width: '90%', 
            padding: '2rem', 
            maxHeight: '85vh',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="font-bold text-xl text-white flex items-center gap-2">
                  <Calendar style={{ width: '1.5rem', height: '1.5rem', color: 'var(--primary)' }} />
                  Appointment Booking Dashboard
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  Manage patient-submitted appointment requests, assign doctors, and set times.
                </p>
              </div>
              <button 
                onClick={() => {
                  setShowApptsModal(false);
                  setSelectedAppt(null);
                }} 
                className="btn btn-secondary btn-icon-only"
                style={{ borderRadius: '50%', width: '2rem', height: '2rem', minWidth: 'auto', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
              >
                ✕
              </button>
            </div>

            <div className="flex-1 grid gap-6 overflow-hidden" style={{ 
              gridTemplateColumns: '1.2fr 1.8fr', 
              minHeight: 0 
            }}>
              
              {/* Left Column: Appointments List */}
              <div className="flex flex-col gap-4 overflow-y-auto pr-2" style={{ borderRight: '1px solid var(--border-light)', minHeight: 0 }}>
                <h3 className="text-sm font-semibold text-slate-300 mb-2">Request Inbox</h3>
                {appointments.length === 0 ? (
                  <div className="text-center text-slate-500 text-xs py-8">
                    No appointment requests logged yet.
                  </div>
                ) : (
                  appointments.map(appt => {
                    const isSelected = selectedAppt?.id === appt.id;
                    const isPending = appt.status === 'PENDING';
                    const isConfirmed = appt.status === 'CONFIRMED';
                    
                    return (
                      <div 
                        key={appt.id}
                        onClick={() => handleSelectAppointment(appt)}
                        className="glass-card-interactive p-4 cursor-pointer"
                        style={{
                          border: isSelected ? '1px solid var(--primary)' : '1px solid var(--border-light)',
                          background: isSelected ? 'rgba(99, 102, 241, 0.1)' : 'rgba(9, 13, 22, 0.4)',
                          marginBottom: '0.5rem'
                        }}
                      >
                        <div className="flex justify-between items-start gap-2 mb-2">
                          <span className="font-semibold text-sm text-white">{appt.patient_name}</span>
                          <span className="text-xs" style={{
                            padding: '0.15rem 0.5rem',
                            borderRadius: '0.25rem',
                            fontSize: '0.65rem',
                            fontWeight: '600',
                            backgroundColor: isPending ? 'rgba(244, 63, 94, 0.15)' : isConfirmed ? 'rgba(16, 185, 129, 0.15)' : 'rgba(255, 255, 255, 0.1)',
                            color: isPending ? 'var(--danger)' : isConfirmed ? 'var(--accent)' : 'var(--text-secondary)',
                            border: `1px solid ${isPending ? 'rgba(244, 63, 94, 0.3)' : isConfirmed ? 'rgba(16, 185, 129, 0.3)' : 'var(--border-light)'}`
                          }}>
                            {appt.status}
                          </span>
                        </div>
                        <div className="flex flex-col gap-1 text-xs text-slate-400 text-left">
                          <div><span className="text-slate-500">Dept:</span> {appt.doctor_type}</div>
                          <div><span className="text-slate-500">Phone:</span> {appt.patient_phone}</div>
                          <div><span className="text-slate-500">Received:</span> {new Date(appt.created_at).toLocaleDateString()}</div>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>

              {/* Right Column: Scheduler Form or Detail Panel */}
              <div className="flex flex-col overflow-y-auto pl-2 pr-2" style={{ minHeight: 0 }}>
                {!selectedAppt ? (
                  <div className="flex-1 flex flex-col items-center justify-center text-center text-slate-500 py-12">
                    <Calendar style={{ width: '3rem', height: '3rem', color: 'var(--text-muted)', marginBottom: '1rem', opacity: 0.5 }} />
                    <p className="text-sm">Select an appointment from the list to view details and schedule.</p>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {/* Patient Request Details Card */}
                    <div className="glass-panel p-4" style={{ backgroundColor: 'rgba(0,0,0,0.2)' }}>
                      <h4 className="text-xs uppercase font-bold text-indigo-400 mb-3 tracking-wider text-left">Patient Request Details</h4>
                      <div className="grid grid-cols-2 gap-4 text-sm mb-3">
                        <div className="text-left">
                          <div className="text-slate-500 text-xs">Patient Name</div>
                          <div className="text-white font-medium mt-0.5">{selectedAppt.patient_name}</div>
                        </div>
                        <div className="text-left">
                          <div className="text-slate-500 text-xs">Requested Specialty</div>
                          <div className="text-white font-medium mt-0.5">{selectedAppt.doctor_type}</div>
                        </div>
                        <div className="text-left">
                          <div className="text-slate-500 text-xs">Email Address</div>
                          <div className="text-white font-medium mt-0.5">{selectedAppt.patient_email}</div>
                        </div>
                        <div className="text-left">
                          <div className="text-slate-500 text-xs">Phone Number</div>
                          <div className="text-white font-medium mt-0.5">{selectedAppt.patient_phone}</div>
                        </div>
                      </div>
                      {selectedAppt.notes && (
                        <div className="text-left">
                          <div className="text-slate-500 text-xs">Patient's Preferred Date/Time & Notes</div>
                          <div className="p-2 font-mono text-slate-300 mt-1" style={{ backgroundColor: 'rgba(0,0,0,0.3)', borderRadius: '0.35rem', fontSize: '0.75rem', border: '1px solid var(--border-light)' }}>
                            {selectedAppt.notes}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Scheduler form */}
                    {selectedAppt.status === 'PENDING' ? (
                      <form onSubmit={handleConfirmSchedule} className="space-y-4 text-left">
                        <h4 className="text-xs uppercase font-bold text-emerald-400 tracking-wider">Schedule Appointment</h4>
                        
                        {schedError && (
                          <div className="alert-box alert-danger text-xs p-3 rounded-lg">
                            <AlertCircle style={{ width: '1rem', height: '1rem' }} />
                            <span>{schedError}</span>
                          </div>
                        )}

                        {schedSuccessMsg && (
                          <div className="alert-box alert-success text-xs p-3 rounded-lg">
                            <CheckCircle style={{ width: '1rem', height: '1rem' }} />
                            <span>{schedSuccessMsg}</span>
                          </div>
                        )}

                        <div className="grid grid-cols-2 gap-4">
                          <div className="form-group">
                            <label className="form-label" style={{ fontSize: '0.65rem' }}>Appointment Date</label>
                            <input 
                              type="date" 
                              required
                              value={schedDate}
                              onChange={e => handleDateChange(e.target.value)}
                              className="form-control"
                            />
                          </div>
                          <div className="form-group">
                            <label className="form-label" style={{ fontSize: '0.65rem' }}>Day of the Week</label>
                            <input 
                              type="text" 
                              required
                              value={schedDay}
                              onChange={e => setSchedDay(e.target.value)}
                              placeholder="e.g. Thursday"
                              className="form-control"
                            />
                          </div>
                        </div>

                        <div className="form-group">
                          <label className="form-label" style={{ fontSize: '0.65rem' }}>Time Slot</label>
                          <input 
                            type="text" 
                            required
                            value={schedTime}
                            onChange={e => setSchedTime(e.target.value)}
                            placeholder="e.g. 10:30 AM"
                            className="form-control"
                          />
                        </div>

                        <div className="form-group text-left">
                          <div className="flex justify-between items-center">
                            <label className="form-label" style={{ fontSize: '0.65rem' }}>Assign Doctor Specialist</label>
                            
                            {/* Doctor Filtering Feedback */}
                            {(() => {
                              const matchingCount = doctors.filter(doc => 
                                doc.specialization && 
                                doc.specialization.toLowerCase() === selectedAppt.doctor_type.toLowerCase()
                              ).length;
                              
                              if (matchingCount > 0) {
                                return (
                                  <span className="text-emerald-400 text-xs font-semibold" style={{ fontSize: '0.65rem' }}>
                                    ✓ Found {matchingCount} specialist(s)
                                  </span>
                                );
                              } else {
                                return (
                                  <span className="text-amber-400 text-xs font-semibold" style={{ fontSize: '0.65rem' }}>
                                    ⚠ No specialists found. Showing all doctors.
                                  </span>
                                );
                              }
                            })()}
                          </div>
                          
                          <select
                            required
                            value={schedDoctorId}
                            onChange={e => setSchedDoctorId(e.target.value)}
                            className="form-control"
                            style={{ backgroundColor: 'var(--bg-body)' }}
                          >
                            <option value="">-- Select Doctor --</option>
                            {(() => {
                              const filtered = doctors.filter(doc => 
                                doc.specialization && 
                                doc.specialization.toLowerCase() === selectedAppt.doctor_type.toLowerCase()
                              );
                              const listToRender = filtered.length > 0 ? filtered : doctors;
                              
                              return listToRender.map(doc => {
                                const docName = `Dr. ${doc.first_name} ${doc.last_name}`.trim() || `Dr. ${doc.username}`;
                                const spec = doc.specialization ? ` (${doc.specialization})` : '';
                                return (
                                  <option key={doc.id} value={doc.id}>
                                    {docName}{spec}
                                  </option>
                                );
                              });
                            })()}
                          </select>
                        </div>

                        <button 
                          type="submit"
                          disabled={schedSaving}
                          className="btn btn-primary w-full mt-4 flex items-center justify-center gap-2"
                        >
                          {schedSaving ? (
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
                              <CheckCircle style={{ width: '1.1rem', height: '1.1rem' }} />
                              <span>Confirm Schedule & Notify Patient</span>
                            </>
                          )}
                        </button>
                      </form>
                    ) : (
                      /* Scheduled Read-only view for CONFIRMED/CANCELLED */
                      <div className="space-y-4 text-left">
                        <h4 className="text-xs uppercase font-bold text-indigo-400 tracking-wider">Scheduled Information</h4>
                        <div className="glass-panel p-4 space-y-3" style={{ borderLeft: '4px solid var(--accent)' }}>
                          <div className="flex justify-between">
                            <span className="text-slate-500 text-xs">Status:</span>
                            <span className="text-accent text-xs font-bold uppercase">{selectedAppt.status}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-500 text-xs">Date:</span>
                            <span className="text-white text-xs font-semibold">{selectedAppt.scheduled_date}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-500 text-xs">Day:</span>
                            <span className="text-white text-xs font-semibold">{selectedAppt.scheduled_day}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-500 text-xs">Time:</span>
                            <span className="text-white text-xs font-semibold">{selectedAppt.scheduled_time}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-500 text-xs">Assigned Doctor:</span>
                            <span className="text-white text-xs font-semibold">{selectedAppt.assigned_doctor_name || 'Specialist'}</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

            </div>
          </div>
        </div>
      )}

      {/* Edit Doctor Modal */}
      {showEditDoctorModal && editingDoctor && (
        <div className="modal-overlay" style={{ zIndex: 100 }}>
          <div className="modal-content glass-panel" style={{ 
            maxWidth: '550px', 
            width: '90%', 
            padding: '2.5rem',
            background: 'linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(9, 13, 22, 0.95) 100%)',
            boxShadow: '0 25px 50px -12px rgba(0,0,0,1)'
          }}>
            <div className="flex justify-between items-center mb-6" style={{ borderBottom: '1px solid var(--border-light)', paddingBottom: '1.5rem' }}>
              <div>
                <h2 className="font-bold text-xl text-white flex items-center gap-2">
                  <UserPlus style={{ width: '1.5rem', height: '1.5rem', color: 'var(--primary)' }} />
                  Edit Doctor Profile
                </h2>
                <p className="text-xs text-slate-400 mt-1">Update directory details for {editingDoctor.first_name ? `Dr. ${editingDoctor.first_name} ${editingDoctor.last_name}` : editingDoctor.username}</p>
              </div>
              <button 
                onClick={() => {
                  setShowEditDoctorModal(false);
                  setEditingDoctor(null);
                }} 
                className="btn btn-secondary btn-icon-only"
                style={{ borderRadius: '50%', width: '2.25rem', height: '2.25rem', minWidth: 'auto', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
              >
                ✕
              </button>
            </div>
            
            {editDocError && <div className="alert-box alert-danger mb-4"><AlertCircle size={18} /> {editDocError}</div>}
            {editDocSuccess && <div className="alert-box alert-success mb-4"><CheckCircle size={18} /> {editDocSuccess}</div>}

            <form onSubmit={handleSaveDoctorProfile} className="space-y-5">
              <div className="form-group">
                <label className="form-label">Email Address</label>
                <input 
                  type="email"
                  className="form-control"
                  value={editDocData.email}
                  onChange={(e) => setEditDocData({...editDocData, email: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Specialization</label>
                <input 
                  type="text"
                  className="form-control"
                  value={editDocData.specialization}
                  onChange={(e) => setEditDocData({...editDocData, specialization: e.target.value})}
                  placeholder="e.g. Cardiology"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="form-group">
                  <label className="form-label">Credentials / Study</label>
                  <input 
                    type="text"
                    className="form-control"
                    value={editDocData.study}
                    onChange={(e) => setEditDocData({...editDocData, study: e.target.value})}
                    placeholder="e.g. MBBS, MD"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Availability</label>
                  <input 
                    type="text"
                    className="form-control"
                    value={editDocData.available_hours}
                    onChange={(e) => setEditDocData({...editDocData, available_hours: e.target.value})}
                    placeholder="e.g. Mon-Fri 9AM-5PM"
                  />
                </div>
              </div>

              <div className="flex justify-between items-center pt-6 mt-2" style={{ borderTop: '1px solid var(--border-light)' }}>
                <button 
                  type="button" 
                  onClick={handleDeleteDoctor}
                  className="btn btn-danger flex items-center gap-2"
                  disabled={editDocSaving}
                >
                  Delete Profile
                </button>
                <div className="flex gap-3">
                  <button 
                    type="button" 
                    onClick={() => setShowEditDoctorModal(false)}
                    className="btn btn-secondary"
                    disabled={editDocSaving}
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary flex items-center gap-2" disabled={editDocSaving}>
                    {editDocSaving ? (
                      <>
                        <span className="animate-spin" style={{
                          display: 'inline-block', width: '1rem', height: '1rem',
                          border: '2px solid rgba(255,255,255,0.3)', borderTopColor: '#fff', borderRadius: '50%'
                        }}></span>
                        Saving...
                      </>
                    ) : (
                      <>Save Changes</>
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

export default AdminDashboard;
