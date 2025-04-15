jest.mock('next/navigation', () => ({
  useRouter: jest.fn(() => ({
    push: jest.fn(),
    replace: jest.fn(),
    refresh: jest.fn(),
    prefetch: jest.fn(),
    back: jest.fn(),
  })),
}));

import { render, screen } from '@testing-library/react';
import Home from './page';
import React from 'react';
import '@testing-library/jest-dom';

describe('Home Page Tests', () => {
  test('renders the main heading "Slash"', () => {
    render(<Home />);
    const heading = screen.getByRole('heading', { name: /slash/i });
    expect(heading).toBeInTheDocument();
  });

  test('renders the subheading about shopping experience', () => {
    render(<Home />);
    const subheading = screen.getByText(/elevating your shopping experience, all you need is one comparison\./i);
    expect(subheading).toBeInTheDocument();
  });

  test('renders the Login button', () => {
    render(<Home />);
    // Use exact text matching instead of regex
    const loginButton = screen.getByRole('button', { name: 'Login' });
    expect(loginButton).toBeInTheDocument();
  });
  

  test('renders the Login with Google button', () => {
    render(<Home />);
    const googleLoginButton = screen.getByRole('button', { name: /login with google/i });
    expect(googleLoginButton).toBeInTheDocument();
  });

  test('renders the loading state when page is loading', () => {
    jest.spyOn(React, 'useState').mockImplementationOnce(() => [true, jest.fn()]);
    render(<Home />);
    const loadingText = screen.getByText(/loading.../i);
    expect(loadingText).toBeInTheDocument();
  });
});
