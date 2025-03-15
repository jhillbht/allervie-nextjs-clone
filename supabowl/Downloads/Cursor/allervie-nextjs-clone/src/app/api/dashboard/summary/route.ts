import { NextResponse } from 'next/server';
import { mockDashboardSummary } from '@/lib/mock-data';

export async function GET() {
  return NextResponse.json(mockDashboardSummary);
}
