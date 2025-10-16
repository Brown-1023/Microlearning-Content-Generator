# UI Enhancement Guide - Professional Interface with Advanced Controls

## 🎨 Overview

The UI has been completely revamped with a professional design and advanced features that provide granular control over the content generation process. The interface now supports dual custom prompts, precise model selection, and fine-tuned generation parameters.

## ✨ Key Features

### 1. **Professional Design Elements**
- **Elegant Panels** with gradient backgrounds and hover effects
- **Icon Integration** for visual hierarchy
- **Smooth Animations** for interactive elements
- **Responsive Layout** optimized for all screen sizes

### 2. **Dual Custom Prompt System**
The UI now supports separate customization of both generation phases:

#### **Generator Prompt** 
- Controls the initial content creation
- Supports placeholders: `{{TEXT_TO_ANALYZE}}`, `{{NUM_QUESTIONS}}`, `{{FOCUS_AREAS}}`
- Allows complete override of default generation logic

#### **Formatter Prompt**
- Controls the formatting and refinement phase
- Applied to the generated content
- Ensures consistent output structure

### 3. **Enhanced Model Selection**
Direct selection of specific model versions with proper API integration:

#### **Anthropic Models**
- `claude-3-5-sonnet-20241022` - Claude 3.5 Sonnet (Latest)
- `claude-3-opus-20240229` - Claude 3 Opus

#### **Google Models**
- `gemini-2.0-pro-exp` - Gemini 2.0 Pro (Experimental)
- `gemini-1.5-pro` - Gemini 1.5 Pro
- `gemini-2.0-flash-exp` - Gemini 2.0 Flash (Experimental)

### 4. **Advanced Settings Panel**
Collapsible advanced settings section with:
- **Temperature Control** (0.0 - 1.0) with visual slider and numeric input
- **Top-P Control** (0.0 - 1.0) for nucleus sampling
- **Expert Mode** for custom prompt configuration

### 5. **Visual Enhancements**
- **Panel Icons** for quick identification
- **Label Icons** (🌡️, 🎯, ✨) for better UX
- **Gradient Backgrounds** for visual appeal
- **Hover Effects** on interactive elements
- **Smooth Transitions** for state changes

## 📋 Usage Guide

### Basic Operation
1. Select content type (MCQ/Non-MCQ)
2. Choose a specific model from the dropdown
3. Enter your educational content
4. Set number of questions and focus areas
5. Click "Generate Content"

### Advanced Configuration

#### Using Custom Prompts
1. Click "Show Advanced Settings"
2. Enable "Use Custom Prompts (Expert Mode)"
3. Enter your custom generator prompt
4. Optionally enter a custom formatter prompt
5. Both prompts work together in the pipeline

#### Fine-Tuning Generation
- **Lower Temperature (0.0-0.3):** More deterministic, focused outputs
- **Medium Temperature (0.4-0.6):** Balanced creativity
- **Higher Temperature (0.7-1.0):** More creative, varied outputs

## 🔧 API Integration

### Request Structure
```json
{
  "content_type": "MCQ",
  "generator_model": "claude-3-5-sonnet-20241022",
  "input_text": "...",
  "num_questions": 3,
  "focus_areas": "pathophysiology",
  "temperature": 0.5,
  "top_p": 0.9,
  "custom_generator_prompt": "...",  // Optional
  "custom_formatter_prompt": "..."    // Optional
}
```

### Model Pipeline Flow
```
1. Load Prompts → 
2. Generator (Selected Model + Custom Generator Prompt if provided) → 
3. Formatter (Gemini Flash + Custom Formatter Prompt if provided) → 
4. Validator → 
5. Output
```

## 🎯 Four Prompt System

The system uses four base prompts that can be customized:

1. **MCQ Generator Template** (`mcq.generator.txt`)
   - Default prompt for MCQ generation
   - Can be overridden with custom generator prompt

2. **MCQ Formatter** (`mcq.formatter.txt`)
   - Default prompt for MCQ formatting
   - Can be overridden with custom formatter prompt

3. **Non-MCQ Generator** (`nonmcq.generator.txt`)
   - Default prompt for NMCQ generation
   - Can be overridden with custom generator prompt

4. **Non-MCQ Formatter** (`nonmcq.formatter.txt`)
   - Default prompt for NMCQ formatting
   - Can be overridden with custom formatter prompt

## 🧪 Testing

### Quick Test
```bash
# Start backend
cd backend
python app.py

# In another terminal, start frontend
cd frontend
npm run dev

# Run comprehensive tests
cd backend
python test_all_features.py
```

### Test Coverage
- ✅ All model variants working correctly
- ✅ Dual custom prompts (generator + formatter)
- ✅ Temperature and Top-P parameters
- ✅ Backward compatibility with old model names
- ✅ Professional UI with all controls

## 🎨 UI Components

### Configuration Panel
- Model dropdown with grouped options
- Content type toggle (MCQ/Non-MCQ)
- Number of questions input
- Focus areas text field

### Advanced Settings (Collapsible)
- Temperature slider with numeric input
- Top-P slider with numeric input
- Custom prompts section with dual textareas

### Input Panel
- Large textarea for content input
- Character counter with color coding
- Sample text loader
- Clear and Generate buttons

## 💡 Best Practices

1. **Model Selection**
   - Use Claude models for complex reasoning
   - Use Gemini Pro for comprehensive analysis
   - Use Gemini Flash for quick iterations

2. **Custom Prompts**
   - Keep placeholders intact when customizing
   - Test prompts with small inputs first
   - Ensure output format requirements are maintained

3. **Temperature Settings**
   - Use low values (0.2-0.4) for consistent medical content
   - Use medium values (0.5-0.7) for balanced generation
   - Use high values (0.8-1.0) only for creative exploration

## 🔍 Troubleshooting

### Issue: Model not generating content
**Solution:** Ensure API keys are properly set for the selected model provider

### Issue: Custom prompts not working
**Solution:** Verify all placeholders are present and correctly formatted

### Issue: Output validation failing
**Solution:** Custom prompts must instruct the model to follow MCQ/NMCQ format requirements

## 📈 Performance Tips

1. **Optimal Settings**
   - Temperature: 0.5-0.6
   - Top-P: 0.9-0.95
   - Questions: 3-5 per request

2. **Model Performance**
   - Claude 3.5 Sonnet: Best for complex medical scenarios
   - Gemini 2.0 Pro: Excellent for comprehensive coverage
   - Gemini Flash: Fastest for quick iterations

## 🚀 Future Enhancements

- Prompt template library
- Saved configuration presets
- Batch processing support
- Export in multiple formats
- A/B testing for prompts
