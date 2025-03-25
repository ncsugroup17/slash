'use client';

import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Link from "next/link";
import { useRouter } from 'next/navigation';

// Constants
const BACKEND_URL = 'http://localhost:5000';
const FRONTEND_URL = 'http://localhost:3000';

export function LoginForm() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const formData = new FormData(event.currentTarget);
      
      // Direct form submission with manual redirect handling
      const response = await fetch(`${BACKEND_URL}/login`, {
        method: 'POST',
        body: formData,
        redirect: 'manual',
        credentials: 'include',
      });
      
      console.log('Login response:', response.status, response.type);
      
      // Check for redirect status or session cookie
      if (response.status === 302 || response.status === 301 || response.type === 'opaqueredirect') {
        console.log('Redirect detected');
        
        // Get the destination from the Location header
        const redirectUrl = response.headers.get('Location');
        console.log('Redirect URL:', redirectUrl);
        
        if (redirectUrl) {
          // Convert backend URL to frontend URL if needed
          if (redirectUrl.includes('localhost:5000')) {
            const frontendUrl = redirectUrl.replace(/localhost:5000/g, 'localhost:3000');
            console.log('Redirecting to frontend:', frontendUrl);
            window.location.href = frontendUrl;
          } else {
            console.log('Redirecting to:', redirectUrl);
            window.location.href = redirectUrl;
          }
        } else {
          // If login successful but no redirect, go to home
          console.log('No redirect URL, going to home');
          window.location.href = FRONTEND_URL;
        }
        return;
      }
      
      // Check if we can get cookies indicating a successful login
      if (document.cookie.includes('session')) {
        console.log('Session cookie found, login successful');
        window.location.href = FRONTEND_URL;
        return;
      }
      
      // If we get here, login likely failed
      setError('Invalid username or password. Please try again.');
    } catch (err) {
      console.error('Login error:', err);
      setError('Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container max-w-md p-8 bg-card rounded-lg shadow-lg">
      <div className="flex flex-col items-center text-center mb-8">
        <h1 className="text-3xl font-bold tracking-tighter mb-4">
          Login to Slash
        </h1>
        <p className="text-sm text-muted-foreground">
          Enter your credentials to access your account
        </p>
      </div>

      {error && (
        <div className="bg-destructive/15 text-destructive p-3 rounded-md mb-6">
          {error}
        </div>
      )}

      <form className="grid gap-4" onSubmit={handleSubmit}>
        <div className="grid gap-2">
          <label htmlFor="username" className="text-sm font-medium">
            Username
          </label>
          <Input
            id="username"
            name="username"
            type="text"
            placeholder="Enter your username"
            required
            disabled={isLoading}
          />
        </div>
        <div className="grid gap-2">
          <label htmlFor="password" className="text-sm font-medium">
            Password
          </label>
          <Input
            id="password"
            name="password"
            type="password"
            placeholder="Enter your password"
            pattern="(?=.*\\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=!]).{8,}"
            required
            disabled={isLoading}
          />
          <p className="text-xs text-muted-foreground">
            At least 8 characters including 1 uppercase, 1 lowercase, 1 digit, and 1 special character
          </p>
        </div>
        <Button type="submit" className="mt-2" disabled={isLoading}>
          {isLoading ? "Logging in..." : "Login"}
        </Button>
      </form>

      <div className="flex flex-col items-center mt-6">
        <div className="relative w-full">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-card px-2 text-muted-foreground">
              Or continue with
            </span>
          </div>
        </div>

        <div className="mt-4 w-full">
          <a href={`${BACKEND_URL}/login/google?redirect_uri=${encodeURIComponent(window.location.origin + '/search')}`} className="w-full">
            <Button className="w-full">
              Login with Google
            </Button>
          </a>
        </div>
      </div>
      
      <div className="mt-6 text-center text-sm">
        <p>
          Don't have an account?{" "}
          <Link href="/register" className="underline">
            Register
          </Link>
        </p>
      </div>
    </div>
  );
} 