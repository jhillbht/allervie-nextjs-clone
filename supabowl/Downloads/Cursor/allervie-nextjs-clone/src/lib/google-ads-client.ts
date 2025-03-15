import axios from 'axios';
import { mockAdsPerformance } from './mock-data';

// Define the types for our Google Ads performance data
export interface MetricWithChange {
  value: number;
  change: number;
}

export interface AdsPerformanceData {
  impressions: MetricWithChange;
  clicks: MetricWithChange;
  conversions: MetricWithChange;
  cost: MetricWithChange;
  clickThroughRate: MetricWithChange;
  conversionRate: MetricWithChange;
  costPerConversion: MetricWithChange;
}

export interface CampaignData {
  id: string;
  name: string;
  status: string;
  impressions: number;
  clicks: number;
  conversions: number;
  cost: number;
  ctr: number;
  conversion_rate: number;
  costPerConversion: number;
}

export interface AdGroupData {
  id: string;
  name: string;
  campaign_id: string;
  campaign_name: string;
  status: string;
  impressions: number;
  clicks: number;
  conversions: number;
  cost: number;
  ctr: number;
  conversion_rate: number;
  costPerConversion: number;
}

export interface SearchTermData {
  search_term: string;
  campaign_id: string;
  campaign_name: string;
  match_type: string;
  impressions: number;
  clicks: number;
  conversions: number;
  cost: number;
  ctr: number;
  conversion_rate: number;
  costPerConversion: number;
}

// Define the base URL for API requests
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? process.env.NEXT_PUBLIC_API_URL || 'https://allervie-api.production.com' 
  : 'http://localhost:5002';

// Create an axios instance with default configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

/**
 * Fetches Google Ads performance data from the API
 * 
 * @param startDate - Start date in YYYY-MM-DD format (optional)
 * @param endDate - End date in YYYY-MM-DD format (optional)
 * @param previousPeriod - Whether to include data from the previous period for comparison (optional)
 * @param useMockData - Whether to use mock data instead of making an API call (optional)
 * @returns Promise resolving to the performance data
 */
export async function getAdsPerformance(
  startDate?: string,
  endDate?: string,
  previousPeriod: boolean = true,
  useMockData: boolean = false
): Promise<AdsPerformanceData> {
  // If using mock data, return it immediately
  if (useMockData) {
    console.log('Using mock Google Ads performance data');
    return mockAdsPerformance;
  }

  // Build query parameters
  const params: Record<string, string> = {};
  if (startDate) params.start_date = startDate;
  if (endDate) params.end_date = endDate;
  if (previousPeriod) params.previous_period = 'true';

  try {
    console.log('Fetching Google Ads performance data from API');
    
    // Make the API request
    const response = await api.get('/api/google-ads/performance', { params });
    
    return response.data;
  } catch (error) {
    console.error('Error fetching Google Ads performance data:', error);
    
    // Fall back to mock data if the API request fails
    console.log('Falling back to mock Google Ads performance data');
    return mockAdsPerformance;
  }
}

/**
 * Fetches Google Ads campaign data
 */
export async function getAdsCampaigns(
  useMockData: boolean = false
): Promise<CampaignData[]> {
  if (useMockData) {
    return import('./mock-data').then(module => module.mockCampaigns);
  }

  try {
    const response = await api.get('/api/google-ads/campaigns');
    return response.data;
  } catch (error) {
    console.error('Error fetching campaign data:', error);
    return import('./mock-data').then(module => module.mockCampaigns);
  }
}

/**
 * Fetches Google Ads ad group data
 */
export async function getAdsAdGroups(
  campaignId?: string,
  useMockData: boolean = false
): Promise<AdGroupData[]> {
  if (useMockData) {
    const { mockAdGroups } = await import('./mock-data');
    return campaignId 
      ? mockAdGroups.filter(group => group.campaign_id === campaignId)
      : mockAdGroups;
  }

  try {
    const params = campaignId ? { campaign_id: campaignId } : {};
    const response = await api.get('/api/google-ads/ad_groups', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching ad group data:', error);
    const { mockAdGroups } = await import('./mock-data');
    return campaignId 
      ? mockAdGroups.filter(group => group.campaign_id === campaignId)
      : mockAdGroups;
  }
}

/**
 * Fetches Google Ads search term data
 */
export async function getAdsSearchTerms(
  campaignId?: string,
  useMockData: boolean = false
): Promise<SearchTermData[]> {
  if (useMockData) {
    const { mockSearchTerms } = await import('./mock-data');
    return campaignId 
      ? mockSearchTerms.filter(term => term.campaign_id === campaignId)
      : mockSearchTerms;
  }

  try {
    const params = campaignId ? { campaign_id: campaignId } : {};
    const response = await api.get('/api/google-ads/search_terms', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching search term data:', error);
    const { mockSearchTerms } = await import('./mock-data');
    return campaignId 
      ? mockSearchTerms.filter(term => term.campaign_id === campaignId)
      : mockSearchTerms;
  }
}
