import { NextResponse } from 'next/server';
import { mockFormPerformance } from '@/lib/mock-data';

export async function GET() {
  return NextResponse.json(mockFormPerformance);
}
