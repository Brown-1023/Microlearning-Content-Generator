import React, { useState, useEffect, useRef } from 'react';

interface StreamingOutputPanelProps {
  progress: {
    stage: string;
    message: string;
    progress: number;
  } | null;
  draft: string | null;
  output: any;
  isStreaming: boolean;
  onShowToast: (message: string, type: string) => void;
  onReformat?: () => void;
  isReformatting?: boolean;
  streamingDraft?: string;
  streamingFormatted?: string;
  onFormatDraft?: () => void;
  isFormattingDraft?: boolean;
}

const StreamingOutputPanel: React.FC<StreamingOutputPanelProps> = ({ 
  progress, 
  draft, 
  output, 
  isStreaming, 
  onShowToast,
  onReformat,
  isReformatting = false,
  streamingDraft = '',
  streamingFormatted = '',
  onFormatDraft,
  isFormattingDraft = false
}) => {
  const draftRef = useRef<HTMLDivElement>(null);
  const formattedRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new content arrives
  useEffect(() => {
    if (draftRef.current && streamingDraft) {
      draftRef.current.scrollTop = draftRef.current.scrollHeight;
    }
  }, [streamingDraft]);

  useEffect(() => {
    if (formattedRef.current && streamingFormatted) {
      formattedRef.current.scrollTop = formattedRef.current.scrollHeight;
    }
  }, [streamingFormatted]);
  const handleCopy = (text: string) => {
    if (!text) {
      onShowToast('No content to copy', 'error');
      return;
    }

    navigator.clipboard.writeText(text).then(() => {
      onShowToast('Copied to clipboard!', 'success');
    }).catch(() => {
      // Fallback method
      const textarea = document.createElement('textarea');
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      onShowToast('Copied to clipboard!', 'success');
    });
  };

  const handleDownload = (text: string, type: string = 'output') => {
    if (!text) {
      onShowToast('No content to download', 'error');
      return;
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    const filename = `${type.toLowerCase()}_${timestamp}.txt`;

    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    onShowToast(`Downloaded as ${filename}`, 'success');
  };

  const getStageIcon = (stage: string) => {
    switch (stage) {
      case 'load_prompts': return '📄';
      case 'generator': return '🤖';
      case 'formatter': return '✨';
      case 'validator': return '✅';
      case 'retry': return '🔄';
      case 'done': return '🎉';
      case 'fail': return '⚠️';
      case 'error': return '❌';
      default: return '⏳';
    }
  };

  const getProgressBarColor = (stage: string) => {
    if (stage === 'done') return '#10b981';
    if (stage === 'fail' || stage === 'error') return '#f59e0b';
    return '#3b82f6';
  };

  return (
    <div className="streaming-output-panel">
      <div className="panel-header">
        <h2>Generated Content</h2>
      </div>

      {/* Progress Section - Show during streaming */}
      {isStreaming && progress && (
        <div className="streaming-progress">
          <div className="progress-header">
            <span className="stage-icon">{getStageIcon(progress.stage)}</span>
            <span className="progress-message">{progress.message}</span>
            <span className="progress-percentage">{progress.progress}%</span>
          </div>
          <div className="progress-bar-container">
            <div 
              className="progress-bar" 
              style={{ 
                width: `${progress.progress}%`,
                backgroundColor: getProgressBarColor(progress.stage)
              }}
            />
          </div>
        </div>
      )}

      {/* Streaming Draft Section - Show when generating or draft is available */}
      {(streamingDraft || draft) && !output && (
        <div className="draft-section">
          <div className="section-header">
            <h3>📝 {streamingDraft && isStreaming ? 'Generating Initial Draft...' : 'Initial Draft'}</h3>
            
          </div>
          <div className="draft-content streaming-content" ref={draftRef}>
            <pre>{streamingDraft || draft}</pre>
            {isStreaming && streamingDraft && (
              <span className="cursor-blink">▊</span>
            )}
          </div>
          <div>
            {!isStreaming && !isFormattingDraft && (draft || streamingDraft) && (
              <div className="draft-actions">
                <button 
                  onClick={() => handleCopy(draft || streamingDraft)} 
                  className="btn btn-outline btn-sm"
                >
                  📋 Copy Draft
                </button>
                <button 
                  onClick={() => handleDownload(draft || streamingDraft, 'draft')} 
                  className="btn btn-outline btn-sm"
                >
                  💾 Download Draft
                </button>
                {onFormatDraft && (
                  <button 
                    onClick={onFormatDraft}
                    className="btn btn-primary btn-sm"
                    style={{ marginLeft: 'auto' }}
                  >
                    ✨ Format Draft
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Streaming Formatted Section - Show when formatting or reformatting */}
      {streamingFormatted && (isReformatting || isFormattingDraft || !output) && (
        <div className="formatted-section">
          <div className="section-header">
            <h3>✨ {(isStreaming || isReformatting || isFormattingDraft) ? 'Formatting Content...' : 'Formatted Content'}</h3>
          </div>
          <div className="formatted-content streaming-content" ref={formattedRef}>
            <pre>{streamingFormatted}</pre>
            {(isStreaming || isReformatting || isFormattingDraft) && (
              <span className="cursor-blink">▊</span>
            )}
          </div>
        </div>
      )}

      {/* Final Output Section */}
      {output && !isStreaming && (
        <>
          {output.success && (
            <div className="status-message success">
              ✅ Content generated successfully!
            </div>
          )}

          {!output.success && output.validation_errors?.length > 0 && (
            <>
              <div className="status-message warning">
                <span>⚠️ Generation completed with validation errors</span>
                {onReformat && (
                  <button 
                    onClick={onReformat}
                    disabled={isReformatting}
                    className="btn btn-warning btn-sm"
                    style={{ marginLeft: 'auto' }}
                  >
                    {isReformatting ? '🔄 Reformatting...' : '🔧 Reformat Output'}
                  </button>
                )}
              </div>
              <div className="validation-errors">
                <h3>Validation Errors ({output.validation_errors.length})</h3>
                <ul>
                  {output.validation_errors.map((err: any, idx: number) => (
                    <li key={idx}>
                      Line {err.line || 'N/A'}: {err.message}
                    </li>
                  ))}
                </ul>
                <p className="reformat-tip">
                  💡 <strong>Tip:</strong> If reformatting fails repeatedly, try adjusting the formatter prompt in the admin panel for better results.
                </p>
              </div>
            </>
          )}

          {!output.success && output.error && !output.validation_errors?.length && (
            <div className="status-message error">
              ❌ {output.error}
            </div>
          )}

          {(output.output || output.partial_output) && (
            <div className="output-section">
              <div className="output-content">
                <pre>{output.output || output.partial_output}</pre>
              </div>
              <div className="output-actions">
                <button 
                  onClick={() => handleCopy(output.output || output.partial_output)} 
                  className="action-button copy-btn"
                >
                  <svg className="button-icon" width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M10.5 1h-6A1.5 1.5 0 003 2.5v9A1.5 1.5 0 004.5 13h6a1.5 1.5 0 001.5-1.5v-9A1.5 1.5 0 0010.5 1zM4.5 2h6a.5.5 0 01.5.5v9a.5.5 0 01-.5.5h-6a.5.5 0 01-.5-.5v-9a.5.5 0 01.5-.5z"/>
                    <path d="M13 4.5V12a1.5 1.5 0 01-1.5 1.5h-7v1h7A2.5 2.5 0 0014 12V4.5h-1z"/>
                  </svg>
                  Copy Final Output
                </button>
                <button 
                  onClick={() => handleDownload(output.output || output.partial_output, output?.metadata?.content_type || 'output')} 
                  className="action-button download-btn"
                >
                  <svg className="button-icon" width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M8 11.5l3.5-3.5L10 6.5 9 7.5V1H7v6.5L6 6.5 4.5 8 8 11.5z"/>
                    <path d="M13 13v-1h1v1a1 1 0 01-1 1H3a1 1 0 01-1-1v-1h1v1h10z"/>
                  </svg>
                  Download Final Output
                </button>
              </div>
            </div>
          )}

          
        </>
      )}

      <style jsx>{`
        .streaming-output-panel {
          background: white;
          border-radius: 12px;
          padding: 24px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
          margin-top: 24px;
          padding-bottom: 46px !important;
        }

        .panel-header {
          margin-bottom: 20px;
        }

        .panel-header h2 {
          font-size: 20px;
          font-weight: 600;
          color: #111827;
          margin: 0;
        }

        .streaming-progress {
          background: #f9fafb;
          border-radius: 8px;
          padding: 16px;
          margin-bottom: 20px;
        }

        .progress-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 12px;
        }

        .stage-icon {
          font-size: 24px;
        }

        .progress-message {
          flex: 1;
          font-size: 14px;
          color: #374151;
          font-weight: 500;
        }

        .progress-percentage {
          font-size: 14px;
          font-weight: 600;
          color: #111827;
        }

        .progress-bar-container {
          width: 100%;
          height: 8px;
          background: #e5e7eb;
          border-radius: 4px;
          overflow: hidden;
        }

        .progress-bar {
          height: 100%;
          transition: width 0.3s ease;
          border-radius: 4px;
        }

        .draft-section {
          background: #fef3c7;
          border-radius: 8px;
          padding: 16px;
          margin-bottom: 20px;
        }

        .section-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }

        .section-header h3 {
          font-size: 16px;
          font-weight: 600;
          color: #92400e;
          margin: 0;
        }

        .draft-actions {
          display: flex;
          gap: 8px;
        }

        .draft-content {
          background: white;
          border-radius: 4px;
          padding: 12px;
          max-height: 300px;
          overflow-y: auto;
        }

        .draft-content pre {
          margin: 0;
          font-size: 13px;
          line-height: 1.5;
          white-space: pre-wrap;
          word-wrap: break-word;
        }

        .output-section {
          margin-bottom: 24px;
        }

        .output-actions {
          display: flex;
          gap: 12px;
          margin-top: 16px;
          justify-content: flex-end;
          padding: 0 16px;
        }

        .action-button {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          padding: 10px 20px;
          border: none;
          border-radius: 8px;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s ease;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .action-button.copy-btn {
          background: #3b82f6;
          color: white;
        }

        .action-button.copy-btn:hover {
          background: #2563eb;
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
        }

        .action-button.download-btn {
          background: #10b981;
          color: white;
        }

        .action-button.download-btn:hover {
          background: #059669;
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
        }

        .button-icon {
          width: 16px;
          height: 16px;
          flex-shrink: 0;
        }

        .btn {
          padding: 8px 16px;
          border-radius: 6px;
          font-size: 14px;
          font-weight: 500;
          border: none;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-primary {
          background: #3b82f6;
          color: white;
        }

        .btn-primary:hover {
          background: #2563eb;
        }

        .btn-outline {
          background: transparent;
          border: 1px solid #d1d5db;
          color: #374151;
        }

        .btn-outline:hover {
          background: #f3f4f6;
        }

        .btn-sm {
          padding: 6px 12px;
          font-size: 13px;
        }

        .btn-warning {
          background: #f59e0b;
          color: white;
        }

        .btn-warning:hover {
          background: #d97706;
        }

        .btn-warning:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .status-message {
          padding: 12px 16px;
          border-radius: 6px;
          margin-bottom: 16px;
          font-size: 14px;
          font-weight: 500;
        }

        .status-message.success {
          background: #d1fae5;
          color: #065f46;
          border: 1px solid #6ee7b7;
        }

        .status-message.warning {
          background: #fed7aa;
          color: #92400e;
          border: 1px solid #fb923c;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }

        .status-message.error {
          background: #fee2e2;
          color: #991b1b;
          border: 1px solid #fca5a5;
        }

        .validation-errors {
          background: #fef2f2;
          border: 1px solid #fecaca;
          border-radius: 6px;
          padding: 16px;
          margin-bottom: 16px;
        }

        .validation-errors h3 {
          font-size: 14px;
          font-weight: 600;
          color: #991b1b;
          margin: 0 0 8px 0;
        }

        .validation-errors ul {
          list-style: none;
          margin: 0;
          padding: 0;
        }

        .validation-errors li {
          font-size: 13px;
          color: #b91c1c;
          margin-bottom: 4px;
        }

        .output-content {
          background: #ffffff;
          border: 1px solid #e5e7eb;
          border-radius: 12px;
          padding: 24px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
          position: relative;
        }

        .output-content pre {
          margin: 0;
          font-size: 14px;
          line-height: 1.6;
          white-space: pre-wrap;
          word-wrap: break-word;
          color: #1f2937;
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        }

        .metadata-panel {
          background: #ffffff;
          border: 1px solid #e5e7eb;
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }

        .metadata-header {
          background: #f9fafb;
          padding: 16px 20px;
          border-bottom: 1px solid #e5e7eb;
        }

        .metadata-header h3 {
          font-size: 16px;
          font-weight: 600;
          color: #111827;
          margin: 0;
          display: flex;
          align-items: center;
        }

        .metadata-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          padding: 20px;
          gap: 24px;
        }

        .metadata-item {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .metadata-label {
          font-size: 12px;
          font-weight: 500;
          color: #6b7280;
          text-transform: uppercase;
          letter-spacing: 0.025em;
        }

        .metadata-value {
          font-size: 15px;
          font-weight: 600;
          color: #111827;
        }
        
        .streaming-content {
          max-height: 500px;
          overflow-y: auto;
          position: relative;
        }
        
        .cursor-blink {
          animation: blink 1s infinite;
          color: #3b82f6;
          font-weight: bold;
        }
        
        @keyframes blink {
          0%, 50% { opacity: 1; }
          51%, 100% { opacity: 0; }
        }
        
        .formatted-section {
          margin-top: 20px;
          background: white;
          border-radius: 8px;
          padding: 20px;
          border: 1px solid #e5e7eb;
        }
        
        .formatted-content {
          background: #f9fafb;
          padding: 16px;
          border-radius: 6px;
          margin-top: 12px;
        }
      `}</style>
    </div>
  );
};

export default StreamingOutputPanel;
