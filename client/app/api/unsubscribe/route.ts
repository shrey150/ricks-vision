import { sql } from '@vercel/postgres';
import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const { phone } = await req.json();
    
    if (!phone) {
      return NextResponse.json(
        { error: 'Phone number is required' },
        { status: 400 }
      );
    }

    await sql`
      UPDATE subscribers 
      SET active = false 
      WHERE phone = ${phone}
    `;

    return NextResponse.json(
      { message: 'Successfully unsubscribed' },
      { status: 200 }
    );
  } catch (error) {
    console.error('Error unsubscribing:', error);
    return NextResponse.json(
      { error: 'Failed to unsubscribe' },
      { status: 500 }
    );
  }
} 