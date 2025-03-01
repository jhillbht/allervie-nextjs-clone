# Backend Integration Plan

This document outlines the integration plan for connecting the Event Harmony Browser frontend with backend services.

## API Endpoints

The frontend expects the following API endpoints:

### Events API

```
GET /api/events
```

Returns a list of events with the following structure:

```typescript
interface Event {
  id: string;
  title: string;
  description: string;
  location: string;
  startTime: string;
  endTime: string;
  tags: string[];
  image?: string;
  energy?: number; // 1-100 scale
  informativeness?: number; // 1-100 scale
}
```

### Voice API

```
POST /api/voice
```

Accepts audio data and returns a command interpretation:

```typescript
interface VoiceCommand {
  type: 'search' | 'filter' | 'navigate';
  payload: {
    query?: string;
    tags?: string[];
    eventId?: string;
  }
}
```

## Integration Points

1. **Event Data Fetching**
   - The frontend currently uses mock data in `src/data/mockEvents.ts`
   - This should be replaced with API calls to the backend

2. **Voice Command Processing**
   - The microphone button in the UI should send audio to the backend
   - Backend would process this with a speech-to-text service
   - Return structured commands for the frontend to execute

3. **Authentication**
   - Future enhancement: Add user authentication
   - JWT-based auth with secure cookies

## Environment Configuration

Create a `.env` file in the frontend directory with:

```
VITE_API_BASE_URL=http://localhost:3000/api
VITE_ENABLE_VOICE=true
```

## Next Steps

1. Implement a basic Node.js backend with Express
2. Create API routes for event data
3. Add speech processing capabilities
4. Deploy backend to cloud platform
5. Connect frontend to deployed backend
