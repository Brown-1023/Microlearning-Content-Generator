# Summary Bytes Feature Guide

This guide explains the new Summary Bytes content generation feature that creates clinical summaries following the same generator → formatter workflow.

## Overview

The Summary Bytes feature generates advanced board review summaries for Hematology and Oncology recertification exams. Each Summary Block consists of:
- A titled summary block focusing on specific clinical concepts
- High Yield Points: Concise, board-relevant bullet points (8-10 words each)
- Additional Concepts: Supporting principles and connections
- Key Insights: 2-3 sentence synthesis of the most important takeaways

## How It Works

### Workflow
1. **Generator** (Claude Sonnet 4.5 or Gemini 2.5 Pro) creates initial clinical vignettes with summaries
2. **Formatter** (Gemini 2.5 Flash) refines and standardizes the format
3. **Validator** ensures proper structure and completeness

### Content Type Selection

The system now supports three content types:
- **MCQ**: Multiple Choice Questions
- **Non-MCQ**: Clinical Vignettes with Q&A
- **Summary Bytes**: Clinical Summaries (NEW)

## Using Summary Bytes

### For All Users

1. **Select Content Type**
   - Choose "Summary Bytes" from the content type radio buttons
   - The interface shows three options: MCQ | Non-MCQ | Summary Bytes

2. **Configure Generation**
   - Select your generator model (Claude or Gemini Pro)
   - Set number of Summary Bytes to generate (1-20)
   - Optionally specify focus areas

3. **Generate Content**
   - Paste or type your educational content
   - Click "Generate Content"
   - Review the generated Summary Bytes

### For Administrators

Admins have additional capabilities:

1. **Customize Prompts**
   - Access the Prompt Templates panel
   - View and edit 6 prompts (including Summary generator and formatter)
   - Save custom prompts for your organization

2. **Advanced Settings**
   - Adjust temperature and top-p for both generator and formatter
   - Fine-tune output creativity and consistency

## Summary Bytes Format

Each Summary Block follows this structure:

```
1. Summary Block: [Title describing the clinical concept]
• High Yield Points:
  - [Concise board-relevant point with arrows --> for connections]
  - [Another key point, 8-10 words maximum]
  - [Additional points as needed]
• Additional Concepts:
  - [Supporting principle, 15-20 words]
  - [Related concept not covered in high yield points]
• Key Insights:
  [2-3 sentence paragraph synthesizing the most important clinical 
  takeaways and board-relevant information]
```

## Validation Rules

The Summary Bytes validator checks for:
- Presence of numbered "Summary Block:" header
- High Yield Points section with content
- Additional Concepts section (optional but recommended)
- Key Insights section with paragraph content
- Proper formatting and structure

## Example Output

```
1. Summary Block: Post-Diagnostic Workup: Uncovering the Underlying Cause
• High Yield Points:
  - Confirmed B12 deficiency --> investigate cause (e.g., PA, malabsorption)
  - Test for anti-IF antibodies to confirm Pernicious Anemia
  - Consider celiac disease or IBD testing if suspected
  - Dietary cause (veganism) --> oral supplementation sufficient
  - Malabsorptive cause --> parenteral or high-dose oral B12
  - Folate deficiency cause usually clear from history
  - Assess for concurrent iron deficiency, especially with malabsorption
• Additional Concepts:
  - The underlying cause dictates the route and duration of therapy
  - High-dose oral B12 (1000-2000 mcg) can be effective even in PA
  - The role of H. pylori testing is controversial and not routinely recommended
• Key Insights:
Once a vitamin B12 deficiency is confirmed, determining the underlying etiology 
is essential as it dictates the route (oral vs. parenteral) and duration 
(temporary vs. lifelong) of therapy. A systematic evaluation for pernicious 
anemia, gastrointestinal malabsorption (e.g., celiac disease, IBD), or dietary 
insufficiency is necessary to provide comprehensive care and address associated 
conditions.
```

## Prompt Customization

### Summary Generator Prompt
- Creates advanced board review summaries for Hematology/Oncology
- Generates high-yield points, additional concepts, and key insights
- Focuses on ABIM blueprint topics and clinical decision-making
- Uses a two-step process for thorough content generation

### Summary Formatter Prompt
- Reformats content to remove document references
- Ensures clean, professional presentation
- Structures output with proper sections and formatting
- Removes specified phrases to maintain authoritative tone

## API Usage

### Request Format
```json
{
  "content_type": "SUMMARY",
  "generator_model": "claude-sonnet-4-5-20250929",
  "input_text": "Your educational content here...",
  "num_questions": 3,
  "focus_areas": "diagnosis and management"
}
```

### Response Format
```json
{
  "success": true,
  "formatted_output": "Summary Byte 1:\n...",
  "validation_errors": [],
  "metadata": {
    "content_type": "SUMMARY",
    "num_questions": 3,
    "generator_model": "claude-sonnet-4-5-20250929",
    "total_time": 15.2
  }
}
```

## Testing

A test script is provided to verify the Summary Bytes feature:

```bash
# Set environment variables
export ADMIN_PASSWORD=your_admin_password

# Run the test script
python backend/test_summary_bytes.py
```

## Best Practices

1. **Input Content**
   - Provide comprehensive educational material
   - Include clinical details, pathophysiology, and management
   - The richer the input, the better the summaries

2. **Focus Areas**
   - Use specific focus areas like "diagnosis", "treatment", "complications"
   - Helps generate more targeted summaries

3. **Number of Summary Bytes**
   - Start with 2-5 for most content
   - Increase for longer, more comprehensive materials

4. **Review and Edit**
   - Always review generated content for clinical accuracy
   - Edit as needed before using in educational materials

## Troubleshooting

### No Summary Bytes Generated
- Check that input text has sufficient clinical content
- Ensure at least 50 characters of input text
- Verify model API keys are configured

### Validation Errors
- "Missing High Yield Points section" - Generator didn't create the High Yield Points
- "Missing Key Insights section" - Key Insights not properly formatted
- "Empty Key Insights content" - Key Insights paragraph is missing
- "No Summary Blocks found" - Content doesn't match expected format

### Poor Quality Output
- Adjust temperature settings (lower for more focused output)
- Provide more specific focus areas
- Ensure input content is clinically relevant

## Integration with Existing Features

- **Model Restrictions**: Admins can limit which models are available for Summary Bytes
- **Role-Based Access**: Same permissions apply as for MCQ/Non-MCQ
- **Prompt Management**: All 6 prompts manageable through admin panel
