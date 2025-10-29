# Streaming Implementation Guide

## Overview
The application now supports real-time streaming of content generation progress using Server-Sent Events (SSE). This provides users with immediate feedback on the generation process, showing progress through each stage of the pipeline.

## Features

### Real-time Progress Updates
- **Stage Indicators**: Shows which stage of the pipeline is currently executing
- **Progress Bar**: Visual progress indicator from 0-100%
- **Stage Messages**: Descriptive messages for each stage
- **Draft Preview**: Shows initial draft content before formatting

### Pipeline Stages
1. **Load Prompts** (10%): Loading prompt templates
2. **Generator** (30-50%): Generating initial content using AI
3. **Formatter** (60%): Formatting content according to requirements
4. **Validator** (80%): Validating the formatted content
5. **Retry** (85-95%): Retry attempts if validation fails
6. **Done/Fail** (100%): Final completion status

## Backend Implementation

### New Streaming Endpoint
```
POST /run/stream
```
- Returns Server-Sent Events (SSE) stream
- Sends progress updates at each pipeline stage
- Includes draft content after generation
- Final event contains complete result

### Pipeline Changes
- Added `run_stream()` async method to ContentPipeline
- Yields progress events at each node execution
- Non-blocking execution using asyncio thread pool
- Maintains backward compatibility with synchronous `run()` method

### Event Format
```javascript
event: progress
data: {
  "stage": "generator",
  "message": "Generating content using claude-sonnet-3.5...",
  "progress": 30
}

event: draft
data: {
  "stage": "generator",
  "message": "Initial draft generated",
  "progress": 50,
  "draft": "..."
}

event: complete
data: {
  "success": true,
  "output": "...",
  "metadata": {...}
}
```

## Frontend Implementation

### Streaming Service
The `generationService` now includes:
- `generateContentStream()`: Handles SSE connection and parsing
- Event callbacks for progress, draft, complete, and error events
- Automatic reconnection and error handling

### UI Components

#### StreamingOutputPanel
New component that displays:
- Real-time progress bar with stage icons
- Draft content preview section
- Final output with metadata
- Copy and download buttons for both draft and final output

#### Streaming Mode Toggle
- Users can choose between streaming and traditional modes
- Streaming mode (default): Real-time progress updates
- Traditional mode: Wait for complete response

### Usage Example
```typescript
await generationService.generateContentStream(params, {
  onProgress: (data) => {
    // Update progress UI
    setStreamProgress(data);
  },
  onDraft: (draft) => {
    // Show draft content
    setStreamDraft(draft);
  },
  onComplete: (result) => {
    // Display final result
    setOutput(result);
  },
  onError: (error) => {
    // Handle errors
    showToast(error, 'error');
  }
});
```

## Installation

### Backend
```bash
# Install new dependency
pip install sse-starlette

# Or using requirements.txt
pip install -r backend/requirements.txt
```

### Frontend
No additional dependencies required - uses native browser EventSource API with fetch fallback.

## Testing

### Backend Test Script
```bash
# Run the test script
cd backend
python test_streaming.py
```

### Manual Testing
1. Start the backend server:
   ```bash
   cd backend
   python run.py
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Login to the application
4. Ensure "Streaming Mode" is enabled (checkbox)
5. Submit a generation request
6. Observe real-time progress updates

## Performance Considerations

### Benefits
- **Immediate Feedback**: Users see progress immediately
- **Better UX**: No long wait times without feedback
- **Draft Preview**: Users can see initial content before formatting
- **Error Recovery**: Failed stages are clearly indicated

### Trade-offs
- **Slightly Higher Bandwidth**: SSE connection remains open longer
- **Browser Compatibility**: Requires modern browser with SSE support
- **Connection Stability**: May need reconnection logic for unstable connections

## Troubleshooting

### Common Issues

1. **No Progress Updates**
   - Check if streaming mode is enabled
   - Verify SSE endpoint is accessible
   - Check browser console for errors

2. **Connection Drops**
   - The frontend will attempt to reconnect automatically
   - Check network stability
   - Verify server timeout settings

3. **Authentication Errors**
   - Ensure JWT token is being sent with streaming requests
   - Check token expiration

### Debug Mode
Enable debug logging in browser console:
```javascript
// In browser console
localStorage.setItem('DEBUG_STREAMING', 'true');
```

## Future Enhancements

1. **WebSocket Support**: For bidirectional communication
2. **Partial Results**: Stream content as it's generated
3. **Cancel Operations**: Allow users to cancel ongoing generation
4. **Progress Persistence**: Save progress for resumable operations
5. **Multiple Concurrent Streams**: Support multiple generation requests

## API Reference

### Backend

#### `POST /run/stream`
Streaming endpoint for content generation.

**Request Body**: Same as `/run` endpoint
**Response**: Server-Sent Events stream
**Authentication**: Required (JWT Bearer token)

### Frontend

#### `generationService.generateContentStream(params, callbacks)`
Initiates streaming content generation.

**Parameters**:
- `params`: Generation parameters (same as non-streaming)
- `callbacks`: Object with event handlers
  - `onProgress(data)`: Progress updates
  - `onDraft(draft)`: Draft content available
  - `onComplete(result)`: Final result
  - `onError(error)`: Error handler

**Returns**: Promise<void>

## Migration Guide

### From Non-Streaming to Streaming

1. Backend: No changes required - both endpoints coexist
2. Frontend: Replace `generateContent()` with `generateContentStream()`
3. UI: Add progress display components

### Backward Compatibility
- Original `/run` endpoint remains unchanged
- Users can toggle between streaming and non-streaming modes
- No breaking changes to existing API contracts
