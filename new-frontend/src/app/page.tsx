'use client';

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import Link from "next/link"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

// Constants 
const BACKEND_URL = 'http://localhost:5000';

export default function Home() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in
    const checkAuth = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/check-auth`, {
          credentials: 'include',
        });

        if (response.ok) {
          // User is logged in, redirect to search page
          router.push('/search');
        }
      } catch (error) {
        console.error('Error checking authentication:', error);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [router]);

  if (isLoading) {
    return (
      <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-gray-100 to-gray-200 dark:from-gray-900 dark:to-gray-800">
        <div>Loading...</div>
      </main>
    );
  }

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-gray-100 to-gray-200 dark:from-gray-900 dark:to-gray-800">
      <div className="container max-w-4xl px-4 py-8">
        <div className="flex flex-col items-center text-center mb-12">
          <h1 className="text-5xl font-bold tracking-tighter mb-4 bg-gradient-to-r from-yellow-400 to-blue-600 bg-clip-text text-transparent">
            Slash
          </h1>
          <p className="text-xl text-muted-foreground max-w-[700px]">
            Elevating Your Shopping Experience, All you need is One Comparison. Shop to until your heart's content.
          </p>
        </div>

        <div className="grid gap-6">
          <form 
            className="flex w-full max-w-lg mx-auto items-center space-x-2"
            action="/search"
            method="GET"
          >
            <Input 
              type="text" 
              name="product_name" 
              placeholder="What's on your mind today?" 
              className="flex-1" 
            />
            <Button type="submit">
              Search
            </Button>
          </form>

          <div className="flex justify-center space-x-4">
            <Link href="/login">
              <Button variant="outline">Login</Button>
            </Link>
          </div>
        </div>
      </div>
    </main>
  )
}
