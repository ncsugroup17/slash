jest.mock('next/navigation', () => ({
    useRouter: jest.fn(() => ({
      push: jest.fn(),
      replace: jest.fn(),
      refresh: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
    })),
  }));

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import WishlistPage from './page';

// Mock global window.location.href
const originalLocation = window.location;
// Constants
const BACKEND_URL = 'http://localhost:5000';

beforeAll(() => {
  delete (window as any).location;
  window.location = { origin: 'http://localhost:3000', href: '' } as any;
});

afterAll(() => {
  window.location = originalLocation as any;
});

describe('WishlistPage', () => {
  /*test('renders loading state initially', () => {
    render(<WishlistPage />);
    expect(screen.getByText('Loading your wishlist...')).toBeInTheDocument();
  });*/

  /*test('redirects to login page if user is not authenticated', async () => {
    // Mock fetch response for unauthenticated user
    global.fetch = jest.fn(() =>
      Promise.resolve(new Response(null, {
        status: 401
      }))
    );

    const mockRouterPush = jest.fn();
    jest.mock('next/navigation', () => ({
      useRouter: () => ({
        push: mockRouterPush
      })
    }));

    render(<WishlistPage />);

    await waitFor(() => {
      expect(mockRouterPush).toHaveBeenCalledWith('/login');
    });
  });*/

  test('renders empty wishlist message if no items are present', async () => {
    // Mock fetch response for empty wishlist
    global.fetch = jest.fn(() =>
      Promise.resolve(new Response(JSON.stringify({ products: [] }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      }))
    );

    render(<WishlistPage />);

    await waitFor(() => {
      expect(screen.getByText('Your wishlist is empty')).toBeInTheDocument();
      expect(screen.getByText('Start Shopping')).toBeInTheDocument();
    });
  });

  /*test('renders wishlist items when available', async () => {
    // Mock fetch response for wishlist with items
    const mockItems = [
      {
        id: '1',
        title: 'Product A',
        img: 'https://placehold.co/300x300?text=Product+A',
        price: '$100',
        website: 'Website A',
        rating: '4.5',
        url: '/product-a',
      },
      {
        id: '2',
        title: 'Product B',
        img: 'https://placehold.co/300x300?text=Product+B',
        price: '$200',
        website: 'Website B',
        rating: '4.8',
        url: '/product-b',
      },
    ];

    global.fetch = jest.fn(() =>
      Promise.resolve(new Response(JSON.stringify({ products: mockItems }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      }))
    );

    render(<WishlistPage />);

    await waitFor(() => {
      expect(screen.getByText('Product A')).toBeInTheDocument();
      expect(screen.getByText('$100')).toBeInTheDocument();
      expect(screen.getByText('Website A')).toBeInTheDocument();

      expect(screen.getByText('Product B')).toBeInTheDocument();
      expect(screen.getByText('$200')).toBeInTheDocument();
      expect(screen.getByText('Website B')).toBeInTheDocument();
    });
  });*/

  /*test('removes item from wishlist when remove button is clicked', async () => {
    const mockItems = [
      {
        id: '1',
        title: 'Product A',
        img: 'https://placehold.co/300x300?text=Product+A',
        price: '$100',
        website: 'Website A',
        rating: '4.5',
        url: '/product-a',
      },
    ];

    global.fetch = jest.fn((url) =>
      url.toString().includes('/wishlist')
        ? Promise.resolve(new Response(JSON.stringify({ products: mockItems }), {
            status: 200,
            headers: { 'Content-Type': 'application/json' }
          }))
        : Promise.resolve(new Response(null, { status: 200 }))
    );

    render(<WishlistPage />);

    await waitFor(() => {
      expect(screen.getByText('Product A')).toBeInTheDocument();
    });

    const removeButton = screen.getByRole('button', { name: /remove/i });
    fireEvent.click(removeButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        `${BACKEND_URL}/remove-wishlist-item`,
        expect.objectContaining({
          method: 'POST',
          body: expect.any(FormData),
          credentials: 'include',
        })
      );
      // Expect item to be removed after refresh
      expect(screen.queryByText('Product A')).not.toBeInTheDocument();
    });
  });*/

  /*test('displays error message if removing item fails', async () => {
    const mockItems = [
      {
        id: '1',
        title: 'Product A',
        img: 'https://placehold.co/300x300?text=Product+A',
        price: '$100',
        website: 'Website A',
        rating: '4.5',
        url: '/product-a',
      },
    ];

    global.fetch = jest.fn((url) =>
      url.toString().includes('/wishlist')
        ? Promise.resolve(new Response(JSON.stringify({ products: mockItems }), {
            status: 200,
            headers: { 'Content-Type': 'application/json' }
          }))
        : Promise.reject(new Error('Failed to remove item'))
    );

    render(<WishlistPage />);

    await waitFor(() => {
      expect(screen.getByText('Product A')).toBeInTheDocument();
    });

    const removeButton = screen.getByRole('button', { name: /remove/i });
    fireEvent.click(removeButton);

    await waitFor(() => {
      expect(screen.getByText(/failed to remove item/i)).toBeInTheDocument();
    });
  });*/

  /*test('opens share modal when share button is clicked', async () => {
    const mockItems = [
      {
        id: '1',
        title: 'Product A',
        img: 'https://placehold.co/300x300?text=Product+A',
        price: '$100',
        website: 'Website A',
        rating: '4.5',
        url: '/product-a',
      },
    ];

    global.fetch = jest.fn((url) => {
    if (url.toString().includes('/wishlist')) {
        return Promise.resolve(
        new Response(JSON.stringify({ products: mockItems }), {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
        })
        );
    }
    // fallback fetch for other endpoints
    return Promise.resolve(
        new Response(null, { status: 200 })
    );
    });


    render(<WishlistPage />);

    await waitFor(() => {
      expect(screen.getByText('Share Wishlist')).toBeInTheDocument();
    });

    const shareButton = screen.getByRole('button', { name: /share wishlist/i });
    fireEvent.click(shareButton);

    await waitFor(() => {
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument(); // Modal appears
      expect(screen.getByRole('button', { name: /share/i })).toBeInTheDocument();
    });
  });*/

  test('shares wishlist successfully when email is submitted', async () => {
    const mockItems = [
      {
        id: '1',
        title: 'Product A',
        img: 'https://placehold.co/300x300?text=Product+A',
        price: '$100',
        website: 'Website A',
        rating: '4.5',
        url: '/product-a',
      },
    ];

    global.fetch = jest.fn((url) =>
      url.toString().includes('/wishlist')
        ? Promise.resolve(new Response(JSON.stringify({ products: mockItems }), {
            status: 200,
            headers: { 'Content-Type': 'application/json' }
          }))
        : Promise.resolve(new Response(null, { status: 200 }))
    );
  })
});

