// API connector for Event Sonar
import { Event } from '../models/event';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api';
const ENABLE_MOCK_DATA = import.meta.env.VITE_ENABLE_MOCK_DATA === 'true';

/**
 * Fetches events from the API or falls back to mock data
 */
export async function fetchEvents(): Promise<Event[]> {
  if (ENABLE_MOCK_DATA) {
    // Import mock data if real API is not available
    const { mockEvents } = await import('../data/mockEvents');
    return mockEvents;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/events`);
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch events:', error);
    // Fall back to mock data on error
    const { mockEvents } = await import('../data/mockEvents');
    return mockEvents;
  }
}

/**
 * Sends voice data to the backend for processing
 */
export async function processVoiceCommand(audioBlob: Blob): Promise<{
  type: 'search' | 'filter' | 'navigate';
  payload: {
    query?: string;
    tags?: string[];
    eventId?: string;
  }
}> {
  if (ENABLE_MOCK_DATA) {
    // Mock response for testing
    return {
      type: 'search',
      payload: {
        query: 'music events',
      }
    };
  }

  try {
    const formData = new FormData();
    formData.append('audio', audioBlob);

    const response = await fetch(`${API_BASE_URL}/voice`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to process voice command:', error);
    // Return a default command on error
    return {
      type: 'search',
      payload: {
        query: '',
      }
    };
  }
}

/**
 * Gets detailed information about a specific event
 */
export async function getEventById(id: string): Promise<Event | null> {
  if (ENABLE_MOCK_DATA) {
    const { mockEvents } = await import('../data/mockEvents');
    return mockEvents.find(event => event.id === id) || null;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/events/${id}`);
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Failed to fetch event ${id}:`, error);
    return null;
  }
}
