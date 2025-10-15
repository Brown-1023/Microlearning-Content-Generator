import React, { useState } from 'react';

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
  const [generatorModel, setGeneratorModel] = useState('claude');
  const [inputText, setInputText] = useState('');
  const [numQuestions, setNumQuestions] = useState(3);
  const [focusAreas, setFocusAreas] = useState('');

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
      focus_areas: focusAreas || null
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
  };

  const charCount = inputText.length;
  const charCountColor = charCount > 140000 ? 'text-error' : 
                         charCount > 120000 ? 'text-warning' : 
                         'text-secondary';

  return (
    <>
      <div className="config-panel">
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
            <label>Generator Model</label>
            <div className="toggle-group">
              <input
                type="radio"
                id="claude"
                name="generatorModel"
                value="claude"
                checked={generatorModel === 'claude'}
                onChange={(e) => setGeneratorModel(e.target.value)}
                disabled={isLoading}
              />
              <label htmlFor="claude" className="toggle-label">Claude 4.5</label>
              
              <input
                type="radio"
                id="gemini"
                name="generatorModel"
                value="gemini"
                checked={generatorModel === 'gemini'}
                onChange={(e) => setGeneratorModel(e.target.value)}
                disabled={isLoading}
              />
              <label htmlFor="gemini" className="toggle-label">Gemini Pro</label>
            </div>
            <small>Claude Sonnet 4.5 | Gemini 2.5 Pro</small>
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
      </div>

      <div className="input-panel">
        <div className="panel-header">
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
