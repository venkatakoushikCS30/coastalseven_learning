import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Bot, User, Clock, AlertTriangle, ArrowLeft, PhoneCall } from 'lucide-react';
import { Link } from 'react-router-dom';

const PatientChat = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'bot',
      text: 'Hello! I am MediAssist AI, your digital healthcare assistant. How can I help you today? You can ask me about hospital hours, bookings, or describe your general symptoms.',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  // Booking Modal States
  const [showBookingModal, setShowBookingModal] = useState(false);
  const [bookingName, setBookingName] = useState('');
  const [bookingEmail, setBookingEmail] = useState('');
  const [bookingPhone, setBookingPhone] = useState('');
  const [bookingDept, setBookingDept] = useState('General Medicine');
  const [bookingNotes, setBookingNotes] = useState('');
  const [bookingSaving, setBookingSaving] = useState(false);


  const quickPrompts = [
    "What are the hospital hours?",
    "How can I book an appointment?",
    "What departments do you have?",
    "I have a severe headache and fever",
    "Precautions for sore throat"
  ];

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);


  const handleSendMessage = async (textToSend) => {
    const text = textToSend || inputText;
    if (!text.trim()) return;

    if (!textToSend) setInputText('');

    const newUserMessage = {
      id: Date.now(),
      sender: 'user',
      text: text,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, newUserMessage]);
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/chatbot/', {
        message: text
      });

      const newBotMessage = {
        id: Date.now() + 1,
        sender: 'bot',
        text: response.data.response,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => [...prev, newBotMessage]);

      if (response.data.show_appointment_form) {
        setTimeout(() => {
          setShowBookingModal(true);
        }, 1000);
      }
    } catch (err) {
      console.error(err);
      const errorBotMessage = {
        id: Date.now() + 1,
        sender: 'bot',
        text: "I'm having trouble connecting to the medical service. Please check back shortly. If you are experiencing a medical emergency, please dial 911.",
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorBotMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleBookingSubmit = async (e) => {
    e.preventDefault();
    setBookingSaving(true);
    try {
      await axios.post('http://localhost:8000/api/appointments/request/', {
        patient_name: bookingName,
        patient_email: bookingEmail,
        patient_phone: bookingPhone,
        doctor_type: bookingDept,
        notes: bookingNotes
      });

      setShowBookingModal(false);

      const successBotMsg = {
        id: Date.now() + 2,
        sender: 'bot',
        text: `Thank you, ${bookingName}. Your request for an appointment with a ${bookingDept} specialist has been logged. Our administrative team will schedule the time slot and email your confirmation letter to ${bookingEmail} shortly.`,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setBookingName('');
      setBookingEmail('');
      setBookingPhone('');
      setBookingNotes('');

      setMessages(prev => [...prev, successBotMsg]);
    } catch (err) {
      console.error(err);
      alert('Failed to submit appointment request. Please try again.');
    } finally {
      setBookingSaving(false);
    }
  };

  return (
    <div className="chat-page-container">
      {/* Hospital Info Sidebar */}
      <div className="chat-sidebar glass-panel">
        <div>
          <div className="flex items-center gap-2 mb-6">
            <span className="text-xs uppercase font-semibold tracking-wider text-indigo-400">MediAssist AI Platform</span>
          </div>

          <div className="flex items-center gap-3 mb-8">
            <div className="flex items-center justify-center" style={{
              width: '3rem',
              height: '3rem',
              background: 'linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%)',
              borderRadius: '0.75rem',
              boxShadow: '0 4px 15px rgba(99, 102, 241, 0.2)'
            }}>
              <Bot style={{ width: '1.5rem', height: '1.5rem', color: '#fff' }} />
            </div>
            <div>
              <h2 className="font-bold text-lg text-white leading-tight" style={{ fontSize: '1.1rem' }}>MediAssist AI</h2>
              <span className="text-xs text-emerald-400 flex items-center gap-1.5 font-medium">
                <span style={{
                  width: '0.4rem',
                  height: '0.4rem',
                  backgroundColor: 'var(--accent)',
                  borderRadius: '50%',
                  display: 'inline-block'
                }}></span>
                Virtual Assistant Online
              </span>
            </div>
          </div>

          <div className="flex flex-col gap-4">
            <div className="p-4 rounded-xl" style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-light)', borderRadius: '0.75rem' }}>
              <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2 mb-2">
                <Clock style={{ width: '1rem', height: '1rem', color: 'var(--primary)' }} />
                Clinic Hours
              </h3>
              <p className="text-xs text-slate-400" style={{ lineHeight: '1.6' }}>
                Mon - Fri: 8:00 AM - 8:00 PM<br />
                Saturday: 9:00 AM - 5:00 PM<br />
                Sunday: Closed<br />
                <span className="text-indigo-300 font-medium">(ER open 24/7)</span>
              </p>
            </div>

            <div className="p-4 rounded-xl" style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-light)', borderRadius: '0.75rem' }}>
              <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2 mb-2">
                <PhoneCall style={{ width: '1rem', height: '1rem', color: 'var(--primary)' }} />
                Contact Info
              </h3>
              <p className="text-xs text-slate-400" style={{ lineHeight: '1.6' }}>
                Emergency: <a href="tel:+15559113000" className="text-rose-400 font-medium" style={{ textDecoration: 'underline' }}>+1 (555) 911-3000</a><br />
                General: <a href="tel:+15551002000" className="text-indigo-300" style={{ textDecoration: 'underline' }}>+1 (555) 100-2000</a>
              </p>
            </div>
          </div>
        </div>

        <div className="alert-box alert-danger mt-6">
          <AlertTriangle style={{ width: '1.25rem', height: '1.25rem', flexShrink: 0 }} />
          <p className="text-xs" style={{ lineHeight: '1.5' }}>
            <strong>Disclaimer:</strong> AI responses are for general information only. If you have severe symptoms, call emergency services immediately or visit the nearest ER.
          </p>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="chat-main-area">
        {/* Top Header */}
        <div className="chat-header glass-panel">
          <h1 className="text-lg font-bold text-white flex items-center gap-2">
            <Bot style={{ width: '1.25rem', height: '1.25rem', color: 'var(--primary)' }} />
            Patient Guidance Assistant
          </h1>
          <Link to="/portal" className="btn btn-secondary" style={{ padding: '0.5rem 1rem', fontSize: '0.8rem' }}>
            Doctor Portal
          </Link>
        </div>

        {/* Chat Feed */}
        <div className="chat-feed-scroll">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`chat-wrapper ${msg.sender === 'user' ? 'chat-user' : ''}`}
            >
              <div className={`chat-avatar ${msg.sender === 'user' ? 'chat-avatar-user' : 'chat-avatar-bot'}`}>
                {msg.sender === 'user' ? <User style={{ width: '1.1rem', height: '1.1rem' }} /> : <Bot style={{ width: '1.1rem', height: '1.1rem' }} />}
              </div>
              <div className="flex flex-col">
                <div className={`chat-bubble ${msg.sender === 'user' ? 'chat-bubble-user' : 'chat-bubble-bot'}`}>
                  {msg.text}
                </div>
                <div className="chat-timestamp">
                  {msg.time}
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="chat-wrapper">
              <div className="chat-avatar chat-avatar-bot">
                <Bot style={{ width: '1.1rem', height: '1.1rem' }} />
              </div>
              <div className="chat-bubble chat-bubble-bot flex items-center gap-1" style={{ padding: '0.85rem 1.25rem' }}>
                <span className="animate-spin" style={{
                  display: 'inline-block',
                  width: '0.75rem',
                  height: '0.75rem',
                  border: '2px solid rgba(255,255,255,0.2)',
                  borderTopColor: 'var(--accent)',
                  borderRadius: '50%'
                }}></span>
                <span className="text-slate-400 text-xs">AI is searching RAG knowledge base...</span>
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Quick Prompts */}
        <div className="quick-prompts-bar">
          <span className="text-slate-500 font-bold uppercase tracking-wider" style={{ fontSize: '0.65rem' }}>Suggested:</span>
          {quickPrompts.map((prompt, index) => (
            <button
              key={index}
              disabled={loading}
              onClick={() => handleSendMessage(prompt)}
              className="tag-pill"
            >
              {prompt}
            </button>
          ))}
        </div>

        {/* Chat Input */}
        <div className="chat-footer">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="chat-input-row"
          >
            <input
              type="text"
              disabled={loading}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Ask me a health question (e.g. precautions for fever)..."
              className="form-control flex-1"
              style={{ padding: '0.85rem 1.15rem' }}
            />
            <button
              type="submit"
              disabled={loading || !inputText.trim()}
              className="btn btn-primary"
              style={{ padding: '0.85rem 1.25rem' }}
            >
              <Send style={{ width: '1.15rem', height: '1.15rem' }} />
            </button>
          </form>
        </div>
      </div>

      {/* Appointment Booking Modal */}
      {showBookingModal && (
        <div className="modal-overlay">
          <div className="modal-content glass-panel" style={{ maxWidth: '420px', padding: '2.25rem' }}>
            <h2 className="font-bold text-lg text-white mb-2 flex items-center gap-2">
              <Clock style={{ width: '1.25rem', height: '1.25rem', color: 'var(--primary)' }} />
              Request Appointment
            </h2>
            <p className="text-xs text-slate-400 mb-6">
              Fill in your details to submit an appointment request. Our admin team will schedule you with a specialist.
            </p>

            <form onSubmit={handleBookingSubmit} className="flex flex-col gap-4">
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <input 
                  type="text" 
                  required 
                  value={bookingName}
                  onChange={e => setBookingName(e.target.value)}
                  placeholder="Patient Name" 
                  className="form-control"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Email Address</label>
                <input 
                  type="email" 
                  required 
                  value={bookingEmail}
                  onChange={e => setBookingEmail(e.target.value)}
                  placeholder="name@example.com" 
                  className="form-control"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Phone Number</label>
                <input 
                  type="tel" 
                  required 
                  value={bookingPhone}
                  onChange={e => setBookingPhone(e.target.value)}
                  placeholder="e.g. +1 (555) 000-0000" 
                  className="form-control"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Select Department / Specialty</label>
                <select 
                  value={bookingDept}
                  onChange={e => setBookingDept(e.target.value)}
                  className="form-control"
                  style={{ backgroundColor: 'var(--bg-body)' }}
                >
                  <option value="General Medicine">General Medicine</option>
                  <option value="Neurology">Neurology</option>
                  <option value="Dermatologist">Dermatology</option>
                  <option value="Gynacologist">Gynaecology</option>
                  <option value="Cardiology">Cardiology</option>
                  <option value="Pediatrics">Pediatrics</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Notes (Optional)</label>
                <textarea 
                  rows={2}
                  value={bookingNotes}
                  onChange={e => setBookingNotes(e.target.value)}
                  placeholder="e.g. Reason for consultation, symptom history, or general notes..." 
                  className="form-control"
                />
              </div>

              <div className="flex gap-3 justify-end mt-4">
                <button 
                  type="button" 
                  onClick={() => setShowBookingModal(false)}
                  className="btn btn-secondary"
                  style={{ padding: '0.5rem 1rem', fontSize: '0.75rem' }}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  disabled={bookingSaving}
                  className="btn btn-primary flex items-center gap-2"
                  style={{ padding: '0.5rem 1.5rem', fontSize: '0.75rem' }}
                >
                  {bookingSaving ? 'Submitting...' : 'Submit Request'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default PatientChat;
