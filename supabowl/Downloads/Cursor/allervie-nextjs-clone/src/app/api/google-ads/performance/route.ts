import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';
import { mockAdsPerformance } from '@/lib/mock-data';

// Define the base URL for the Flask backend API
const BACKEND_API_URL = process.env.BACKEND_API_URL || 'http://localhost:5002';

/**
 * Handler for GET requests to /api/google-ads/performance
 * 
 * This endpoint proxies requests to the Flask backend API and falls back to mock data if needed.
 * It supports query parameters for date ranges and previous period comparison.
 */
export async function GET(request: NextRequest): Promise<NextResponse> {
  // Extract query parameters
  const searchParams = request.nextUrl.searchParams;
  const startDate = searchParams.get('start_date');
  const endDate = searchParams.get('end_date');
  const previousPeriod = searchParams.get('previous_period') === 'true';
  
  // Get use_mock parameter to determine if we should force using mock data
  const useMock = searchParams.get('use_mock') === 'true';
  
  // If using mock data, return it immediately
  if (useMock) {
    console.log('Using mock Google Ads performance data (forced)');
    return NextResponse.json(mockAdsPerformance);
  }
  
  // Build query parameters for the backend API
  const params: Record<string, string> = {};
  if (startDate) params.start_date = startDate;
  if (endDate) params.end_date = endDate;
  if (previousPeriod) params.previous_period = 'true';
  
  try {
    console.log(`Requesting Google Ads performance data from ${BACKEND_API_URL}/api/google-ads/performance`);
    
    // Make a request to the backend API
    const response = await axios.get(`${BACKEND_API_URL}/api/google-ads/performance`, { 
      params,
      // Pass along any authorization headers
      headers: {
        Authorization: request.headers.get('Authorization') || '',
      },
    });
    
    console.log('Successfully fetched Google Ads performance data from backend API');
    return NextResponse.json(response.data);
  } catch (error) {
    console.error('Error fetching Google Ads performance data from API:', error);
    
    // Fall back to mock data
    console.log('Falling back to mock Google Ads performance data');
    return NextResponse.json(mockAdsPerformance);
  }
}
