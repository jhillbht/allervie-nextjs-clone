import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';
import { mockAdGroups } from '@/lib/mock-data';

// Define the base URL for the Flask backend API
const BACKEND_API_URL = process.env.BACKEND_API_URL || 'http://localhost:5002';

/**
 * Handler for GET requests to /api/google-ads/ad_groups
 * 
 * This endpoint fetches ad group data from the Google Ads API via the Flask backend.
 * It supports filtering by campaign_id and falls back to mock data if the API request fails.
 */
export async function GET(request: NextRequest): Promise<NextResponse> {
  // Extract query parameters
  const searchParams = request.nextUrl.searchParams;
  const campaignId = searchParams.get('campaign_id');
  const useMock = searchParams.get('use_mock') === 'true';
  
  if (useMock) {
    console.log('Using mock ad group data (forced)');
    // If a campaign ID is provided, filter the mock data
    const filteredData = campaignId 
      ? mockAdGroups.filter(group => group.campaign_id === campaignId)
      : mockAdGroups;
    return NextResponse.json(filteredData);
  }
  
  // Build query parameters for the backend API
  const params: Record<string, string> = {};
  if (campaignId) params.campaign_id = campaignId;
  
  try {
    console.log(`Requesting Google Ads ad group data from ${BACKEND_API_URL}/api/google-ads/ad_groups`);
    
    // Make a request to the backend API
    const response = await axios.get(`${BACKEND_API_URL}/api/google-ads/ad_groups`, {
      params,
      headers: {
        Authorization: request.headers.get('Authorization') || '',
      },
    });
    
    console.log('Successfully fetched Google Ads ad group data');
    return NextResponse.json(response.data);
  } catch (error) {
    console.error('Error fetching Google Ads ad group data:', error);
    
    // Fall back to mock data, applying the same filtering
    console.log('Falling back to mock ad group data');
    const filteredData = campaignId 
      ? mockAdGroups.filter(group => group.campaign_id === campaignId)
      : mockAdGroups;
    return NextResponse.json(filteredData);
  }
}
