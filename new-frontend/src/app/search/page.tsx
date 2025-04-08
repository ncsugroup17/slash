'use client';

import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Navbar } from "@/components/navbar"
import { useRouter, useSearchParams } from 'next/navigation';
import { useToast } from '@/components/ui/toast';

// Constants
const BACKEND_URL = 'http://localhost:5000';

export default function SearchPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isLoading, setIsLoading] = useState(true);
  const [isSearching, setIsSearching] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [username, setUsername] = useState('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [addingToWishlist, setAddingToWishlist] = useState<Record<string, boolean>>({});
  const [wishlistMessages, setWishlistMessages] = useState<Record<string, {message: string, isError: boolean}>>({});
  
  // Initialize toast notifications
  const { addToast, ToastList } = useToast();

  // Get the product name from URL query params
  const productName = searchParams.get('product_name');

  useEffect(() => {
    // Initialize search term from URL if present
    if (productName) {
      setSearchTerm(productName);
    }

    // Check if user is authenticated
    const checkAuth = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/check-auth`, {
          credentials: 'include',
        });

        if (response.ok) {
          const data = await response.json();
          setIsAuthenticated(true);
          setUsername(data.displayName || data.username);
          
          // If product_name exists in query, perform search
          if (productName) {
            performSearch(productName);
          }
        } else {
          // Not authenticated, redirect to login
          router.push('/login');
        }
      } catch (error) {
        console.error('Error checking authentication:', error);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [router, productName]);

  const performSearch = async (term) => {
    try {
      setIsSearching(true);
      setHasSearched(false);
      setErrorMessage(null);
      
      // Call backend search API with a format parameter to ensure we get JSON
      const response = await fetch(`${BACKEND_URL}/search?product_name=${encodeURIComponent(term)}&format=json`, {
        credentials: 'include',
        headers: {
          'Accept': 'application/json'
        },
      });
      
      // Handle HTTP errors first
      if (!response.ok && response.status !== 200) {
        console.error('Search failed with status:', response.status);
        if (response.status === 401) {
          // Not authenticated
          router.push('/login');
          return;
        }
        throw new Error(`Search request failed with status ${response.status}`);
      }
      
      // Parse the JSON response
      const data = await response.json();
      
      // Handle API errors (even with 200 status)
      if (data.error) {
        console.warn('Search API returned error:', data.error);
        setErrorMessage(data.error);
        setResults([]);
      } else if (data.products && Array.isArray(data.products)) {
        // Success case - we have products
        if (data.products.length === 0) {
          setErrorMessage(`No results found for "${term}". Try a different search term.`);
        }
        // Improve logging to better understand the data structure
        if (data.products.length > 0) {
          console.log('First product raw data:', JSON.stringify(data.products[0], null, 2));
          console.log('Available product fields:', Object.keys(data.products[0]).join(', '));
        }
        
        // Process products to ensure all required fields are present
        const processedProducts = data.products.map(product => {
          // Debug each product title
          console.log(`Product title fields: title=${product.title}, name=${product.name}, productName=${product.product_name}`);
          
          return {
            ...product,
            // Use title or name or product_name, falling back to other potential fields
            title: product.title || product.name || product.product_name || 'Product'
          };
        });
        
        // Update results first
        setResults(processedProducts);
      } else {
        // Unexpected response format
        console.error('Unexpected response format:', data);
        setErrorMessage('Received an invalid response from the server.');
        setResults([]);
      }
    } catch (error) {
      console.error('Error performing search:', error);
      setErrorMessage('Failed to search. Please try again later.');
      setResults([]);
    } finally {
      // Mark search as completed and clear loading state
      setHasSearched(true);
      setIsSearching(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    
    if (searchTerm.trim()) {
      // Update URL with search term
      router.push(`/search?product_name=${encodeURIComponent(searchTerm)}`);
      
      // Perform search
      performSearch(searchTerm);
    }
  };

  // Function to add a product to wishlist
  const addToWishlist = async (product, event) => {
    // Prevent any default behavior that might cause page refresh
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    
    if (!product) return;
    
    const productId = product.id || `product-${new Date().getTime()}`;
    
    // Don't proceed if already adding this product
    if (addingToWishlist[productId]) {
      console.log('Already processing this product, ignoring duplicate click');
      return;
    }
    
    // Set loading state
    setAddingToWishlist(prev => ({ ...prev, [productId]: true }));
    setWishlistMessages(prev => ({ ...prev, [productId]: null }));
    
    console.log('Adding product to wishlist - START:', product);
    
    try {
      // First, check if we're still authenticated
      console.log('Checking authentication status before adding to wishlist');
      const authCheckResponse = await fetch(`/api/check-auth`, {
        credentials: 'include',
        headers: {
          'Accept': 'application/json'
        },
      });
      
      if (!authCheckResponse.ok) {
        console.error('Authentication check failed:', await authCheckResponse.text());
        addToast("Please log in again to add items", "error");
        
        // Redirect to login page
        setTimeout(() => {
          router.push('/login');
        }, 2000);
        
        return;
      }
      
      console.log('Authentication confirmed, proceeding with wishlist addition');
      
      // Create form data for submission
      const formData = new FormData();
      
      // Add timestamp to make each addition unique
      const timestamp = new Date().getTime();
      
      // Generate a unique ID/URL for this wishlist addition
      const uniqueProductUrl = product.link || product.url || '#';
      const uniqueUrl = uniqueProductUrl.includes('?') 
        ? `${uniqueProductUrl}&_t=${timestamp}` 
        : `${uniqueProductUrl}?_t=${timestamp}`;
      
      formData.append('title', product.title || 'Unknown Product');
      formData.append('img', product.image_url || product.img_link || 'https://placehold.co/300x300?text=No+Image');
      formData.append('price', product.price || '$0.00');
      formData.append('website', product.website || 'Unknown');
      formData.append('rating', product.rating || '0');
      // Use unique URL for each addition to bypass duplicate detection
      formData.append('url', uniqueUrl);
      
      console.log('Sending request with unique URL:', uniqueUrl);
      
      // Direct fetch approach through Next.js rewrites (not directly to backend)
      const response = await fetch(`/add-wishlist-item`, {
        method: 'POST',
        body: formData,
        credentials: 'include',
        headers: {
          'Accept': 'application/json, text/plain, */*',
          'X-Requested-With': 'XMLHttpRequest'
        }
      });
      
      console.log('Add to wishlist response status:', response.status);
      
      // Get the response text
      const responseText = await response.text();
      console.log('Add to wishlist response text:', responseText);
      
      // Try to parse as JSON if possible
      let jsonResponse = null;
      try {
        if (responseText.trim().startsWith('{')) {
          jsonResponse = JSON.parse(responseText);
          console.log('Parsed JSON response:', jsonResponse);
        }
      } catch (jsonError) {
        console.log('Response is not valid JSON');
      }
      
      // Handle the response based on status and content
      if (response.ok) {
        console.log('Successfully added to wishlist');
        // Show toast notification and update in-line message
        addToast(`${product.title} added to wishlist!`, "success");
        setWishlistMessages(prev => ({
          ...prev,
          [productId]: { message: "Added to wishlist!", isError: false }
        }));
        
        // Clear in-line success message after 3 seconds
        setTimeout(() => {
          setWishlistMessages(prev => ({ ...prev, [productId]: null }));
        }, 3000);
      } else if (response.status === 401) {
        console.error('Authentication error - redirecting to login');
        addToast("Please log in to add items", "error");
        setWishlistMessages(prev => ({
          ...prev,
          [productId]: { message: "Please log in to add items", isError: true }
        }));
        
        // Redirect to login
        setTimeout(() => {
          router.push('/login');
        }, 2000);
      } else if (response.status === 409 || responseText.includes('already in wishlist')) {
        // This shouldn't happen now, but we'll handle it just in case
        console.error('Product still detected as duplicate despite unique URL');
        addToast(`Unable to add duplicate item to wishlist`, "error");
        setWishlistMessages(prev => ({
          ...prev,
          [productId]: { message: "Duplicate detection active, please try again", isError: true }
        }));
      } else {
        console.error('Failed to add to wishlist:', responseText);
        
        // Extract error message
        let errorMsg = "Failed to add to wishlist";
        if (jsonResponse && jsonResponse.error) {
          errorMsg = jsonResponse.error;
        } else {
          try {
            // Try to extract error message from HTML response
            const errorMatch = responseText.match(/<p>(.*?)<\/p>/);
            if (errorMatch) {
              errorMsg = errorMatch[1];
            }
          } catch (parseError) {
            console.error('Error parsing response:', parseError);
          }
        }
        
        console.log('Final error message:', errorMsg);
        addToast(errorMsg, "error");
        setWishlistMessages(prev => ({
          ...prev,
          [productId]: { message: errorMsg, isError: true }
        }));
      }
    } catch (error) {
      console.error('Exception adding to wishlist:', error);
      addToast("Network error. Please try again.", "error");
      setWishlistMessages(prev => ({ 
        ...prev, 
        [productId]: { message: "Network error. Please try again.", isError: true } 
      }));
    } finally {
      console.log('Add to wishlist operation complete');
      setAddingToWishlist(prev => ({ ...prev, [productId]: false }));
    }
  };

  // Only show full page loader for initial page load
  if (isLoading && !productName) {
    // Only show full page loader for initial page load, not during searches
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar username={username || 'Guest'} />
        <main className="flex-1 container max-w-7xl mx-auto p-4">
          <div className="mb-8">
            <h1 className="text-3xl font-bold tracking-tighter mb-4">
              Product Search
            </h1>
            <div className="flex w-full max-w-lg items-center space-x-2">
              <div className="flex-1 h-10 bg-gray-100 animate-pulse rounded"></div>
              <div className="w-20 h-10 bg-gray-100 animate-pulse rounded"></div>
            </div>
          </div>
          <div className="flex justify-center py-8">
            <div className="inline-flex items-center px-4 py-2 bg-blue-50 text-blue-500 rounded-md">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Loading...</span>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-100">
      <Navbar username={username} />
      <ToastList />
      <main className="flex-1 container max-w-7xl mx-auto p-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tighter mb-4">
            {username ? `Hello, ${username}!` : 'Product Search'}
          </h1>
          <form onSubmit={handleSearch} className="flex w-full max-w-lg items-center space-x-2">
            <Input 
              type="text" 
              name="product_name" 
              placeholder="What are you looking for?" 
              className="flex-1"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <Button type="submit" disabled={isSearching}>
              {isSearching ? (
                <span className="inline-flex items-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Searching...
                </span>
              ) : (
                'Search'
              )}
            </Button>
          </form>
        </div>

        <div>
          {errorMessage && (
            <div className="bg-amber-50 border border-amber-200 text-amber-800 p-4 rounded-md mb-6">
              {errorMessage}
            </div>
          )}
          
          {/* Show loading indicator during search */}
          {isSearching && (
            <div className="border rounded-md p-4 mb-6">
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 bg-slate-200 rounded-md animate-pulse"></div>
                <div className="space-y-2 flex-1">
                  <div className="h-4 bg-slate-200 rounded w-1/3 animate-pulse"></div>
                  <div className="h-4 bg-slate-200 rounded w-1/2 animate-pulse"></div>
                  <div className="h-4 bg-slate-200 rounded w-1/4 animate-pulse"></div>
                </div>
              </div>
              <div className="h-5 mt-4 text-sm text-blue-500 flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Searching for "{productName}"...
              </div>
            </div>
          )}
          
          {/* Only show results when not searching and there are results */}
          {!isSearching && results.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {results.map((product, index) => {
                // Debug log - can be removed in production
                console.log(`Product ${index}:`, product);
                
                const productId = product.id || `product-${index}`;
                const isAdding = addingToWishlist[productId];
                const wishlistMessage = wishlistMessages[productId];
                
                return (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="aspect-square relative mb-4">
                      <img
                        src={product.image_url || product.img_link || 'https://placehold.co/300x300?text=No+Image'}
                        alt={product.title || 'Product'}
                        className="object-contain w-full h-full"
                      />
                    </div>
                    <h3 className="text-lg font-bold">{product.title || 'Unknown Product'}</h3>
                    <p className="text-xl">{product.price || '$0.00'}</p>
                    <p className="text-sm text-gray-500">{product.website}</p>
                    {product.rating && (
                      <p className="text-sm text-yellow-600">★ {product.rating} ({product.no_of_ratings || '0'} reviews)</p>
                    )}
                    <div className="flex justify-between mt-4">
                      <Button variant="outline" size="sm" asChild>
                        <a href={product.link} target="_blank" rel="noopener noreferrer">
                          View Product
                        </a>
                      </Button>
                      <Button 
                        size="sm" 
                        onClick={(e) => addToWishlist(product, e)}
                        disabled={isAdding}
                        className={`min-w-[130px] ${wishlistMessage && !wishlistMessage.isError ? "bg-green-600 hover:bg-green-700" : ""}`}
                      >
                        {isAdding ? "Adding..." : wishlistMessage && !wishlistMessage.isError ? "Added!" : "Add to Wishlist"}
                      </Button>
                    </div>
                    {wishlistMessage && (
                      <div className={`mt-2 text-sm px-2 py-1 rounded ${wishlistMessage.isError ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'}`}>
                        {wishlistMessage.message}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
          
          {/* Only show "No results" when: not searching, has searched, and has no results */}
          {!isSearching && hasSearched && results.length === 0 && productName && (
            <div className="text-center py-8 text-gray-500">
              No results found for "{productName}"
            </div>
          )}
        </div>
      </main>
    </div>
  )
} 