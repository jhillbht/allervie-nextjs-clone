import { Card } from '@/components/ui/card';
import { MetricWithChange } from '@/lib/google-ads-client';
import { ArrowUpIcon, ArrowDownIcon, MinusIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  metric: MetricWithChange;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  inverseColors?: boolean;
  className?: string;
}

export default function MetricCard({
  title,
  metric,
  prefix = '',
  suffix = '',
  decimals = 0,
  inverseColors = false,
  className = '',
}: MetricCardProps) {
  const { value, change } = metric;
  
  // Format the value based on the type and decimals
  let formattedValue: string;
  if (typeof value === 'number') {
    formattedValue = value.toLocaleString(undefined, {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  } else {
    formattedValue = 'N/A';
  }
  
  // Determine if the change is positive, negative, or neutral
  let changeType: 'positive' | 'negative' | 'neutral' = 'neutral';
  if (typeof change === 'number') {
    changeType = change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral';
    // If inverseColors is true, reverse the positive/negative logic (e.g., for metrics like bounce rate)
    if (inverseColors) {
      changeType = changeType === 'positive' ? 'negative' : changeType === 'negative' ? 'positive' : 'neutral';
    }
  }
  
  // Format the change percentage
  const formattedChange = typeof change === 'number'
    ? `${change > 0 ? '+' : ''}${change.toFixed(1)}%`
    : 'N/A';
  
  // Define colors based on change type
  const changeColors = {
    positive: 'text-green-500',
    negative: 'text-red-500',
    neutral: 'text-gray-500',
  };
  
  // Define the background color for the change indicator
  const changeBgColors = {
    positive: 'bg-green-100',
    negative: 'bg-red-100',
    neutral: 'bg-gray-100',
  };
  
  return (
    <Card className={`p-6 hover:shadow-md transition-shadow ${className}`}>
      <div className="flex flex-col space-y-2">
        <h3 className="text-sm font-medium text-gray-500">{title}</h3>
        
        <div className="flex justify-between items-center">
          <div className="text-2xl font-bold">
            {prefix}{formattedValue}{suffix}
          </div>
          
          <div className={`flex items-center px-2 py-1 rounded-full ${changeBgColors[changeType]}`}>
            {changeType === 'positive' && <ArrowUpIcon className={`h-4 w-4 ${changeColors[changeType]}`} />}
            {changeType === 'negative' && <ArrowDownIcon className={`h-4 w-4 ${changeColors[changeType]}`} />}
            {changeType === 'neutral' && <MinusIcon className={`h-4 w-4 ${changeColors[changeType]}`} />}
            <span className={`text-sm font-medium ml-1 ${changeColors[changeType]}`}>
              {formattedChange}
            </span>
          </div>
        </div>
      </div>
    </Card>
  );
}
