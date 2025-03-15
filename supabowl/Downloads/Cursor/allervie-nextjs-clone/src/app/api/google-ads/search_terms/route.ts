import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';
import { mockSearchTerms } from '@/lib/mock-data';

// Define the base URL for the Flask backend API
const BACKEND_API_URL = process.env.BACKEND_API_URL || 'http://localhost:5002';

/**
 * Handler for GET requests to /api/google-ads/search_terms
 * 
 * This endpoint fetches search term data from the Google Ads API via the Flask backend.
 * It supports filtering by campaign_id and falls back to mock data if the API request fails.
 */
export async function GET(request: NextRequest): Promise<NextResponse> {
  // Extract query parameters
  const searchParams = request.nextUrl.searchParams;
  const campaignId = searchParams.get('campaign_id');
  const useMock = searchParams.get('use_mock') === 'true';
  
  if (useMock) {
    console.log('Using mock search term data (forced)');
    // If a campaign ID is provided, filter the mock data
    const filteredData = campaignId 
      ? mockSearchTerms.filter(term => term.campaign_id === campaignId)
      : mockSearchTerms;
    return NextResponse.json(filteredData);
  }
  
  // Build query parameters for the backend API
  const params: Record<string, string> = {};
  if (campaignId) params.campaign_id = campaignId;
  
  try {
    console.log(`Requesting Google Ads search term data from ${BACKEND_API_URL}/api/google-ads/search_terms`);
    
    // Make a request to the backend API
    const response = await axios.get(`${BACKEND_API_URL}/api/google-ads/search_terms`, {
      params,
      headers: {
        Authorization: request.headers.get('Authorization') || '',
      },
    });
    
    console.log('Successfully fetched Google Ads search term data');
    return NextResponse.json(response.data);
  } catch (error) {
    console.error('Error fetching Google Ads search term data:', error);
    
    // Fall back to mock data, applying the same filtering
    console.log('Falling back to mock search term data');
    const filteredData = campaignId 
      ? mockSearchTerms.filter(term => term.campaign_id === campaignId)
      : mockSearchTerms;
    return NextResponse.json(filteredData);
  }
}
