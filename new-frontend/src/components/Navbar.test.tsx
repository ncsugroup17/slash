import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import { Navbar } from './navbar'

// Mock global window.location.href
const originalLocation = window.location

beforeAll(() => {
  delete (window as any).location
  window.location = { origin: 'http://localhost:3000', href: '' } as any
})

afterAll(() => {
  window.location = originalLocation as any
})

describe('Navbar', () => {
  describe('when user is not logged in', () => {
    test('renders logo', () => {
      render(<Navbar />)
      expect(screen.getByText('Slash')).toBeInTheDocument()
    })

    test('renders login buttons', () => {
      render(<Navbar />)
      expect(screen.getByText('Login')).toBeInTheDocument()
      expect(screen.getByText('Login with Google')).toBeInTheDocument()
    })
  })

  describe('when user is logged in', () => {
    test('renders welcome message', () => {
      render(<Navbar username="Meseker" />)
      expect(screen.getByText('Welcome, Meseker')).toBeInTheDocument()
    })

    test('renders navigation links', () => {
      render(<Navbar username="Meseker" />)
      expect(screen.getByText('Search')).toBeInTheDocument()
      expect(screen.getByText('Wishlist')).toBeInTheDocument()
      expect(screen.getByText('Smart Finds')).toBeInTheDocument()
      expect(screen.getByText('For You Page')).toBeInTheDocument()
    })

    test('renders logout button', () => {
      render(<Navbar username="Meseker" />)
      expect(screen.getByText('Logout')).toBeInTheDocument()
    })

    test('shows loading state when logout button is clicked', () => {
      render(<Navbar username="Meseker" />)
      const logoutButton = screen.getByText('Logout')
      fireEvent.click(logoutButton)
      expect(screen.getByText('Logging out...')).toBeInTheDocument()
    })
  })
})
