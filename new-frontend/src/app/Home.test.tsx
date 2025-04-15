jest.mock('next/navigation', () => ({
  useRouter: jest.fn(() => ({
    push: jest.fn(),
    replace: jest.fn(),
    refresh: jest.fn(),
    prefetch: jest.fn(),
    back: jest.fn(),
  })),
}));

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>,
    p: ({ children, ...props }) => <p {...props}>{children}</p>,
  },
  AnimatePresence: ({ children }) => <>{children}</>,
}));

import { render, screen } from '@testing-library/react';
import Home from './page';
import React from 'react';
import '@testing-library/jest-dom';

describe('Home Page Tests', () => {
  test('renders the main heading "SLASH"', () => {
    render(<Home />);
    const heading = screen.getByRole('heading', { level: 1, name: /SLASH/i });
    expect(heading).toBeInTheDocument();
  });

  test('renders the subheading about shopping experience', () => {
    render(<Home />);
    const subheading = screen.getByText(/elevating your shopping experience/i);
    expect(subheading).toBeInTheDocument();
  });

  test('renders the description text about finding deals', () => {
    render(<Home />);
    const description = screen.getByText(/find the best deals across multiple stores/i);
    expect(description).toBeInTheDocument();
  });

  test('renders the Login with Google button', () => {
    render(<Home />);
    const googleLoginButton = screen.getByRole('button', { name: /login with google/i });
    expect(googleLoginButton).toBeInTheDocument();
  });

  test('renders feature cards with their titles', () => {
    render(<Home />);
    const fastComparisonTitle = screen.getByText(/fast comparison/i);
    const saveFavoritesTitle = screen.getByText(/save favorites/i);
    const smartRecommendationsTitle = screen.getByText(/smart recommendations/i);
    
    expect(fastComparisonTitle).toBeInTheDocument();
    expect(saveFavoritesTitle).toBeInTheDocument();
    expect(smartRecommendationsTitle).toBeInTheDocument();
  });

  test('renders the loading state when page is loading', () => {
    jest.spyOn(React, 'useState').mockImplementationOnce(() => [true, jest.fn()]);
    render(<Home />);
    const loadingText = screen.getByText(/loading.../i);
    expect(loadingText).toBeInTheDocument();
  });

  test('renders the footer with copyright information', () => {
    render(<Home />);
    const currentYear = new Date().getFullYear();
    const footerText = screen.getByText(new RegExp(`© ${currentYear} Slash - All rights reserved`, 'i'));
    expect(footerText).toBeInTheDocument();
  });
});
