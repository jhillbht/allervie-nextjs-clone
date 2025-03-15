'use client';

import { useState } from 'react';
import GoogleAdsPerformance from '@/components/dashboard/GoogleAdsPerformance';
import GoogleAdsCampaigns from '@/components/dashboard/GoogleAdsCampaigns';
import { Card } from '@/components/ui/card';
import { RefreshCw } from 'lucide-react';

export default function DashboardPage() {
  const [refreshKey, setRefreshKey] = useState<number>(0);
  
  const handleRefreshAll = () => {
    // Increment the key to force a re-render of all components
    setRefreshKey(prev => prev + 1);
  };
  
  return (
    <div className="container mx-auto py-8 px-4">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Allervie Analytics Dashboard</h1>
        
        <button 
          onClick={handleRefreshAll}
          className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
        >
          <RefreshCw className="h-5 w-5" />
          <span>Refresh All</span>
        </button>
      </div>
      
      <div className="grid grid-cols-1 gap-8">
        {/* Google Ads Performance Metrics */}
        <GoogleAdsPerformance key={`performance-${refreshKey}`} />
        
        {/* Google Ads Campaigns */}
        <GoogleAdsCampaigns key={`campaigns-${refreshKey}`} />
        
        {/* Additional widgets can be added here */}
        <Card className="p-6">
          <h2 className="text-xl font-bold mb-4">Coming Soon: Google Analytics 4 Integration</h2>
          <p className="text-gray-600">
            GA4 data integration is planned for the next phase of development. 
            This will include user behavior metrics, conversion funnels, and audience insights.
          </p>
        </Card>
      </div>
    </div>
  );
}
