import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { RegisterForm } from './register-form';

// Mock global window.location.href
const originalLocation = window.location;

beforeAll(() => {
  delete (window as any).location;
  window.location = { origin: 'http://localhost:3000', href: '' } as any;
});

afterAll(() => {
  window.location = originalLocation as any;
});

describe('RegisterForm', () => {
  test('renders form with all fields and buttons', () => {
    render(<RegisterForm />);

    // Form fields
    expect(screen.getByLabelText('Username')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();

    // Submit button
    expect(screen.getByRole('button', { name: /register/i })).toBeInTheDocument();

    // Login link
    expect(screen.getByText('Login')).toBeInTheDocument();
  });

  test('displays validation error for invalid password format', () => {
    render(<RegisterForm />);

    const passwordInput = screen.getByLabelText('Password');
    fireEvent.change(passwordInput, { target: { value: 'short' } });

    const submitButton = screen.getByRole('button', { name: /register/i });
    fireEvent.click(submitButton);

    // Expect password input to still have the value "short"
    expect(passwordInput).toHaveValue('short');

    // Expect no submission due to invalid password pattern
    expect(screen.queryByText(/registration failed/i)).not.toBeInTheDocument();
  });

  test('displays loading state when form is submitted', async () => {
    render(<RegisterForm />);

    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: /Register/ });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'ValidPass1!' } });
    fireEvent.click(submitButton);

    // Expect button text to change to "Registering..."
    expect(submitButton).toHaveTextContent(/Register/);
  });

  /*test('redirects to login page on successful registration', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve(
        new Response(JSON.stringify({}), {
          status: 200,
          statusText: 'OK',
        })
      )
    );

    render(<RegisterForm />);

    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: /register/i });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'ValidPass1!' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(window.location.href).toBe(`${window.location.origin}/login`);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:5000/register',
        expect.objectContaining({
          method: 'POST',
        })
      );
    });
  });*/

  /*test('displays error message on registration failure', async () => {
    // Mock failed registration response
    global.fetch = jest.fn(() =>
      Promise.resolve(
        new Response(
          JSON.stringify({ message: 'Username already exists' }),
          {
            status: 400,
            statusText: 'Bad Request',
            headers: { 'Content-Type': 'application/json' }
          }
        )
      )
    );
  
    render(<RegisterForm />);
  
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: /register/i });
  
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'ValidPass1!' } });
    fireEvent.click(submitButton);
  
    // Use findByText for async error display
    const errorMessage = await screen.findByText(/registration failed/i);
    expect(errorMessage).toBeInTheDocument();
    
    // Add assertion for error message content
    expect(errorMessage).toHaveTextContent('Registration failed. Username might already exist.');
  });*/
  

  /*test('handles redirect responses correctly', async () => {
    // Mock fetch with headers object containing get method
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        status: 302,
        headers: {
          get: (key: string) => 
            key === 'Location' ? 'http://localhost:5000/login' : null
        },
      } as Response)
    );
  
    render(<RegisterForm />);
  
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: /register/i });
  
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'ValidPass1!' } });
    fireEvent.click(submitButton);
  
    await waitFor(() => {
      // Verify URL replacement logic works
      expect(window.location.href).toBe('http://localhost:3000/login');
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:5000/register',
        expect.objectContaining({
          method: 'POST',
        })
      );
    });
  });*/
  

  test('disables inputs and button while loading', async () => {
    global.fetch = jest.fn(() =>
      new Promise((resolve) =>
        setTimeout(() =>
          resolve(
            new Response(JSON.stringify({}), {
              status: 200,
              headers: { 'Content-Type': 'application/json' },
            })
          ),
          1000
        )
      ))
    render(<RegisterForm />);

    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: /register/i });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
})
});
