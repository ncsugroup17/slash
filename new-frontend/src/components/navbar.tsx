'use client';

import Link from "next/link"
import { Button, buttonVariants } from "@/components/ui/button"
import { useState } from "react"

// Constants
const BACKEND_URL = 'http://localhost:5000';
const FRONTEND_URL = 'http://localhost:3000';

interface NavbarProps {
  username?: string
}

export function Navbar({ username }: NavbarProps) {
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const isLoggedIn = !!username

  const handleLogout = async (event: React.MouseEvent<HTMLAnchorElement>) => {
    event.preventDefault();
    setIsLoggingOut(true);

    try {
      // Call the logout endpoint with a redirect back to the homepage
      window.location.href = `${BACKEND_URL}/logout?redirect_uri=${encodeURIComponent(window.location.origin)}`;
    } catch (error) {
      console.error('Error during logout:', error);
      setIsLoggingOut(false);
    }
  };

  return (
    <nav className="bg-background border-b sticky top-0 z-10">
      <div className="container flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-xl font-bold">Slash</span>
          </Link>
          {isLoggedIn && (
            <>
              <Link href="/search" className="text-sm font-medium transition-colors hover:text-primary">
                Search
              </Link>
              <Link href="/wishlist" className="text-sm font-medium transition-colors hover:text-primary">
                Wishlist
              </Link>
              <Link href="/recommendations" className="text-sm font-medium transition-colors hover:text-primary">
                <span className="flex items-center">
                  <span className="mr-1">✨</span> AI Recommendations
                </span>
              </Link>
            </>
          )}
        </div>
        <div className="flex items-center gap-4">
          {isLoggedIn ? (
            <>
              <span className="text-sm">Welcome, {username}</span>
              <a href="#" onClick={handleLogout}>
                <Button variant="outline" size="sm" disabled={isLoggingOut}>
                  {isLoggingOut ? "Logging out..." : "Logout"}
                </Button>
              </a>
            </>
          ) : (
            <>
              <Link href="/login">
                <Button variant="outline" size="sm">
                  Login
                </Button>
              </Link>
              <a href={`${BACKEND_URL}/login/google?redirect_uri=${encodeURIComponent(window.location.origin + '/search')}`}>
                <Button size="sm">
                  Login with Google
                </Button>
              </a>
            </>
          )}
        </div>
      </div>
    </nav>
  )
} 