'use client';

import { useState, useEffect } from 'react';
import { getAdsPerformance, AdsPerformanceData } from '@/lib/google-ads-client';
import MetricCard from './MetricCard';
import { Card } from '@/components/ui/card';
import { subDays, format } from 'date-fns';
import { RefreshCw } from 'lucide-react';

interface GoogleAdsPerformanceProps {
  initialData?: AdsPerformanceData;
  refreshInterval?: number; // In milliseconds
}

export default function GoogleAdsPerformance({
  initialData,
  refreshInterval = 0, // 0 means no auto-refresh
}: GoogleAdsPerformanceProps) {
  const [performanceData, setPerformanceData] = useState<AdsPerformanceData | null>(
    initialData || null
  );
  const [isLoading, setIsLoading] = useState<boolean>(!initialData);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>(
    format(new Date(), 'MMM d, yyyy h:mm a')
  );
  
  // Calculate default date range (last 30 days)
  const today = new Date();
  const startDate = format(subDays(today, 30), 'yyyy-MM-dd');
  const endDate = format(subDays(today, 1), 'yyyy-MM-dd'); // Yesterday
  
  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await getAdsPerformance(startDate, endDate, true);
      setPerformanceData(data);
      setLastUpdated(format(new Date(), 'MMM d, yyyy h:mm a'));
    } catch (err) {
      console.error('Error fetching Google Ads performance data:', err);
      setError('Failed to load Google Ads performance data. Please try again.');
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
  
  if (isLoading && !performanceData) {
    return (
      <Card className="p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Google Ads Performance</h2>
        </div>
        <div className="grid grid-cols-1 gap-4 animate-pulse">
          <div className="h-24 bg-gray-200 rounded"></div>
          <div className="h-24 bg-gray-200 rounded"></div>
        </div>
      </Card>
    );
  }
  
  if (error) {
    return (
      <Card className="p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Google Ads Performance</h2>
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
        <h2 className="text-xl font-bold">Google Ads Performance</h2>
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
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {performanceData && (
          <>
            <MetricCard
              title="Impressions"
              metric={performanceData.impressions}
            />
            <MetricCard
              title="Clicks"
              metric={performanceData.clicks}
            />
            <MetricCard
              title="Conversions"
              metric={performanceData.conversions}
            />
            <MetricCard
              title="Cost"
              metric={performanceData.cost}
              prefix="$"
              decimals={2}
            />
            <MetricCard
              title="Click-Through Rate"
              metric={performanceData.clickThroughRate}
              suffix="%"
              decimals={2}
            />
            <MetricCard
              title="Conversion Rate"
              metric={performanceData.conversionRate}
              suffix="%"
              decimals={2}
            />
            <MetricCard
              title="Cost Per Conversion"
              metric={performanceData.costPerConversion}
              prefix="$"
              decimals={2}
              inverseColors
            />
          </>
        )}
      </div>
      
      <div className="mt-4 text-sm text-gray-500">
        <p>Period: {startDate} to {endDate}</p>
      </div>
    </Card>
  );
}
