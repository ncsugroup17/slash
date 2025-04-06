import React, { useState, useEffect } from 'react';
import { Navbar } from '@/components/navbar';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

// Constants
const BACKEND_URL = 'http://localhost:5000';

export default function PersonalizedRecommendationsPage() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [recommendations, setRecommendations] = useState([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    
    const fetchData = async () => {
      try {
        const authResponse = await fetch(`${BACKEND_URL}/api/check-auth`, {
          credentials: 'include',
        });

        if (!authResponse.ok) {
          router.push('/login');
          return;
        }

        const authData = await authResponse.json();
        setUsername(authData.displayName || authData.username);

        const recommendationsResponse = await fetch(`${BACKEND_URL}/personalized-recommendations`, {
          credentials: 'include',
        });

        const data = await recommendationsResponse.json();

        if (recommendationsResponse.ok) {
          setRecommendations(data.recommendations || []);
          setMessage(data.response || '');
        } else {
          setError(data.error || 'Failed to load recommendations');
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        setError('An error occurred while loading your recommendations');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [router]);

  const handleProductClick = (product) => {
    window.open(product.link, '_blank');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar username={username} />
        <main className="flex-1 container max-w-7xl mx-auto p-4 flex items-center justify-center">
          <div className="flex items-center space-x-2">
            <div className="animate-spin h-5 w-5 border-t-2 border-b-2 border-primary rounded-full"></div>
            <p>Loading your recommendations...</p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar username={username} />
      <main className="flex-1 container max-w-7xl mx-auto p-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tighter mb-4">
            Personalized Recommendations
          </h1>
          <p className="text-muted-foreground">
            Products suggested based on your browsing history
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded-md mb-6">
            {error}
          </div>
        )}

        {message && (
          <div className="bg-blue-50 border border-blue-200 text-blue-800 p-4 rounded-md mb-6">
            {message}
          </div>
        )}

        {recommendations.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recommendations.map((product, index) => (
              <div 
                key={index} 
                className="border rounded-lg p-4 hover:shadow-md cursor-pointer transition-shadow"
                onClick={() => handleProductClick(product)}
              >
                <div className="aspect-square relative mb-4">
                  <img
                    src={product.img || 'https://placehold.co/300x300?text=No+Image'}
                    alt={product.title || 'Product'}
                    className="object-contain w-full h-full"
                  />
                </div>
                <h3 className="text-lg font-semibold mb-2 line-clamp-2">{product.title}</h3>
                <p className="text-xl">{product.price}</p>
                {product.rating && (
                  <p className="text-sm text-yellow-600 mt-2">
                    ★ {product.rating}
                  </p>
                )}
                <Button
                  className="w-full mt-4"
                  onClick={(e) => {
                    e.stopPropagation();
                    window.open(product.link, '_blank');
                  }}
                >
                  View Product
                </Button>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-card rounded-lg shadow p-8 text-center">
            <h2 className="text-xl font-semibold mb-4">No recommendations yet</h2>
            <p className="text-muted-foreground mb-6">
              {message || "We need more search data to provide personalized recommendations. Try searching for some products first!"}
            </p>
            <Link href="/recommendations">
              <Button>Start Searching</Button>
            </Link>
          </div>
        )}
      </main>
    </div>
  );
}