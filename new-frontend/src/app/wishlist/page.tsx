'use client';

import { Button } from "@/components/ui/button"
import { Navbar } from "@/components/navbar"
import Link from "next/link"
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

// Constants
const BACKEND_URL = 'http://localhost:5000';

export default function WishlistPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [wishlistItems, setWishlistItems] = useState([]);
  const [username, setUsername] = useState('');
  const [error, setError] = useState(null);
  const [sharingEmail, setSharingEmail] = useState('');
  const [shareStatus, setShareStatus] = useState({ message: '', isError: false });
  const [removingItems, setRemovingItems] = useState({});
  
  // Check auth and fetch wishlist on mount
  useEffect(() => {
    const checkAuthAndFetchWishlist = async () => {
      try {
        // First check if user is authenticated
        const authResponse = await fetch(`${BACKEND_URL}/api/check-auth`, {
          credentials: 'include',
        });
        
        if (!authResponse.ok) {
          // Not authenticated, redirect to login
          router.push('/login');
          return;
        }
        
        const authData = await authResponse.json();
        setIsAuthenticated(true);
        setUsername(authData.displayName || authData.username);
        
        // Then fetch the wishlist
        await fetchWishlist();
      } catch (error) {
        console.error('Error checking authentication:', error);
        setError('Failed to authenticate. Please login again.');
        setIsLoading(false);
      }
    };
    
    checkAuthAndFetchWishlist();
  }, [router]);
  
  // Direct access to wishlist page to grab the HTML content
  const fetchWishlist = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('Fetching wishlist HTML...');
      const response = await fetch(`${BACKEND_URL}/wishlist`, {
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
        }
      });
      
      if (!response.ok) {
        console.error('Failed to fetch wishlist HTML:', response.status);
        throw new Error(`Server returned ${response.status}`);
      }
      
      // Try to parse as JSON first
      try {
        const jsonData = await response.json();
        console.log('Received JSON wishlist data:', jsonData);
        
        if (jsonData.products && Array.isArray(jsonData.products)) {
          setWishlistItems(jsonData.products);
          setIsLoading(false);
          return;
        }
      } catch (jsonError) {
        console.log('Response is not JSON, trying HTML parsing');
      }
      
      // Fallback to HTML parsing if JSON fails
      const html = await response.text();
      console.log('Received HTML length:', html.length);
      
      // Create a DOM parser
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      
      // Find the wishlist table
      const table = doc.querySelector('table');
      if (!table) {
        console.warn('No table found in wishlist HTML');
        // Check if this is an empty wishlist
        const emptyMessage = doc.querySelector('.container p');
        if (emptyMessage && emptyMessage.textContent.includes('empty')) {
          console.log('Empty wishlist detected');
          setWishlistItems([]);
          setIsLoading(false);
          return;
        }
        throw new Error('Could not find wishlist table');
      }
      
      // Extract items from the table
      const rows = table.querySelectorAll('tbody tr');
      console.log('Found rows:', rows.length);
      
      // Examine the HTML structure carefully
      if (rows.length > 0) {
        console.log('First row HTML:', rows[0].outerHTML);
        
        // Log all cell contents of the first row to better understand the structure
        const firstRowCells = rows[0].querySelectorAll('td');
        console.log('First row has', firstRowCells.length, 'cells');
        firstRowCells.forEach((cell, i) => {
          console.log(`Cell ${i} content:`, cell.textContent);
        });
      }
      
      // If JSON endpoint failed, fallback to HTML parsing
      const items = [];
      rows.forEach((row, index) => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 5) {
          try {
            // Since we don't have access to the actual product ID in the HTML,
            // we'll use the URL as a unique identifier
            const productCell = cells[0];
            const title = productCell.textContent.trim();
            
            const imgEl = cells[1].querySelector('img');
            const imgSrc = imgEl ? imgEl.getAttribute('src') : '';
            
            const price = cells[2].textContent.trim();
            const website = cells[3].textContent.trim();
            const rating = cells[4].textContent.trim();
            
            // Find the product URL which we can use as a unique identifier
            const linkEl = productCell.querySelector('a');
            const url = linkEl ? linkEl.getAttribute('href') : '#';
            
            // Let's try a different approach - we'll use url as a unique identifier
            // Each product in the database has a unique URL
            
            items.push({
              index: index,
              id: String(index), // This will be used for display/tracking
              title: title || 'Unknown Product',
              img: imgSrc || 'https://placehold.co/300x300?text=No+Image',
              price: price || '$0.00',
              website: website || 'Unknown Source',
              rating: rating || 'Not Rated',
              url: url
            });
          } catch (err) {
            console.error('Error parsing row:', err);
          }
        }
      });
      
      console.log('Parsed wishlist items:', items);
      setWishlistItems(items);
    } catch (error) {
      console.error('Error fetching wishlist:', error);
      setError(`Failed to load your wishlist: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Function to remove item from wishlist
  const handleRemoveItem = async (item) => {
    console.log('Removing item:', item);
    
    // Mark item as being removed
    setRemovingItems(prev => ({ ...prev, [item.id]: true }));
    
    try {
      // The endpoint is /remove-wishlist-item, not /remove-from-wishlist
      const formData = new FormData();
      formData.append('id', item.id);
      
      console.log(`Attempting to remove product with ID: ${item.id}`);
      
      // Send a direct request using fetch
      const response = await fetch(`${BACKEND_URL}/remove-wishlist-item`, {
        method: 'POST',
        body: formData,
        credentials: 'include',
      });
      
      console.log('Remove response status:', response.status);
      
      // Try to read the response
      let responseText = '';
      try {
        responseText = await response.text();
        console.log('Remove response text:', responseText);
      } catch (e) {
        console.error('Error reading response:', e);
      }
      
      // Check if successful
      if (response.ok) {
        console.log('Successfully removed item from wishlist');
      } else {
        console.error('Failed to remove item:', responseText);
        
        // Try alternative removal approaches
        await tryAlternativeRemoval(item);
      }
      
      // Always refresh the wishlist
      await fetchWishlist();
    } catch (error) {
      console.error('Error removing item:', error);
      setError('Failed to remove item. Please try again.');
      
      // Try alternative approaches
      await tryAlternativeRemoval(item);
      
      // Refresh the wishlist anyway
      await fetchWishlist();
    } finally {
      setRemovingItems(prev => ({ ...prev, [item.id]: false }));
    }
  };
  
  // Alternative removal approaches
  const tryAlternativeRemoval = async (item) => {
    console.log('Trying alternative removal approaches');
    
    // Try using window.open to directly navigate to the wishlist page
    // This might trigger the removal through the original Flask routes
    try {
      // Create an iframe to avoid navigating away
      const iframe = document.createElement('iframe');
      iframe.style.display = 'none';
      document.body.appendChild(iframe);
      
      // Create a form inside the iframe
      const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
      const form = iframeDoc.createElement('form');
      form.method = 'POST';
      form.action = `${BACKEND_URL}/remove-wishlist-item`;
      
      // Add the product ID
      const idInput = iframeDoc.createElement('input');
      idInput.name = 'id';
      idInput.value = item.id;
      form.appendChild(idInput);
      
      // Add the form to the iframe document and submit
      iframeDoc.body.appendChild(form);
      form.submit();
      
      // Wait a bit before removing the iframe
      setTimeout(() => {
        document.body.removeChild(iframe);
      }, 2000);
    } catch (error) {
      console.error('Alternative removal approach failed:', error);
    }
  };
  
  // Function to share wishlist
  const handleShareWishlist = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setShareStatus({ message: 'Sharing...', isError: false });
    
    try {
      // Create form data for submission
      const formData = new FormData();
      formData.append('email', sharingEmail);
      
      console.log(`Sharing wishlist with ${sharingEmail}`);
      
      // Send email via backend API
      const response = await fetch(`${BACKEND_URL}/share`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: sharingEmail,
          wishlist: wishlistItems,
        }),
        credentials: 'include',
      });
      
      console.log('Share response:', response.status);
      
      
      // Show success message
      setShareStatus({ message: 'Wishlist shared successfully!', isError: false });
      
      // Close modal after a delay
      setTimeout(() => {
        setIsModalOpen(false);
        setShareStatus({ message: '', isError: false });
      }, 2000);
    } catch (error) {
      console.error('Error sharing wishlist:', error);
      setShareStatus({ 
        message: `Failed to share wishlist: ${error.message}`, 
        isError: true 
      });
    }
  };
  
  const openShareModal = () => {
    setIsModalOpen(true);
    setShareStatus({ message: '', isError: false });
  };
  
  const closeShareModal = () => {
    setIsModalOpen(false);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar username={username} />
        <main className="flex-1 container max-w-7xl mx-auto p-4 flex items-center justify-center">
          <p>Loading your wishlist...</p>
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
            Your Wishlist
          </h1>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded-md mb-6">
              {error}
              <Button
                onClick={() => fetchWishlist()}
                className="ml-4"
                size="sm"
                variant="outline"
              >
                Try Again
              </Button>
            </div>
          )}
        </div>

        <div className="bg-card rounded-lg shadow">
          {wishlistItems.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-4 font-medium">Product</th>
                    <th className="text-left p-4 font-medium">Image</th>
                    <th className="text-left p-4 font-medium">Price</th>
                    <th className="text-left p-4 font-medium">Website</th>
                    <th className="text-left p-4 font-medium">Rating</th>
                    <th className="text-left p-4 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {wishlistItems.map((item) => (
                    <tr key={item.id} className="border-b">
                      <td className="p-4">
                        <a href={item.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                          {item.title}
                        </a>
                      </td>
                      <td className="p-4">
                        <img 
                          src={item.img} 
                          alt={item.title} 
                          className="w-16 h-16 object-cover rounded"
                        />
                      </td>
                      <td className="p-4">{item.price}</td>
                      <td className="p-4">{item.website}</td>
                      <td className="p-4">{item.rating}</td>
                      <td className="p-4">
                        <Button 
                          onClick={() => handleRemoveItem(item)} 
                          variant="destructive" 
                          size="sm"
                          disabled={removingItems[item.id]}
                        >
                          {removingItems[item.id] ? "Removing..." : "Remove"}
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-8 text-center">
              <p className="text-muted-foreground mb-4">Your wishlist is empty</p>
              <Link href="/search">
                <Button>
                  Start Shopping
                </Button>
              </Link>
            </div>
          )}
        </div>

        {wishlistItems.length > 0 && (
          <div className="mt-8">
            <Button onClick={openShareModal}>
              Share Wishlist
            </Button>
          </div>
        )}

        {isModalOpen && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-card rounded-lg shadow-lg p-6 max-w-md w-full">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">Share Wishlist</h2>
                <button
                  onClick={closeShareModal}
                  className="text-muted-foreground"
                >
                  ✕
                </button>
              </div>
              
              {shareStatus.message && (
                <div className={`mb-4 p-3 rounded ${shareStatus.isError ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'}`}>
                  {shareStatus.message}
                </div>
              )}
              
              <form onSubmit={handleShareWishlist} className="grid gap-4">
                <div className="grid gap-2">
                  <label htmlFor="email" className="text-sm font-medium">
                    Email
                  </label>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    value={sharingEmail}
                    onChange={(e) => setSharingEmail(e.target.value)}
                    placeholder="Enter recipient's email"
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    required
                  />
                </div>
                <Button type="submit" disabled={shareStatus.message === 'Sharing...'}>
                  {shareStatus.message === 'Sharing...' ? 'Sharing...' : 'Share'}
                </Button>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  )
} 