import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';
import { mockCampaigns } from '@/lib/mock-data';

// Define the base URL for the Flask backend API
const BACKEND_API_URL = process.env.BACKEND_API_URL || 'http://localhost:5002';

/**
 * Handler for GET requests to /api/google-ads/campaigns
 * 
 * This endpoint fetches campaign data from the Google Ads API via the Flask backend.
 * It falls back to mock data if the API request fails.
 */
export async function GET(request: NextRequest): Promise<NextResponse> {
  // Check if we should force using mock data
  const useMock = request.nextUrl.searchParams.get('use_mock') === 'true';
  
  if (useMock) {
    console.log('Using mock campaign data (forced)');
    return NextResponse.json(mockCampaigns);
  }
  
  try {
    console.log(`Requesting Google Ads campaign data from ${BACKEND_API_URL}/api/google-ads/campaigns`);
    
    // Make a request to the backend API
    const response = await axios.get(`${BACKEND_API_URL}/api/google-ads/campaigns`, {
      headers: {
        Authorization: request.headers.get('Authorization') || '',
      },
    });
    
    console.log('Successfully fetched Google Ads campaign data');
    return NextResponse.json(response.data);
  } catch (error) {
    console.error('Error fetching Google Ads campaign data:', error);
    
    // Fall back to mock data
    console.log('Falling back to mock campaign data');
    return NextResponse.json(mockCampaigns);
  }
}
