'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function CallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    // Immediately redirect to home page
    console.log('Callback received, redirecting to home page');
    
    // Get code and state from URL if they exist
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    
    if (code && state) {
      // Make a call to the backend to exchange the code for a token
      fetch(`http://localhost:5000/exchange-token?code=${code}&state=${state}`, {
        method: 'GET',
        credentials: 'include'
      })
      .then(response => {
        console.log('Token exchange response:', response.status);
        // Redirect to home page after token exchange
        router.push('/');
      })
      .catch(error => {
        console.error('Error exchanging token:', error);
        // Still redirect to home on error
        router.push('/');
      });
    } else {
      // If no code/state, just redirect to home
      router.push('/');
    }
  }, [router, searchParams]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      <h1 className="text-2xl font-bold mb-4">Processing your login...</h1>
      <p>Please wait, you will be redirected shortly.</p>
    </div>
  );
} 