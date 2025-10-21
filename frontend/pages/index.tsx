import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import LoginModal from '../components/LoginModal';
import GeneratorForm from '../components/GeneratorForm';
import OutputPanel from '../components/OutputPanel';
import Toast from '../components/Toast';
import { authService, UserRole } from '../services/auth';
import { generationService } from '../services/generation';

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRole, setUserRole] = useState<UserRole>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [output, setOutput] = useState<any>(null);
  const [toast, setToast] = useState({ show: false, message: '', type: 'info' });

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const { authenticated, role } = await authService.checkAuth();
    setIsAuthenticated(authenticated);
    setUserRole(role);
  };

  const handleLogin = async (password: string) => {
    const { success, role } = await authService.login(password);
    if (success) {
      setIsAuthenticated(true);
      setUserRole(role);
      showToast(`Successfully logged in as ${role}`, 'success');
    } else {
      showToast('Invalid password', 'error');
    }
    return success;
  };

  const handleLogout = async () => {
    await authService.logout();
    setIsAuthenticated(false);
    setUserRole(null);
    setOutput(null);
    showToast('Logged out successfully', 'info');
  };

  const handleGenerate = async (params: any) => {
    setIsLoading(true);
    setOutput(null);
    
    try {
      const result = await generationService.generateContent(params);
      setOutput(result);
      
      if (result.success) {
        showToast('Content generated successfully!', 'success');
      } else if (result.validation_errors?.length > 0) {
        showToast('Generation completed with validation errors', 'warning');
      } else {
        showToast(result.error || 'Generation failed', 'error');
      }
    } catch (error) {
      showToast('Network error. Please try again.', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const showToast = (message: string, type: string = 'info') => {
    setToast({ show: true, message, type });
    setTimeout(() => setToast({ show: false, message: '', type: 'info' }), 3000);
  };

  return (
    <>
      <Head>
        <title>Revi</title>
        <meta name="description" content="Generate educational content with AI" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      {!isAuthenticated ? (
        <LoginModal onLogin={handleLogin} />
      ) : (
        <div className="app">
          <header className="header">
            <div className="container">
              <div className="header-content">
                <div className="logo">
                  <h1>📚 ReviewBytes Internal Content Generator</h1>
                  <p className="subtitle">Transform educational content into interactive questions</p>
                </div>
                <div className="header-actions">
                  {userRole && (
                    <span className="user-role">
                      {userRole === 'admin' ? '👑' : '✍️'} {userRole.charAt(0).toUpperCase() + userRole.slice(1)}
                    </span>
                  )}
                  <button onClick={handleLogout} className="btn btn-outline">
                    Logout
                  </button>
                </div>
              </div>
            </div>
          </header>

          <main className="main">
            <div className="container">
              <GeneratorForm 
                onGenerate={handleGenerate} 
                isLoading={isLoading}
                userRole={userRole}
              />
              
              {output && (
                <OutputPanel 
                  output={output}
                  onShowToast={showToast}
                />
              )}
            </div>
          </main>

          <footer className="footer">
            <div className="container">
              <p>© 2025 Internal Tool | Version 1.0.0</p>
            </div>
          </footer>
        </div>
      )}

      {toast.show && (
        <Toast message={toast.message} type={toast.type} />
      )}
    </>
  );
}
