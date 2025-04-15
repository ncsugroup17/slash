import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// This middleware function will run for every request
export function middleware(request: NextRequest) {
  // Get the response headers
  const response = NextResponse.next()
  
  // Check if the referer is from port 5000
  const referer = request.headers.get('referer')
  
  if (referer && referer.includes('localhost:5000')) {
    // Get the current path
    const url = request.nextUrl.clone()
    url.host = 'localhost:3000'
    
    // Redirect to the same path on localhost:3000
    return NextResponse.redirect(url)
  }
  
  return response
} 