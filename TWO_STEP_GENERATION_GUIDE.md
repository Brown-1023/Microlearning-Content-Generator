# Two-Step Content Generation Implementation Guide

## Overview

The content generation process has been updated to work in two distinct steps:
1. **Generate Draft** - Creates the initial draft with token-by-token streaming
2. **Format Draft** - Formats the draft into final output with token-by-token streaming

## How It Works

### Step 1: Generate Draft
When the user clicks "Generate Content":
- The system calls `/run/stream/draft` endpoint
- Draft is generated token-by-token and displayed in real-time
- A "Format Draft" button appears after draft generation completes

### Step 2: Format Draft  
When the user clicks "Format Draft":
- The system calls `/run/stream/format` endpoint
- Draft is formatted token-by-token and displayed in real-time
- Validation is performed and final output is shown

## Backend Changes

### New Endpoints

1. **`POST /run/stream/draft`**
   - Generates only the initial draft
   - Streams tokens in real-time
   - Returns draft content without formatting

2. **`POST /run/stream/format`**
   - Formats a provided draft
   - Streams formatted tokens in real-time
   - Performs validation and returns final output

### Pipeline Methods

Added in `backend/pipeline.py`:
- `run_stream_draft_only()` - Handles draft generation with streaming
- `run_stream_format_only()` - Handles formatting with streaming

## Frontend Changes

### Service Methods

Added in `frontend/services/generation.ts`:
- `generateDraftStream()` - Calls draft endpoint
- `formatDraftStream()` - Calls format endpoint

### UI Updates

In `frontend/pages/index.tsx`:
- `handleGenerate()` - Now only generates draft
- `handleFormatDraft()` - New function to format the draft

In `frontend/components/StreamingOutputPanel.tsx`:
- Added "Format Draft" button that appears after draft generation
- Button has a pulsing animation to draw attention
- Both draft and formatted content show with streaming cursor

### Visual Features

- **Draft Section**: Shows generated draft with copy/download options
- **Format Draft Button**: Prominent purple gradient button with pulse animation
- **Formatted Section**: Shows formatted content during formatting
- **Streaming Cursor**: Blinking cursor shows live generation progress

## User Flow

1. User fills in the form and clicks "Generate Content"
2. System generates draft (token-by-token streaming)
3. Draft is displayed with "Format Draft" button
4. User reviews draft and clicks "Format Draft"
5. System formats the draft (token-by-token streaming)
6. Final formatted output is displayed with validation results

## Benefits

- **Better User Control**: Users can review draft before formatting
- **Improved Transparency**: Users see each step of the process
- **Flexibility**: Users can copy/save draft before formatting
- **Better Error Recovery**: If formatting fails, draft is still available
- **Educational**: Users can see how AI transforms draft to final output

## Testing

To test the implementation:

1. Start the backend:
```bash
cd backend
python run.py
```

2. Start the frontend:
```bash
cd frontend
npm run dev
```

3. Test the flow:
   - Enter text and click "Generate Content"
   - Watch the draft stream in token-by-token
   - Click "Format Draft" when it appears
   - Watch the formatting happen token-by-token
   - Verify final output shows correctly

## Deployment Notes

No special deployment requirements. The changes are compatible with existing infrastructure:
- Cloud Run handles streaming endpoints automatically
- Vercel supports Server-Sent Events for streaming
- All environment variables remain the same

## CSS Styling

Added new styles in `frontend/styles/globals.css`:
- `.draft-section` - Container for draft content
- `.draft-actions` - Button container with flex layout
- `.btn-primary` - Gradient purple button with pulse animation
- `.streaming-content` - Styled container for streaming text
- `.cursor-blink` - Animated cursor for live generation

## Known Limitations

- Draft must complete before formatting can begin
- Both steps are required (no skip option currently)
- Large drafts may take time to format

## Future Enhancements

- Add option to skip formatting for simple content
- Allow editing draft before formatting
- Add progress percentage for each step
- Save draft/formatted pairs for comparison
- Add regenerate options for each step
