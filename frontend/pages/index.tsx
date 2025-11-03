import React, { useState, useEffect, useRef } from 'react';
import Head from 'next/head';
import LoginModal from '../components/LoginModal';
import GeneratorForm from '../components/GeneratorForm';
import OutputPanel from '../components/OutputPanel';
import StreamingOutputPanel from '../components/StreamingOutputPanel';
import Toast from '../components/Toast';
import ModelRestrictionsPanel from '../components/ModelRestrictions';
import { authService, UserRole } from '../services/auth';
import { generationService, StreamProgress } from '../services/generation';

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRole, setUserRole] = useState<UserRole>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [output, setOutput] = useState<any>(null);
  const [toast, setToast] = useState({ show: false, message: '', type: 'info' });
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamProgress, setStreamProgress] = useState<StreamProgress | null>(null);
  const [streamDraft, setStreamDraft] = useState<string | null>(null);
  const [useStreaming, setUseStreaming] = useState(true); // Default to streaming mode
  const [isReformatting, setIsReformatting] = useState(false);
  const [lastGenerationParams, setLastGenerationParams] = useState<any>(null);
  const [originalInputText, setOriginalInputText] = useState<string>('');  // Store original input
  const [streamingDraft, setStreamingDraft] = useState<string>(''); // For token streaming
  const [streamingFormatted, setStreamingFormatted] = useState<string>(''); // For token streaming
  const streamingFormattedRef = useRef<string>(''); // Ref to access latest value in callbacks

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
    setStreamProgress(null);
    setStreamDraft(null);
    setStreamingDraft(''); // Reset streaming draft
    setStreamingFormatted(''); // Reset streaming formatted
    streamingFormattedRef.current = ''; // Reset ref
    setLastGenerationParams(params); // Store params for potential reformat
    setOriginalInputText(params.input_text || ''); // Store original input text
    
    try {
      if (useStreaming) {
        // Use streaming mode
        setIsStreaming(true);
        
        await generationService.generateContentStream(params, {
          onProgress: (data: StreamProgress) => {
            setStreamProgress(data);
          },
          onDraft: (draft: string) => {
            setStreamDraft(draft);
          },
          onDraftToken: (token: string) => {
            setStreamingDraft(prev => prev + token);
          },
          onFormattedToken: (token: string) => {
            setStreamingFormatted(prev => {
              const newContent = prev + token;
              streamingFormattedRef.current = newContent; // Update ref
              return newContent;
            });
            // Don't clear draft immediately
          },
          onComplete: (result: any) => {
            // If content was streamed, use the accumulated streamingFormatted as output
            if (result.streamed && streamingFormattedRef.current) {
              setOutput({
                ...result,
                output: streamingFormattedRef.current,
                partial_output: streamingFormattedRef.current
              });
            } else {
              // Fallback for non-streaming or if output is provided
              setOutput(result);
            }
            setIsStreaming(false);
            
            if (result.success) {
              showToast('Content generated successfully!', 'success');
            } else if (result.validation_errors?.length > 0) {
              showToast('Generation completed with validation errors', 'warning');
            } else {
              showToast(result.error || 'Generation failed', 'error');
            }
          },
          onError: (error: string) => {
            setIsStreaming(false);
            showToast(error, 'error');
          }
        });
      } else {
        // Use traditional non-streaming mode
        const result = await generationService.generateContent(params);
        setOutput(result);
        
        if (result.success) {
          showToast('Content generated successfully!', 'success');
        } else if (result.validation_errors?.length > 0) {
          showToast('Generation completed with validation errors', 'warning');
        } else {
          showToast(result.error || 'Generation failed', 'error');
        }
      }
    } catch (error) {
      setIsStreaming(false);
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
        <title>ReviewBytes</title>
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
              <ModelRestrictionsPanel userRole={userRole} />
              
              {/* Streaming Mode Toggle */}
              <div className="streaming-toggle">
                <label className="toggle-label">
                  <input
                    type="checkbox"
                    checked={useStreaming}
                    onChange={(e) => setUseStreaming(e.target.checked)}
                    disabled={isLoading}
                  />
                  <span className="toggle-text">
                    {useStreaming ? '🚀 Streaming Mode (Real-time Progress)' : '📦 Traditional Mode'}
                  </span>
                </label>
                <span className="toggle-description">
                  {useStreaming 
                    ? 'Shows real-time progress as content is generated'
                    : 'Waits for complete response before showing results'}
                </span>
              </div>
              
              <GeneratorForm 
                onGenerate={handleGenerate} 
                isLoading={isLoading}
                userRole={userRole}
              />
              
              {/* Show streaming panel if streaming, otherwise show regular panel */}
              {(isStreaming || streamProgress || streamDraft || output || streamingDraft || streamingFormatted) && (
                <StreamingOutputPanel
                  progress={streamProgress}
                  draft={streamDraft}
                  output={output}
                  isStreaming={isStreaming}
                  onShowToast={showToast}
                  streamingDraft={streamingDraft}
                  streamingFormatted={streamingFormatted}
                  onReformat={async () => {
                    if (!output || (!output.output && !output.partial_output && !streamDraft)) {
                      showToast('No content available to reformat', 'error');
                      return;
                    }
                    
                    setIsReformatting(true);
                    setStreamingFormatted(''); // Clear previous formatted content
                    streamingFormattedRef.current = ''; // Clear ref too
                    
                    try {
                      // Use the draft or output for reformatting
                      const contentToReformat = streamDraft || output.output || output.partial_output;
                      
                      const reformatParams = {
                        draft_1: contentToReformat,
                        input_text: originalInputText,  // Include original input text
                        content_type: lastGenerationParams?.content_type || output?.metadata?.content_type || 'MCQ',
                        generator_model: lastGenerationParams?.generator_model || output?.metadata?.generator_model || 'claude-sonnet-3.5',
                        num_questions: lastGenerationParams?.num_questions || output?.metadata?.num_questions || 1,
                        focus_areas: lastGenerationParams?.focus_areas,  // Include focus areas
                        // Use lower temperature for reformatting (more consistent)
                        formatter_temperature: 0.3,  // Lower than default
                        formatter_top_p: 0.9  // Slightly lower for consistency
                      };
                      
                      // Use streaming for reformatting
                      await generationService.reformatContentStream(reformatParams, {
                        onProgress: (data: StreamProgress) => {
                          setStreamProgress(data);
                        },
                        onFormattedToken: (token: string) => {
                          setStreamingFormatted(prev => {
                            const newContent = prev + token;
                            streamingFormattedRef.current = newContent; // Update ref
                            return newContent;
                          });
                        },
                        onComplete: (result: any) => {
                          // If content was streamed, use the accumulated streamingFormatted as output
                          if (result.streamed && streamingFormattedRef.current) {
                            setOutput({
                              ...result,
                              output: streamingFormattedRef.current,
                              partial_output: streamingFormattedRef.current
                            });
                          } else {
                            // Fallback for non-streaming or if output is provided
                            setOutput(result);
                          }
                          setIsReformatting(false);
                          // Don't clear immediately - keep for display
                          
                          if (result.success) {
                            showToast('Content reformatted successfully!', 'success');
                          } else if (result.validation_errors?.length > 0) {
                            showToast(`Reformatting completed with ${result.validation_errors.length} validation errors. Try again or adjust prompts.`, 'warning');
                          } else {
                            showToast(result.error || 'Reformatting failed. Consider adjusting formatter prompts.', 'error');
                          }
                        },
                        onError: (error: string) => {
                          setIsReformatting(false);
                          setStreamingFormatted(''); // Clear streaming content on error
                          showToast(error || 'Failed to reformat content', 'error');
                        }
                      });
                    } catch (error) {
                      setIsReformatting(false);
                      setStreamingFormatted(''); // Clear streaming content on error
                      showToast('Failed to reformat content', 'error');
                    }
                  }}
                  isReformatting={isReformatting}
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
