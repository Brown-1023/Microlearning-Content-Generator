import React from 'react';

interface OutputPanelProps {
  output: any;
  onShowToast: (message: string, type: string) => void;
}

const OutputPanel: React.FC<OutputPanelProps> = ({ output, onShowToast }) => {
  const handleCopy = () => {
    const text = output?.output || output?.partial_output;
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

  const handleDownload = () => {
    const text = output?.output || output?.partial_output;
    if (!text) {
      onShowToast('No content to download', 'error');
      return;
    }

    const contentType = output?.metadata?.content_type || 'output';
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    const filename = `${contentType.toLowerCase()}_${timestamp}.txt`;

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

  return (
    <div className="output-panel">
      <div className="panel-header">
        <h2>Generated Content</h2>
        <div className="output-actions">
          <button onClick={handleCopy} className="btn btn-outline btn-sm">
            📋 Copy
          </button>
          <button onClick={handleDownload} className="btn btn-outline btn-sm">
            💾 Download
          </button>
        </div>
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
    </div>
  );
};

export default OutputPanel;
