import React, { useState, useEffect } from 'react';
import { generationService } from '../services/generation';

const SAMPLE_INPUT = `The cardiovascular system consists of the heart, blood vessels, and blood. 
The heart is a muscular pump that circulates blood throughout the body. 
Blood vessels include arteries, veins, and capillaries. 
Arteries carry oxygenated blood away from the heart, while veins return 
deoxygenated blood to the heart. Capillaries are the smallest blood vessels 
where gas exchange occurs.`;

interface GeneratorFormProps {
  onGenerate: (params: any) => void;
  isLoading: boolean;
}

const GeneratorForm: React.FC<GeneratorFormProps> = ({ onGenerate, isLoading }) => {
  const [contentType, setContentType] = useState('MCQ');
  const [generatorModel, setGeneratorModel] = useState('claude-sonnet-4-5-20250929');
  const [inputText, setInputText] = useState('');
  const [numQuestions, setNumQuestions] = useState(3);
  const [focusAreas, setFocusAreas] = useState('');
  const [temperature, setTemperature] = useState(0.51);
  const [topP, setTopP] = useState(0.95);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showPrompts, setShowPrompts] = useState(false);
  
  // All 4 prompts state
  const [mcqGeneratorPrompt, setMcqGeneratorPrompt] = useState('');
  const [mcqFormatterPrompt, setMcqFormatterPrompt] = useState('');
  const [nmcqGeneratorPrompt, setNmcqGeneratorPrompt] = useState('');
  const [nmcqFormatterPrompt, setNmcqFormatterPrompt] = useState('');
  
  // Default prompts for reset functionality
  const [defaultPrompts, setDefaultPrompts] = useState({
    mcq_generator: '',
    mcq_formatter: '',
    nmcq_generator: '',
    nmcq_formatter: ''
  });

  // Fetch default prompts on component mount
  useEffect(() => {
    const fetchPrompts = async () => {
      const prompts = await generationService.getDefaultPrompts();
      if (prompts) {
        setDefaultPrompts(prompts);
        setMcqGeneratorPrompt(prompts.mcq_generator);
        setMcqFormatterPrompt(prompts.mcq_formatter);
        setNmcqGeneratorPrompt(prompts.nmcq_generator);
        setNmcqFormatterPrompt(prompts.nmcq_formatter);
      }
    };
    fetchPrompts();
  }, []);

  const handleSubmit = () => {
    if (!inputText.trim()) {
      alert('Please enter some text to analyze');
      return;
    }

    if (inputText.length < 50) {
      alert('Input text is too short. Please provide more content.');
      return;
    }

    onGenerate({
      content_type: contentType,
      generator_model: generatorModel,
      input_text: inputText,
      num_questions: numQuestions,
      focus_areas: focusAreas || null,
      temperature: temperature,
      top_p: topP,
      custom_mcq_generator: mcqGeneratorPrompt !== defaultPrompts.mcq_generator ? mcqGeneratorPrompt : null,
      custom_mcq_formatter: mcqFormatterPrompt !== defaultPrompts.mcq_formatter ? mcqFormatterPrompt : null,
      custom_nmcq_generator: nmcqGeneratorPrompt !== defaultPrompts.nmcq_generator ? nmcqGeneratorPrompt : null,
      custom_nmcq_formatter: nmcqFormatterPrompt !== defaultPrompts.nmcq_formatter ? nmcqFormatterPrompt : null
    });
  };

  const handleLoadSample = () => {
    setInputText(SAMPLE_INPUT);
  };

  const handleClear = () => {
    if (inputText && !confirm('Are you sure you want to clear the input?')) {
      return;
    }
    setInputText('');
    setFocusAreas('');
    // Reset prompts to defaults
    setMcqGeneratorPrompt(defaultPrompts.mcq_generator);
    setMcqFormatterPrompt(defaultPrompts.mcq_formatter);
    setNmcqGeneratorPrompt(defaultPrompts.nmcq_generator);
    setNmcqFormatterPrompt(defaultPrompts.nmcq_formatter);
  };

  const charCount = inputText.length;
  const charCountColor = charCount > 140000 ? 'text-error' : 
                         charCount > 120000 ? 'text-warning' : 
                         'text-secondary';

  return (
    <>
      <div className="config-panel elegant-panel">
        <div className="panel-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="3"/>
            <path d="M12 1v6m0 6v6m9-9h-6m-6 0H3"/>
          </svg>
        </div>
        <h2>Configuration</h2>
        
        <div className="config-grid">
          <div className="config-group">
            <label>Content Type</label>
            <div className="toggle-group">
              <input
                type="radio"
                id="mcq"
                name="contentType"
                value="MCQ"
                checked={contentType === 'MCQ'}
                onChange={(e) => setContentType(e.target.value)}
                disabled={isLoading}
              />
              <label htmlFor="mcq" className="toggle-label">MCQ</label>
              
              <input
                type="radio"
                id="nmcq"
                name="contentType"
                value="NMCQ"
                checked={contentType === 'NMCQ'}
                onChange={(e) => setContentType(e.target.value)}
                disabled={isLoading}
              />
              <label htmlFor="nmcq" className="toggle-label">Non-MCQ</label>
            </div>
            <small>MCQ: Multiple Choice | Non-MCQ: Clinical Vignettes</small>
          </div>

          <div className="config-group">
            <label htmlFor="generatorModel">Generator Model</label>
            <select
              id="generatorModel"
              value={generatorModel}
              onChange={(e) => setGeneratorModel(e.target.value)}
              disabled={isLoading}
              className="model-select"
            >
              <optgroup label="Anthropic Claude">
                <option value="claude-sonnet-4-5-20250929">claude-sonnet-4-5-20250929</option>
                <option value="claude-opus-4-1-20250805">claude-opus-4-1-20250805</option>
              </optgroup>
              <optgroup label="Google Gemini">
                <option value="gemini-2.5-pro">gemini-2.5-pro</option>
                <option value="gemini-2.5-flash">gemini-2.5-flash</option>
              </optgroup>
            </select>
            <small>Select the AI model for content generation</small>
          </div>

          <div className="config-group">
            <label htmlFor="numQuestions">Number of Questions</label>
            <input
              type="number"
              id="numQuestions"
              min="1"
              max="20"
              value={numQuestions}
              onChange={(e) => setNumQuestions(parseInt(e.target.value))}
              disabled={isLoading}
            />
            <small>Generate 1-20 questions</small>
          </div>

          <div className="config-group">
            <label htmlFor="focusAreas">Focus Areas (Optional)</label>
            <input
              type="text"
              id="focusAreas"
              placeholder="e.g., diagnosis, treatment, pathophysiology"
              value={focusAreas}
              onChange={(e) => setFocusAreas(e.target.value)}
              disabled={isLoading}
            />
            <small>Specific topics to emphasize</small>
          </div>

        </div>
        
        <div className="advanced-toggle" onClick={() => setShowAdvanced(!showAdvanced)}>
          <span className="toggle-text">
            {showAdvanced ? 'Hide' : 'Show'} Advanced Settings
          </span>
          <svg 
            className={`toggle-arrow ${showAdvanced ? 'rotated' : ''}`}
            width="20" height="20" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2"
          >
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </div>

        {showAdvanced && (
        <div className="advanced-settings">
          <div className="config-group">
            <label htmlFor="temperature">
              <span className="label-icon">🌡️</span>
              Temperature
            </label>
            <div className="slider-container">
              <input
                type="range"
                id="temperature"
                min="0"
                max="1"
                step="0.01"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                disabled={isLoading}
              />
              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                disabled={isLoading}
                className="slider-value"
              />
            </div>
            <small>Controls randomness (0 = focused, 1 = creative)</small>
          </div>

          <div className="config-group">
            <label htmlFor="topP">
              <span className="label-icon">🎯</span>
              Top P (Nucleus Sampling)
            </label>
            <div className="slider-container">
              <input
                type="range"
                id="topP"
                min="0"
                max="1"
                step="0.01"
                value={topP}
                onChange={(e) => setTopP(parseFloat(e.target.value))}
                disabled={isLoading}
              />
              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={topP}
                onChange={(e) => setTopP(parseFloat(e.target.value))}
                disabled={isLoading}
                className="slider-value"
              />
            </div>
            <small>Nucleus sampling threshold</small>
          </div>
        </div>
        )}
      </div>

      <div className="prompts-panel elegant-panel">
        <div className="prompts-header" onClick={() => setShowPrompts(!showPrompts)}>
          <div className="header-left">
            <div className="panel-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
              </svg>
            </div>
            <h2>Prompt Templates</h2>
            <span className="prompt-subtitle">(Click to view and edit all 4 prompts)</span>
          </div>
          <svg 
            className={`toggle-arrow ${showPrompts ? 'rotated' : ''}`}
            width="20" height="20" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2"
          >
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </div>
        
        {showPrompts && (
          <div className="all-prompts-container">
            <div className="prompts-grid">
              <div className="prompt-box">
                <div className="prompt-header">
                  <h4>📝 MCQ Generator Prompt</h4>
                  <button 
                    className="reset-btn"
                    onClick={() => setMcqGeneratorPrompt(defaultPrompts.mcq_generator)}
                    disabled={isLoading}
                    title="Reset to default"
                  >
                    ↻
                  </button>
                </div>
                <textarea
                  value={mcqGeneratorPrompt}
                  onChange={(e) => setMcqGeneratorPrompt(e.target.value)}
                  disabled={isLoading}
                  rows={8}
                  className="prompt-textarea"
                />
                <small>Template for generating MCQ questions</small>
              </div>

              <div className="prompt-box">
                <div className="prompt-header">
                  <h4>🎨 MCQ Formatter Prompt</h4>
                  <button 
                    className="reset-btn"
                    onClick={() => setMcqFormatterPrompt(defaultPrompts.mcq_formatter)}
                    disabled={isLoading}
                    title="Reset to default"
                  >
                    ↻
                  </button>
                </div>
                <textarea
                  value={mcqFormatterPrompt}
                  onChange={(e) => setMcqFormatterPrompt(e.target.value)}
                  disabled={isLoading}
                  rows={8}
                  className="prompt-textarea"
                />
                <small>Template for formatting MCQ output</small>
              </div>

              <div className="prompt-box">
                <div className="prompt-header">
                  <h4>📋 Non-MCQ Generator Prompt</h4>
                  <button 
                    className="reset-btn"
                    onClick={() => setNmcqGeneratorPrompt(defaultPrompts.nmcq_generator)}
                    disabled={isLoading}
                    title="Reset to default"
                  >
                    ↻
                  </button>
                </div>
                <textarea
                  value={nmcqGeneratorPrompt}
                  onChange={(e) => setNmcqGeneratorPrompt(e.target.value)}
                  disabled={isLoading}
                  rows={8}
                  className="prompt-textarea"
                />
                <small>Template for generating Non-MCQ questions</small>
              </div>

              <div className="prompt-box">
                <div className="prompt-header">
                  <h4>🖌️ Non-MCQ Formatter Prompt</h4>
                  <button 
                    className="reset-btn"
                    onClick={() => setNmcqFormatterPrompt(defaultPrompts.nmcq_formatter)}
                    disabled={isLoading}
                    title="Reset to default"
                  >
                    ↻
                  </button>
                </div>
                <textarea
                  value={nmcqFormatterPrompt}
                  onChange={(e) => setNmcqFormatterPrompt(e.target.value)}
                  disabled={isLoading}
                  rows={8}
                  className="prompt-textarea"
                />
                <small>Template for formatting Non-MCQ output</small>
              </div>
            </div>
            
            <div className="prompts-footer">
              <button 
                className="btn btn-outline"
                onClick={() => {
                  setMcqGeneratorPrompt(defaultPrompts.mcq_generator);
                  setMcqFormatterPrompt(defaultPrompts.mcq_formatter);
                  setNmcqGeneratorPrompt(defaultPrompts.nmcq_generator);
                  setNmcqFormatterPrompt(defaultPrompts.nmcq_formatter);
                }}
                disabled={isLoading}
              >
                Reset All to Defaults
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="input-panel elegant-panel">
        <div className="panel-header">
          <div className="panel-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
          </div>
          <h2>Input Text</h2>
          <div className={`char-counter ${charCountColor}`}>
            <span>{charCount.toLocaleString()}</span> / 150,000 characters
          </div>
        </div>
        
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Paste or type your educational content here..."
          maxLength={150000}
          disabled={isLoading}
        />
        
        <div className="action-buttons">
          <button 
            onClick={handleClear} 
            className="btn btn-outline"
            disabled={isLoading}
          >
            Clear
          </button>
          <button 
            onClick={handleLoadSample} 
            className="btn btn-outline"
            disabled={isLoading}
          >
            Load Sample
          </button>
          <button 
            onClick={handleSubmit} 
            className="btn btn-primary"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span>Generating...</span>
                <span className="spinner"></span>
              </>
            ) : (
              'Generate Content'
            )}
          </button>
        </div>
      </div>
    </>
  );
};

export default GeneratorForm;
