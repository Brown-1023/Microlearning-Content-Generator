import React, { useState } from 'react';

interface LoginModalProps {
  onLogin: (password: string) => Promise<boolean>;
}

const LoginModal: React.FC<LoginModalProps> = ({ onLogin }) => {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    
    const success = await onLogin(password);
    
    if (!success) {
      setError('Invalid password');
    }
    
    setIsLoading(false);
  };

  return (
    <div className="modal">
      <div className="modal-content">
        <div className="modal-header">
          <h2>🔐 Secure Login</h2>
          <p>Enter your credentials to access the content generator</p>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Enter your password"
              disabled={isLoading}
            />
          </div>
          
          <button type="submit" className="btn btn-primary" disabled={isLoading}>
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
          
          {error && (
            <div className="error-message">{error}</div>
          )}
        </form>
      </div>
    </div>
  );
};

export default LoginModal;
