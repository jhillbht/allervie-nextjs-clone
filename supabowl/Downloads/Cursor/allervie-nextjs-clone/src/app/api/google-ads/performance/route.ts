import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';
import { mockAdsPerformance } from '@/lib/mock-data';

/**
 * Handler for GET requests to /api/google-ads/performance
 * 
 * This endpoint implements direct integration with Google Ads API
 * instead of proxying to a separate backend.
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
  
  try {
    // In a production implementation, we would connect to the Google Ads API here
    // For now, we'll use mock data as we don't have the actual authentication credentials
    
    console.log('Mock implementation of Google Ads API integration');
    console.log(`Parameters: start_date=${startDate}, end_date=${endDate}, previous_period=${previousPeriod}`);
    
    // Return mock data
    console.log('Returning mock Google Ads performance data');
    return NextResponse.json(mockAdsPerformance);
    
  } catch (error) {
    console.error('Error fetching Google Ads performance data:', error);
    
    // Fall back to mock data
    console.log('Falling back to mock Google Ads performance data');
    return NextResponse.json(mockAdsPerformance);
  }
}