# Complete Feature Guide - Four Prompt System with Professional UI

## 🎯 Overview

The system now features a complete four-prompt editing system where users can view and modify all default prompts directly in the UI. Each prompt is pre-loaded with its default content, allowing users to understand and customize the entire generation pipeline.

## 🔥 Key Features Implemented

### 1. **Four Editable Prompt Fields**
All four prompts are now visible and editable in the UI:
- **MCQ Generator Prompt** - Controls MCQ question generation
- **MCQ Formatter Prompt** - Formats MCQ output structure
- **Non-MCQ Generator Prompt** - Controls NMCQ generation
- **Non-MCQ Formatter Prompt** - Formats NMCQ output

Each prompt:
- Shows the original default content on load
- Can be edited in real-time
- Has an individual reset button (↻)
- Includes helpful descriptions

### 2. **Model Selection Updates**
Enhanced model dropdown now includes:

**Anthropic Claude:**
- Claude 4.5 (Latest) - Maps to most recent available model
- Claude 3.5 Sonnet
- Claude 3 Opus

**Google Gemini:**
- Gemini 2.5 Pro (Latest) - Maps to most recent available model
- Gemini 2.0 Pro
- Gemini 1.5 Pro
- Gemini 2.0 Flash

### 3. **Professional UI Design**

#### **Collapsible Prompt Panel**
- Click header to expand/collapse
- Smooth animations
- Clear visual hierarchy
- Icon indicators

#### **Grid Layout**
- 2x2 grid for prompts (responsive)
- Each prompt in its own card
- Hover effects and shadows
- Professional typography

#### **Reset Functionality**
- Individual reset buttons per prompt
- "Reset All to Defaults" button
- Visual feedback on hover

## 📸 UI Components

### Main Sections:
1. **Configuration Panel** - Model selection and basic settings
2. **Advanced Settings** - Temperature and Top-P controls (collapsible)
3. **Prompt Templates Panel** - All 4 prompts (collapsible)
4. **Input Panel** - Text input area

## 🚀 How It Works

### Workflow:
1. **On Page Load:**
   - Frontend fetches all 4 default prompts from `/api/prompts`
   - Prompts are populated in their respective textareas
   - User sees exactly what templates will be used

2. **During Editing:**
   - User can modify any prompt directly
   - Changes are tracked against defaults
   - Only modified prompts are sent to backend

3. **Generation Process:**
   - System uses modified prompts if changed
   - Falls back to defaults if unchanged
   - Appropriate prompt selected based on content type

## 🔧 API Structure

### GET `/api/prompts`
Returns all default prompt templates:
```json
{
  "mcq_generator": "Full MCQ generator template...",
  "mcq_formatter": "Full MCQ formatter template...",
  "nmcq_generator": "Full NMCQ generator template...",
  "nmcq_formatter": "Full NMCQ formatter template..."
}
```

### POST `/run`
Accepts custom prompts for all 4 templates:
```json
{
  "content_type": "MCQ",
  "generator_model": "Claude 4.5",
  "input_text": "...",
  "num_questions": 3,
  "focus_areas": "diagnosis",
  "temperature": 0.5,
  "top_p": 0.9,
  "custom_mcq_generator": "Modified MCQ generator prompt...",
  "custom_mcq_formatter": "Modified MCQ formatter prompt...",
  "custom_nmcq_generator": null,  // Using default
  "custom_nmcq_formatter": null   // Using default
}
```

## 💡 Usage Examples

### Example 1: Modify Only Generator
1. Expand "Prompt Templates" panel
2. Edit the MCQ Generator prompt to emphasize clinical reasoning
3. Leave other prompts unchanged
4. Generate content - only your modified generator will be used

### Example 2: Custom Formatting Style
1. Edit the MCQ Formatter prompt
2. Add instructions for specific formatting requirements
3. Generate content with custom formatting

### Example 3: Complete Customization
1. Modify all 4 prompts for your specific needs
2. Use "Reset All" button to restore defaults if needed
3. Individual reset buttons for selective restoration

## 🎨 Visual Features

### Professional Design Elements:
- **Gradient backgrounds** for elegant appearance
- **Icon integration** (📝, 🎨, 📋, 🖊️) for visual clarity
- **Smooth transitions** on all interactions
- **Hover effects** on cards and buttons
- **Rotating reset buttons** on hover
- **Color-coded sections** for easy navigation

### Responsive Design:
- Desktop: 2x2 grid for prompts
- Tablet: Adjusts to optimal layout
- Mobile: Single column layout

## 📋 Placeholders in Prompts

Generator prompts support these placeholders:
- `{{TEXT_TO_ANALYZE}}` - Input text content
- `{{NUM_QUESTIONS}}` - Number of questions to generate
- `{{FOCUS_AREAS}}` - Specific areas to focus on

Formatter prompts:
- Receive the generated content appended
- Process and format according to instructions

## 🧪 Testing the System

### Quick Test:
```bash
# Backend
cd backend
python app.py

# Frontend (new terminal)
cd frontend
npm run dev

# Visit http://localhost:3000
```

### Test Scenarios:

1. **Default Prompts Test**
   - Click "Prompt Templates" to expand
   - Verify all 4 prompts are loaded
   - Should see full template content

2. **Model Selection Test**
   - Select "Claude 4.5" → Maps to latest Claude
   - Select "Gemini 2.5" → Maps to latest Gemini

3. **Prompt Modification Test**
   - Edit any prompt
   - Generate content
   - Modified prompt should be used

4. **Reset Test**
   - Modify a prompt
   - Click individual reset (↻)
   - Prompt returns to default

## 🔒 Security & Performance

- Prompts are stored server-side
- Only differences from defaults are transmitted
- Efficient caching of default prompts
- Minimal network overhead

## 📊 Benefits

1. **Full Transparency** - Users see exactly what prompts are used
2. **Complete Control** - Every aspect of generation is customizable
3. **Educational** - Users learn from default prompts
4. **Flexibility** - Mix and match customizations
5. **Professional** - Enterprise-ready UI/UX

## 🎯 Summary

The system now provides:
✅ All 4 prompts visible and editable
✅ Default prompts pre-loaded
✅ Claude 4.5 and Gemini 2.5 support
✅ Professional, intuitive interface
✅ Individual and bulk reset options
✅ Responsive design for all devices
✅ Clear visual feedback
✅ Efficient API integration

Users have complete visibility and control over the entire content generation pipeline while maintaining a clean, professional interface.
