import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Response } from 'node-fetch';
import CallbackPage from './page';

// Mock next/navigation hooks
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(() => ({
    push: jest.fn(),
  })),
  useSearchParams: jest.fn(() => ({
    get: (key: string) => key === 'code' ? 'test-code' : 'test-state',
  })),
}));

// Mock global fetch
const mockFetch = jest.fn(() =>
  Promise.resolve(new Response(null, {
    status: 200,
    statusText: 'OK'
  }))
);
global.fetch = mockFetch as unknown as typeof global.fetch;

describe('CallbackPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state correctly', () => {
    render(<CallbackPage />);
    
    expect(screen.getByText('Processing your login...')).toBeInTheDocument();
    expect(screen.getByText(/you will be redirected shortly/i)).toBeInTheDocument();
  });

  test('handles successful token exchange', async () => {
    const { useRouter, useSearchParams } = require('next/navigation');
    const mockPush = jest.fn();
    
    useRouter.mockImplementation(() => ({
      push: mockPush,
    }));
    
    useSearchParams.mockImplementation(() => ({
      get: (key: string) => key === 'code' ? 'test-code' : 'test-state',
    }));

    render(<CallbackPage />);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:5000/exchange-token?code=test-code&state=test-state',
        expect.objectContaining({
          method: 'GET',
          credentials: 'include'
        })
      );
      expect(mockPush).toHaveBeenCalledWith('/');
    });
  });

  test('handles missing code/state parameters', async () => {
    const { useSearchParams } = require('next/navigation');
    const { useRouter } = require('next/navigation');
    const mockPush = jest.fn();
    
    useRouter.mockImplementation(() => ({
      push: mockPush,
    }));
    
    useSearchParams.mockImplementation(() => ({
      get: () => null,
    }));

    render(<CallbackPage />);

    await waitFor(() => {
      expect(mockFetch).not.toHaveBeenCalled();
      expect(mockPush).toHaveBeenCalledWith('/');
    });
  });

  test('handles token exchange error', async () => {
    const { useRouter } = require('next/navigation');
    const mockPush = jest.fn();
    
    useRouter.mockImplementation(() => ({
      push: mockPush,
    }));

    mockFetch.mockImplementationOnce(() =>
      Promise.reject(new Error('Network error'))
    );

    render(<CallbackPage />);

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/');
    });
  });
});
