import { sql } from '@vercel/postgres';
import { NextResponse } from 'next/server';
import { headers } from 'next/headers';

const RATE_LIMIT_WINDOW = 60 * 60 * 1000; // 1 hour
const MAX_REQUESTS = 5;

const rateLimitMap = new Map<string, { count: number; timestamp: number }>();

function isRateLimited(ip: string): boolean {
  const now = Date.now();
  const record = rateLimitMap.get(ip);

  if (!record) {
    rateLimitMap.set(ip, { count: 1, timestamp: now });
    return false;
  }

  if (now - record.timestamp > RATE_LIMIT_WINDOW) {
    rateLimitMap.set(ip, { count: 1, timestamp: now });
    return false;
  }

  if (record.count >= MAX_REQUESTS) {
    return true;
  }

  record.count++;
  return false;
}

function isValidPhone(phone: string): boolean {
  // Remove all non-digits
  const cleaned = phone.replace(/\D/g, '');
  
  // Check if it's exactly 10 digits
  if (cleaned.length !== 10) {
    return false;
  }
  
  // Check if it's a valid US area code (first digit can't be 0 or 1)
  if (cleaned[0] === '0' || cleaned[0] === '1') {
    return false;
  }
  
  return true;
}

export async function POST(req: Request) {
  const headersList = await headers();
  const ip = headersList.get('x-forwarded-for') || 'unknown';
  
  if (isRateLimited(ip)) {
    return NextResponse.json(
      { error: 'Too many requests. Please try again later.' },
      { status: 429 }
    );
  }

  try {
    const { phone } = await req.json();
    
    if (!phone || !isValidPhone(phone)) {
      return NextResponse.json(
        { error: 'Invalid phone number' },
        { status: 400 }
      );
    }

    try {
      // First check if the phone number exists but is inactive
      const result = await sql`
        SELECT id, active 
        FROM subscribers 
        WHERE phone = ${phone}
      `;

      if (result.rows.length > 0) {
        if (result.rows[0].active) {
          return NextResponse.json(
            { message: "You're on the list! We'll text you when the line is looking good!" },
            { status: 200 }
          );
        } else {
          // Reactivate the subscription
          await sql`
            UPDATE subscribers 
            SET active = true 
            WHERE phone = ${phone}
          `;
          return NextResponse.json(
            { message: "You're on the list! We'll text you when the line is looking good!" },
            { status: 200 }
          );
        }
      }

      // If no existing record, create new subscription
      await sql`
        INSERT INTO subscribers (phone, created_at)
        VALUES (${phone}, NOW())
      `;

      return NextResponse.json(
        { message: 'Successfully subscribed' },
        { status: 201 }
      );
    } catch (error) {
      console.error('Error saving subscriber:', error);
      return NextResponse.json(
        { error: 'Failed to save subscriber' },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error('Error saving subscriber:', error);
    return NextResponse.json(
      { error: 'Failed to save subscriber' },
      { status: 500 }
    );
  }
} 