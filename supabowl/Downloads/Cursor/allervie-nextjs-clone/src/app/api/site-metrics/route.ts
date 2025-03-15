import { NextResponse } from 'next/server';
import { mockSiteMetrics } from '@/lib/mock-data';

export async function GET() {
  return NextResponse.json(mockSiteMetrics);
}
