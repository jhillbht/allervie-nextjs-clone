import { NextResponse } from 'next/server';
import { mockPerformanceOverTime } from '@/lib/mock-data';

export async function GET() {
  return NextResponse.json(mockPerformanceOverTime);
}
