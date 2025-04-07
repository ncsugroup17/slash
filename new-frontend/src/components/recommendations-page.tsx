'use client';

import React, { useState, useEffect } from 'react';
import { Navbar } from '@/components/navbar';

// Constants
const BACKEND_URL = 'http://localhost:5000';

export default function RecommendationsPage() {
  const [username, setUsername] = useState<string | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/check-auth`, {
          credentials: 'include'
        });
        
        if (response.ok) {
          const data = await response.json();
          if (data.authenticated) {
            setUsername(data.displayName || data.username);
          }
        }
      } catch (error) {
        console.error('Authentication check failed:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    checkAuth();
  }, []);

  if (isLoading) {
    return (
      <div>
        <Navbar username={username} />
        <div className="container py-8">
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <Navbar username={username} />
      <div className="container py-8">
        <AIRecommendationSystem />
      </div>
    </div>
  );
}

const AIRecommendationSystem = () => {
  const [question, setQuestion] = useState('');
  const [userInput, setUserInput] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversation, setConversation] = useState([]);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [error, setError] = useState('');

  // Check authentication on component mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/check-auth`, {
          credentials: 'include'
        });
        
        if (response.ok) {
          const data = await response.json();
          setIsAuthenticated(data.authenticated);
        }
      } catch (error) {
        console.error('Authentication check failed:', error);
      }
    };
    
    checkAuth();
  }, []);

  // Initial prompt to start the conversation
  useEffect(() => {
    setQuestion("Hi! I'd like to help you find products you'll love. What are you looking for today?");
  }, []);
  
  // Handle user input submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!userInput.trim()) return;
    
    // Update conversation with user input
    const updatedConversation = [
      ...conversation,
      { role: 'user', content: userInput }
    ];
    
    setConversation(updatedConversation);
    setIsLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${BACKEND_URL}/ai-recommendations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ 
          conversation: updatedConversation,
          previousQuestion: question
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to get recommendations');
      }
      
      const data = await response.json();
      
      // Update conversation with AI response
      setConversation([
        ...updatedConversation,
        { role: 'assistant', content: data.response }
      ]);
      
      // Update next question or recommendation
      setQuestion(data.nextQuestion || '');
      
      // If recommendations are provided, update state
      if (data.recommendations && data.recommendations.length > 0) {
        setRecommendations(data.recommendations);
      }
      
    } catch (err) {
      setError('Sorry, there was an error getting recommendations. Please try again.');
      console.error('Recommendation error:', err);
    } finally {
      setIsLoading(false);
      setUserInput('');
    }
  };
  
  // Handle clicking on a recommended product
  const handleProductClick = (product) => {
    // Open product link in new tab
    window.open(product.link, '_blank');
  };

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md max-w-2xl mx-auto">
        <h2 className="text-2xl font-bold mb-4">Personalized Recommendations</h2>
        <p className="mb-4">Please log in to get personalized product recommendations.</p>
        <button 
          onClick={() => window.location.href = '/login'}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Login
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">AI-Powered Recommendations</h2>
      
      {/* Conversation history */}
      <div className="mb-6 max-h-64 overflow-y-auto">
        {conversation.map((message, index) => (
          <div 
            key={index} 
            className={`mb-4 ${message.role === 'user' ? 'text-right' : 'text-left'}`}
          >
            <div 
              className={`inline-block px-4 py-2 rounded-lg ${
                message.role === 'user' 
                  ? 'bg-blue-100 text-blue-800' 
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}
      </div>
      
      {/* Current question from AI */}
      {question && (
        <div className="mb-6 p-4 bg-gray-100 rounded-lg">
          <p>{question}</p>
        </div>
      )}
      
      {/* User input form */}
      <form onSubmit={handleSubmit} className="mb-6">
        <div className="flex">
          <input
            type="text"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Type your answer here..."
            className="flex-grow p-2 border border-gray-300 rounded-l focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded-r hover:bg-blue-700 disabled:bg-blue-300"
            disabled={isLoading || !userInput.trim()}
          >
            {isLoading ? 'Thinking...' : 'Submit'}
          </button>
        </div>
        {error && <p className="mt-2 text-red-600">{error}</p>}
      </form>
      
      {/* Product recommendations */}
      {recommendations.length > 0 && (
        <div>
          <h3 className="text-xl font-semibold mb-4">Recommended Products</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recommendations.map((product, index) => (
              <div 
                key={index}
                className="border rounded-lg p-4 hover:shadow-md cursor-pointer"
                onClick={() => handleProductClick(product)}
              >
                <div className="h-40 flex justify-center items-center mb-2">
                  <img 
                    src={product.img || product.image_url || "/api/placeholder/200/200"} 
                    alt={product.title} 
                    className="max-h-full max-w-full object-contain"
                  />
                </div>
                <h4 className="font-medium text-lg truncate">{product.title}</h4>
                <p className="text-gray-700">{product.price}</p>
                <div className="flex items-center mt-2">
                  <span className="text-yellow-500 mr-1">★</span>
                  <span>{product.rating || 'N/A'}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};