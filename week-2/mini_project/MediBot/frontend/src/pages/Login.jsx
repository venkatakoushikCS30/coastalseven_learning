import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { Shield, Key, User, Activity, AlertCircle } from 'lucide-react';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/auth/login/', {
        username,
        password,
      });

      const { access, refresh, id, role, email, first_name, last_name } = response.data;

      // Store in localStorage
      localStorage.setItem('token', access);
      localStorage.setItem('refresh', refresh);
      localStorage.setItem('userId', id);
      localStorage.setItem('username', username);
      localStorage.setItem('role', role);
      localStorage.setItem('fullName', `${first_name} ${last_name}`.trim() || username);

      // Redirect based on role
      if (role === 'ADMIN') {
        navigate('/admin');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data) {
        setError(err.response.data.detail || 'Invalid username or password.');
      } else {
        setError('Unable to connect to the backend server. Please verify Django is running.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      {/* Decorative Background Elements */}
      <div className="decorative-blob-1"></div>
      <div className="decorative-blob-2"></div>

      <div className="login-card glass-panel">
        {/* App Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="flex items-center justify-center p-3 mb-2" style={{
            background: 'linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%)',
            borderRadius: '1rem',
            boxShadow: '0 4px 15px rgba(99, 102, 241, 0.2)'
          }}>
            <Activity className="animate-spin" style={{ width: '2.25rem', height: '2.25rem', color: '#fff' }} />
          </div>
          <h1 className="logo-title">
            MediAssist AI
          </h1>
          <p className="logo-sub">Smart Healthcare Portal</p>
        </div>

        {error && (
          <div className="alert-box alert-danger mb-6">
            <AlertCircle style={{ width: '1.25rem', height: '1.25rem', flexShrink: 0 }} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="flex flex-col gap-4">
          <div className="form-group">
            <label className="form-label">
              Username
            </label>
            <div className="input-with-icon">
              <span className="input-icon-slot">
                <User style={{ width: '1.25rem', height: '1.25rem' }} />
              </span>
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="e.g. doctor1"
                className="form-control"
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">
              Password
            </label>
            <div className="input-with-icon">
              <span className="input-icon-slot">
                <Key style={{ width: '1.25rem', height: '1.25rem' }} />
              </span>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="form-control"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary w-full mt-4"
            style={{ padding: '0.85rem' }}
          >
            {loading ? (
              <span className="animate-spin" style={{
                display: 'inline-block',
                width: '1.25rem',
                height: '1.25rem',
                border: '2px solid rgba(255,255,255,0.3)',
                borderTopColor: '#fff',
                borderRadius: '50%'
              }}></span>
            ) : (
              <div className="flex items-center justify-center gap-2">
                <Shield style={{ width: '1.25rem', height: '1.25rem' }} />
                <span>Access Dashboard</span>
              </div>
            )}
          </button>
        </form>

        <div className="text-center mt-6" style={{ borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '1.5rem' }}>
          <p className="text-slate-400 text-sm">
            Are you a patient?{' '}
            <Link
              to="/"
              className="text-indigo-400 font-semibold"
              style={{ textDecoration: 'underline', textUnderlineOffset: '4px' }}
            >
              Consult Patient AI Chatbot
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
