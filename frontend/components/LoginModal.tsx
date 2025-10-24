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
          <p>
          Hi Ranjan,

I&apos;m writing to let you know that my Upwork account has suddenly been suspended, and I&apos;m not sure why yet.

Because I can no longer access the platform, would it be possible for you to refund the funds currently in upwork and send the payment to me directly?

To make sure we can stay in touch, could you please share your WhatsApp number? My email is snowflake30518@gmail.com.

Please contact me at this email so we can coordinate.

Thanks,

          </p>
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
