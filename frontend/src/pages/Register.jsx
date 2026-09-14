import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Register = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const success = await register(username, email, password);
    setLoading(false);
    if (success) navigate('/login');
  };

  return (
    <div className=\"min-h-screen flex items-center justify-center bg-primary-cream px-4\">
      <div className=\"max-w-md w-full bg-white rounded-2xl shadow-xl p-8\">
        <div className=\"text-center mb-8\">
          <div className=\"text-4xl mb-3\">💰</div>
          <h1 className=\"font-serif text-3xl font-bold text-primary-green\">Sensible</h1>
          <p className=\"text-gray-500 mt-1\">Create your account</p>
        </div>
        <form onSubmit={handleSubmit}>
          <div className=\"space-y-4\">
            <div>
              <label className=\"block text-sm font-medium text-gray-700 mb-1\">Username</label>
              <input type=\"text\" value={username} onChange={(e) => setUsername(e.target.value)} className=\"w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-green focus:border-transparent\" placeholder=\"Choose a username\" required />
            </div>
            <div>
              <label className=\"block text-sm font-medium text-gray-700 mb-1\">Email</label>
              <input type=\"email\" value={email} onChange={(e) => setEmail(e.target.value)} className=\"w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-green focus:border-transparent\" placeholder=\"Enter your email\" required />
            </div>
            <div>
              <label className=\"block text-sm font-medium text-gray-700 mb-1\">Password</label>
              <input type=\"password\" value={password} onChange={(e) => setPassword(e.target.value)} className=\"w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-green focus:border-transparent\" placeholder=\"Min 8 characters\" minLength={8} required />
            </div>
            <button type=\"submit\" disabled={loading} className=\"w-full bg-primary-green text-white py-3 rounded-lg font-semibold hover:bg-primary-greenLight transition-colors disabled:opacity-50\">
              {loading ? 'Creating account...' : 'Register'}
            </button>
          </div>
        </form>
        <p className=\"text-center mt-6 text-gray-600\">
          Already have an account? <Link to=\"/login\" className=\"text-primary-green font-semibold hover:underline\">Login</Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
