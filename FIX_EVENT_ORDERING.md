# Fix: Event Ordering in Streaming to Prevent Token Loss

## Problem
When multiple streaming events arrive at the same timestamp (in the same network chunk), the completion events (`draft_complete`, `format_complete`) were being processed before all token events. This caused the frontend to stop accepting tokens prematurely, resulting in missing content at the end.

### Example Issue
```
23:26:33.244 - draft_token: "the in"
23:26:33.244 - draft_token: "dolent nature of loc"
23:26:33.244 - draft_token: "alized disease."
23:26:33.244 - draft_token: "\n</summary>"
23:26:33.244 - draft_complete: {...}
```

When these events arrive simultaneously, if `draft_complete` is processed first, it sets `isStreaming = false`, causing subsequent tokens to be ignored.

## Solution

### 1. Event Collection and Prioritization
Instead of processing events immediately as they're parsed, we:
1. Collect all events from a chunk into an array
2. Sort them by priority (tokens first, completion last)
3. Process them in the correct order

### 2. Priority System
```javascript
const priority: Record<string, number> = {
  'draft_token': 1,        // Process first
  'formatted_token': 1,    // Process first
  'progress': 2,           // Process second
  'keepalive': 3,          // Process third
  'ping': 3,               // Process third
  'draft_complete': 4,     // Process fourth
  'format_complete': 4,    // Process fourth
  'complete': 4,           // Process fourth
  'error': 5               // Process last
};
```

### 3. Completion Delay
Added a small delay (10ms) before processing completion events to ensure all tokens are rendered in the UI:
```javascript
case 'draft_complete':
  await new Promise(resolve => setTimeout(resolve, 10));
  callbacks.onComplete?.(event.data);
  break;
```

## Files Updated

### `frontend/services/generation.ts`

Updated 4 streaming methods:
1. `generateDraftStream()` 
2. `formatDraftStream()`
3. `generateContentStream()`
4. `reformatContentStream()`

Each method now:
- Collects events in batches
- Sorts by priority
- Processes tokens before completions
- Handles final buffer with same logic

## Implementation Example

### Before (Problem)
```javascript
for (const line of lines) {
  // Process immediately as parsed
  switch (eventType) {
    case 'draft_token':
      callbacks.onDraftToken?.(token);
      break;
    case 'draft_complete':
      callbacks.onComplete?.(data); // Sets isStreaming = false
      break;
  }
}
```

### After (Solution)
```javascript
// Collect all events
const events = [];
for (const line of lines) {
  events.push({ type: eventType, data: parsedData });
}

// Sort by priority (tokens first)
const sortedEvents = events.sort((a, b) => {
  return priority[a.type] - priority[b.type];
});

// Process in order
for (const event of sortedEvents) {
  switch (event.type) {
    case 'draft_token':
      callbacks.onDraftToken?.(event.data.token);
      break;
    case 'draft_complete':
      await new Promise(resolve => setTimeout(resolve, 10));
      callbacks.onComplete?.(event.data);
      break;
  }
}
```

## Impact

1. **No Token Loss**: All tokens are processed before completion
2. **Complete Content**: Users receive all generated text
3. **Proper State Management**: `isStreaming` flag set at the right time
4. **Better Reliability**: Handles simultaneous events correctly

## Testing

To verify the fix:
1. Generate content and watch the console
2. Look for events with the same timestamp
3. Verify all tokens appear in the UI
4. Check that the last part of content is not missing
5. Try with both short and long content generation

## Technical Details

The issue specifically affected:
- Events arriving in the same network packet
- High-speed connections where multiple events batch together
- The final burst of tokens before completion
- Both draft and formatted content streaming

The fix ensures proper event ordering regardless of network timing.
