'use client';

import { useState, useEffect } from 'react';
import { getAdsCampaigns, CampaignData } from '@/lib/google-ads-client';
import { Card } from '@/components/ui/card';
import { RefreshCw } from 'lucide-react';
import { format } from 'date-fns';

interface GoogleAdsCampaignsProps {
  initialData?: CampaignData[];
  refreshInterval?: number; // In milliseconds
}

export default function GoogleAdsCampaigns({
  initialData,
  refreshInterval = 0, // 0 means no auto-refresh
}: GoogleAdsCampaignsProps) {
  const [campaignData, setCampaignData] = useState<CampaignData[] | null>(
    initialData || null
  );
  const [isLoading, setIsLoading] = useState<boolean>(!initialData);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>(
    format(new Date(), 'MMM d, yyyy h:mm a')
  );
  
  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await getAdsCampaigns();
      setCampaignData(data);
      setLastUpdated(format(new Date(), 'MMM d, yyyy h:mm a'));
    } catch (err) {
      console.error('Error fetching Google Ads campaign data:', err);
      setError('Failed to load Google Ads campaign data. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Fetch data on component mount if not provided
  useEffect(() => {
    if (!initialData) {
      fetchData();
    }
    
    // Set up auto-refresh if interval is provided
    if (refreshInterval > 0) {
      const intervalId = setInterval(fetchData, refreshInterval);
      
      // Clean up interval on component unmount
      return () => clearInterval(intervalId);
    }
  }, [initialData, refreshInterval]);
  
  const handleRefresh = () => {
    fetchData();
  };
  
  if (isLoading && !campaignData) {
    return (
      <Card className="p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Google Ads Campaigns</h2>
        </div>
        <div className="animate-pulse">
          <div className="h-10 bg-gray-200 rounded mb-4"></div>
          <div className="h-20 bg-gray-200 rounded"></div>
        </div>
      </Card>
    );
  }
  
  if (error) {
    return (
      <Card className="p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Google Ads Campaigns</h2>
          <button 
            onClick={handleRefresh}
            className="flex items-center space-x-1 text-sm text-blue-600 hover:text-blue-800"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Retry</span>
          </button>
        </div>
        <div className="text-red-500">{error}</div>
      </Card>
    );
  }
  
  return (
    <Card className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Google Ads Campaigns</h2>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-500">
            Last updated: {lastUpdated}
          </div>
          <button 
            onClick={handleRefresh}
            className="flex items-center space-x-1 text-sm text-blue-600 hover:text-blue-800"
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>
      
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Campaign
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Impressions
              </th>
              <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Clicks
              </th>
              <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Conversions
              </th>
              <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Cost
              </th>
              <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                CTR
              </th>
              <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Conv. Rate
              </th>
              <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Cost/Conv.
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {campaignData && campaignData.map((campaign) => (
              <tr key={campaign.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{campaign.name}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    campaign.status === 'ENABLED' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {campaign.status === 'ENABLED' ? 'Active' : 'Paused'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                  {campaign.impressions.toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                  {campaign.clicks.toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                  {campaign.conversions.toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                  ${campaign.cost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                  {campaign.ctr.toFixed(2)}%
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                  {campaign.conversion_rate.toFixed(2)}%
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                  ${campaign.costPerConversion.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </td>
              </tr>
            ))}
            {campaignData && campaignData.length === 0 && (
              <tr>
                <td colSpan={9} className="px-6 py-4 text-center text-sm text-gray-500">
                  No campaign data available
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
