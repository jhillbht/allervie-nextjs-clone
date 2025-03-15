export const mockDashboardSummary = {
  impressions: 203626,
  clicks: 4581,
  conversions: 104,
  cost: 4488,
  conversionRate: 2.28,
  costPerConversion: 43.16
};

export const mockSiteMetrics = {
  conversionRate: {
    value: 9.75,
    change: 34.1
  },
  revenue: {
    value: 46825,
    change: 2.6
  },
  sessions: {
    value: 46491,
    change: -30.6
  },
  engagement: {
    value: 32.1,
    change: 38.6
  },
  bounceRate: {
    value: 22.7,
    change: -12.2
  },
  avgOrder: {
    value: 96,
    change: 1.4
  }
};

export const mockPerformanceOverTime = [
  { time: '9 AM', conversions: 620, sessions: 1500 },
  { time: '11 AM', conversions: 1150, sessions: 1200 },
  { time: '1 PM', conversions: 1050, sessions: 900 },
  { time: '3 PM', conversions: 950, sessions: 1100 },
  { time: '5 PM', conversions: 700, sessions: 1050 },
  { time: '7 PM', conversions: 1200, sessions: 650 }
];

export const mockFormPerformance = {
  patientForms: {
    changePercentage: -5.2,
    totalSubmissions: 243,
    completionRate: 78.4,
    avgTimeToComplete: '3m 42s'
  },
  sponsorForms: {
    changePercentage: -12.5,
    totalSubmissions: 86,
    completionRate: 64.8,
    avgTimeToComplete: '5m 18s'
  }
};

export const mockAdsPerformance = {
  impressions: {
    value: 203626,
    change: 41.9
  },
  clicks: {
    value: 4581,
    change: 26.8
  },
  conversions: {
    value: 104,
    change: 26.5
  },
  cost: {
    value: 4488,
    change: 41.9
  },
  clickThroughRate: {
    value: 2.25,
    change: -16.1
  },
  conversionRate: {
    value: 2.28,
    change: 20.1
  },
  costPerConversion: {
    value: 43.16,
    change: 33.0
  }
};

export const mockCampaigns = [
  {
    id: 'c1',
    name: 'New Patient Acquisition',
    status: 'ENABLED',
    impressions: 89726,
    clicks: 1876,
    conversions: 42,
    cost: 1920.45,
    ctr: 2.09,
    conversion_rate: 2.24,
    costPerConversion: 45.73
  },
  {
    id: 'c2',
    name: 'Allergy Testing Promo',
    status: 'ENABLED',
    impressions: 62341,
    clicks: 1520,
    conversions: 39,
    cost: 1345.20,
    ctr: 2.44,
    conversion_rate: 2.57,
    costPerConversion: 34.49
  },
  {
    id: 'c3',
    name: 'Asthma Awareness',
    status: 'ENABLED',
    impressions: 42184,
    clicks: 954,
    conversions: 18,
    cost: 876.30,
    ctr: 2.26,
    conversion_rate: 1.89,
    costPerConversion: 48.68
  },
  {
    id: 'c4',
    name: 'Clinical Trials',
    status: 'PAUSED',
    impressions: 8475,
    clicks: 231,
    conversions: 5,
    cost: 346.05,
    ctr: 2.73,
    conversion_rate: 2.16,
    costPerConversion: 69.21
  }
];

export const mockAdGroups = [
  {
    id: 'ag1',
    name: 'New Patients - General',
    campaign_id: 'c1',
    campaign_name: 'New Patient Acquisition',
    status: 'ENABLED',
    impressions: 52436,
    clicks: 1132,
    conversions: 28,
    cost: 1120.45,
    ctr: 2.16,
    conversion_rate: 2.47,
    costPerConversion: 40.01
  },
  {
    id: 'ag2',
    name: 'New Patients - Allergies',
    campaign_id: 'c1',
    campaign_name: 'New Patient Acquisition',
    status: 'ENABLED',
    impressions: 37290,
    clicks: 744,
    conversions: 14,
    cost: 800.00,
    ctr: 1.99,
    conversion_rate: 1.88,
    costPerConversion: 57.14
  },
  {
    id: 'ag3',
    name: 'Allergy Testing - Adults',
    campaign_id: 'c2',
    campaign_name: 'Allergy Testing Promo',
    status: 'ENABLED',
    impressions: 41562,
    clicks: 1025,
    conversions: 27,
    cost: 897.35,
    ctr: 2.47,
    conversion_rate: 2.63,
    costPerConversion: 33.24
  },
  {
    id: 'ag4',
    name: 'Allergy Testing - Children',
    campaign_id: 'c2',
    campaign_name: 'Allergy Testing Promo',
    status: 'ENABLED',
    impressions: 20779,
    clicks: 495,
    conversions: 12,
    cost: 447.85,
    ctr: 2.38,
    conversion_rate: 2.42,
    costPerConversion: 37.32
  }
];

export const mockSearchTerms = [
  {
    search_term: 'allergy doctor near me',
    campaign_id: 'c1',
    campaign_name: 'New Patient Acquisition',
    match_type: 'BROAD',
    impressions: 15426,
    clicks: 482,
    conversions: 18,
    cost: 520.56,
    ctr: 3.13,
    conversion_rate: 3.73,
    costPerConversion: 28.92
  },
  {
    search_term: 'food allergy testing',
    campaign_id: 'c2',
    campaign_name: 'Allergy Testing Promo',
    match_type: 'PHRASE',
    impressions: 12384,
    clicks: 380,
    conversions: 15,
    cost: 370.15,
    ctr: 3.07,
    conversion_rate: 3.95,
    costPerConversion: 24.68
  },
  {
    search_term: 'asthma specialist',
    campaign_id: 'c3',
    campaign_name: 'Asthma Awareness',
    match_type: 'EXACT',
    impressions: 8742,
    clicks: 245,
    conversions: 8,
    cost: 210.45,
    ctr: 2.80,
    conversion_rate: 3.27,
    costPerConversion: 26.31
  },
  {
    search_term: 'allervie health',
    campaign_id: 'c1',
    campaign_name: 'New Patient Acquisition',
    match_type: 'EXACT',
    impressions: 4256,
    clicks: 320,
    conversions: 14,
    cost: 180.80,
    ctr: 7.52,
    conversion_rate: 4.38,
    costPerConversion: 12.91
  },
  {
    search_term: 'allergy immunology clinic',
    campaign_id: 'c1',
    campaign_name: 'New Patient Acquisition',
    match_type: 'PHRASE',
    impressions: 6521,
    clicks: 187,
    conversions: 5,
    cost: 195.42,
    ctr: 2.87,
    conversion_rate: 2.67,
    costPerConversion: 39.08
  }
];
