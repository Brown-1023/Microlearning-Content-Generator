import React, { useState, useEffect } from 'react';
import { modelService, ModelInfo, ModelRestrictions } from '../services/models';

interface ModelRestrictionsProps {
  userRole?: string;
}

const ModelRestrictionsPanel: React.FC<ModelRestrictionsProps> = ({ userRole }) => {
  const [showPanel, setShowPanel] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<{ show: boolean; message: string; type: 'success' | 'error' }>({ 
    show: false, 
    message: '', 
    type: 'success' 
  });
  
  const [allModels, setAllModels] = useState<Record<string, ModelInfo>>({});
  const [restrictionsEnabled, setRestrictionsEnabled] = useState(false);
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [initialRestrictions, setInitialRestrictions] = useState<ModelRestrictions | null>(null);

  // Only show for admins
  if (userRole !== 'admin') {
    return null;
  }

  // Fetch models and current restrictions on mount
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      const response = await modelService.getAvailableModels();
      if (response) {
        setAllModels(response.all_models || {});
        if (response.restrictions) {
          setInitialRestrictions(response.restrictions);
          setRestrictionsEnabled(response.restrictions.enabled);
          setSelectedModels(response.restrictions.allowed_models);
        }
      }
      setIsLoading(false);
    };
    fetchData();
  }, []);

  // Hide save status after 3 seconds
  useEffect(() => {
    if (saveStatus.show) {
      const timer = setTimeout(() => {
        setSaveStatus({ show: false, message: '', type: 'success' });
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [saveStatus.show]);

  const handleToggleModel = (modelId: string) => {
    setSelectedModels(prev => {
      if (prev.includes(modelId)) {
        return prev.filter(id => id !== modelId);
      } else {
        return [...prev, modelId];
      }
    });
  };

  const handleSelectAll = () => {
    setSelectedModels(Object.keys(allModels));
  };

  const handleDeselectAll = () => {
    setSelectedModels([]);
  };

  const handleSave = async () => {
    if (!restrictionsEnabled && selectedModels.length === 0) {
      // If disabling restrictions with no models selected, that's fine
    } else if (restrictionsEnabled && selectedModels.length === 0) {
      setSaveStatus({ 
        show: true, 
        message: 'Please select at least one model when restrictions are enabled', 
        type: 'error' 
      });
      return;
    }

    setIsSaving(true);
    const result = await modelService.updateRestrictions(restrictionsEnabled, selectedModels);
    
    if (result.success) {
      setSaveStatus({ 
        show: true, 
        message: result.message || 'Model restrictions updated successfully!', 
        type: 'success' 
      });
      if (result.restrictions) {
        setInitialRestrictions(result.restrictions);
      }
    } else {
      setSaveStatus({ 
        show: true, 
        message: result.message || 'Failed to update model restrictions', 
        type: 'error' 
      });
    }
    
    setIsSaving(false);
  };

  const handleReset = () => {
    if (initialRestrictions) {
      setRestrictionsEnabled(initialRestrictions.enabled);
      setSelectedModels(initialRestrictions.allowed_models);
    }
  };

  const hasChanges = () => {
    if (!initialRestrictions) return true;
    return restrictionsEnabled !== initialRestrictions.enabled ||
           JSON.stringify(selectedModels.sort()) !== JSON.stringify(initialRestrictions.allowed_models.sort());
  };

  // Group models by category
  const modelsByCategory = Object.entries(allModels).reduce((acc, [modelId, modelInfo]) => {
    if (!acc[modelInfo.category]) {
      acc[modelInfo.category] = [];
    }
    acc[modelInfo.category].push({ id: modelId, ...modelInfo });
    return acc;
  }, {} as Record<string, Array<ModelInfo & { id: string }>>);

  return (
    <div className="model-restrictions-panel elegant-panel">
      <div 
        className="panel-header clickable-header"
        onClick={() => setShowPanel(!showPanel)}
        style={{ cursor: 'pointer' }}
      >
        <div className="header-left">
          <div className="panel-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <path d="M9 9h6" />
              <path d="M9 12h6" />
              <path d="M9 15h2" />
            </svg>
          </div>
          <h2>Model Restrictions</h2>
          <span className="subtitle">(Admin Only - Control which models users can access)</span>
        </div>
        <svg 
          className={`toggle-arrow ${showPanel ? 'rotated' : ''}`}
          width="20" height="20" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2"
        >
          <polyline points="6 9 12 15 18 9"/>
        </svg>
      </div>

      {showPanel && (
        <div className="model-restrictions-content">
          {isLoading ? (
            <div className="loading-state">Loading model configuration...</div>
          ) : (
            <>
              <div className="restriction-toggle">
                <label className="toggle-container">
                  <input
                    type="checkbox"
                    checked={restrictionsEnabled}
                    onChange={(e) => setRestrictionsEnabled(e.target.checked)}
                    disabled={isSaving}
                  />
                  <span className="toggle-label">
                    Enable Model Restrictions
                  </span>
                </label>
                <small className="help-text">
                  When enabled, non-admin users will only see the selected models below.
                  When disabled, all available models are shown to all users.
                </small>
              </div>

              <div className={`models-selection ${!restrictionsEnabled ? 'disabled' : ''}`}>
                <div className="selection-header">
                  <h3>Available Models</h3>
                  <div className="selection-actions">
                    <button 
                      className="btn-small btn-outline"
                      onClick={handleSelectAll}
                      disabled={!restrictionsEnabled || isSaving}
                    >
                      Select All
                    </button>
                    <button 
                      className="btn-small btn-outline"
                      onClick={handleDeselectAll}
                      disabled={!restrictionsEnabled || isSaving}
                    >
                      Deselect All
                    </button>
                  </div>
                </div>

                <div className="models-grid">
                  {Object.entries(modelsByCategory).map(([category, models]) => (
                    <div key={category} className="model-category">
                      <h4 className="category-title">{category}</h4>
                      <div className="category-models">
                        {models.map(model => (
                          <label key={model.id} className="model-checkbox">
                            <input
                              type="checkbox"
                              checked={selectedModels.includes(model.id)}
                              onChange={() => handleToggleModel(model.id)}
                              disabled={!restrictionsEnabled || isSaving}
                            />
                            <span className="model-info">
                              <span className="model-name">{model.display_name}</span>
                              <span className="model-id">{model.id}</span>
                            </span>
                          </label>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>

                {restrictionsEnabled && selectedModels.length === 0 && (
                  <div className="warning-message">
                    ⚠️ No models selected. Users won't be able to generate content. Please select at least one model.
                  </div>
                )}

                {restrictionsEnabled && selectedModels.length > 0 && (
                  <div className="info-message">
                    ℹ️ {selectedModels.length} model{selectedModels.length !== 1 ? 's' : ''} selected for non-admin users
                  </div>
                )}
              </div>

              <div className="panel-footer">
                {saveStatus.show && (
                  <div className={`save-status ${saveStatus.type}`}>
                    {saveStatus.message}
                  </div>
                )}
                <div className="footer-actions">
                  <button 
                    className="btn btn-outline"
                    onClick={handleReset}
                    disabled={isSaving || !hasChanges()}
                  >
                    Reset Changes
                  </button>
                  <button 
                    className="btn btn-primary"
                    onClick={handleSave}
                    disabled={isSaving || !hasChanges()}
                  >
                    {isSaving ? 'Saving...' : 'Save Restrictions'}
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default ModelRestrictionsPanel;
