import React from 'react';

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
}

const StreamingOutputPanel: React.FC<StreamingOutputPanelProps> = ({ 
  progress, 
  draft, 
  output, 
  isStreaming, 
  onShowToast 
}) => {
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

      {/* Draft Section - Show when draft is available */}
      {draft && (
        <div className="draft-section">
          <div className="section-header">
            <h3>📝 Initial Draft</h3>
            <div className="draft-actions">
              <button 
                onClick={() => handleCopy(draft)} 
                className="btn btn-outline btn-sm"
              >
                📋 Copy Draft
              </button>
              <button 
                onClick={() => handleDownload(draft, 'draft')} 
                className="btn btn-outline btn-sm"
              >
                💾 Download Draft
              </button>
            </div>
          </div>
          <div className="draft-content">
            <pre>{draft}</pre>
          </div>
        </div>
      )}

      {/* Final Output Section */}
      {output && !isStreaming && (
        <>
          <div className="output-actions">
            <button 
              onClick={() => handleCopy(output.output || output.partial_output)} 
              className="btn btn-primary btn-sm"
            >
              📋 Copy Final Output
            </button>
            <button 
              onClick={() => handleDownload(output.output || output.partial_output, output?.metadata?.content_type || 'output')} 
              className="btn btn-primary btn-sm"
            >
              💾 Download Final Output
            </button>
          </div>

          {output.success && (
            <div className="status-message success">
              ✅ Content generated successfully!
            </div>
          )}

          {!output.success && output.validation_errors?.length > 0 && (
            <>
              <div className="status-message warning">
                ⚠️ Generation completed with validation errors
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
              </div>
            </>
          )}

          {!output.success && output.error && !output.validation_errors?.length && (
            <div className="status-message error">
              ❌ {output.error}
            </div>
          )}

          {(output.output || output.partial_output) && (
            <div className="output-content">
              <pre>{output.output || output.partial_output}</pre>
            </div>
          )}

          {output.metadata && (
            <div className="metadata">
              <h3>Generation Details</h3>
              <div className="metadata-content">
                <div className="metadata-item">
                  <span className="metadata-label">Content Type:</span>
                  <span className="metadata-value">{output.metadata.content_type}</span>
                </div>
                <div className="metadata-item">
                  <span className="metadata-label">Generator Model:</span>
                  <span className="metadata-value">{output.metadata.generator_model}</span>
                </div>
                <div className="metadata-item">
                  <span className="metadata-label">Questions Generated:</span>
                  <span className="metadata-value">{output.metadata.num_questions}</span>
                </div>
                <div className="metadata-item">
                  <span className="metadata-label">Formatter Retries:</span>
                  <span className="metadata-value">{output.metadata.formatter_retries}</span>
                </div>
                <div className="metadata-item">
                  <span className="metadata-label">Total Time:</span>
                  <span className="metadata-value">{output.metadata.total_time?.toFixed(2)}s</span>
                </div>
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

        .output-actions {
          display: flex;
          gap: 12px;
          margin-bottom: 16px;
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
          background: #f9fafb;
          border: 1px solid #e5e7eb;
          border-radius: 6px;
          padding: 16px;
          margin-bottom: 16px;
        }

        .output-content pre {
          margin: 0;
          font-size: 13px;
          line-height: 1.5;
          white-space: pre-wrap;
          word-wrap: break-word;
        }

        .metadata {
          background: #f3f4f6;
          border-radius: 6px;
          padding: 16px;
        }

        .metadata h3 {
          font-size: 14px;
          font-weight: 600;
          color: #374151;
          margin: 0 0 12px 0;
        }

        .metadata-content {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 12px;
        }

        .metadata-item {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .metadata-label {
          font-size: 12px;
          color: #6b7280;
        }

        .metadata-value {
          font-size: 14px;
          font-weight: 500;
          color: #111827;
        }
      `}</style>
    </div>
  );
};

export default StreamingOutputPanel;
