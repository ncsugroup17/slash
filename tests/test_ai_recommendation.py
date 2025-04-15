import pytest
import json
from unittest.mock import patch, MagicMock
import pandas as pd
from flask import Flask
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.modules.app import app, db, searchWalmart

@pytest.fixture
def client():
    """Creating a test client for the Flask application."""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    
    with app.test_client() as client:
        with app.app_context():
            yield client

# AI Recommendations Tests
def test_ai_recommendations_options_method(client):
    """Test that the AI recommendations route handles OPTIONS method."""
    with patch('src.modules.app.make_response', return_value=('', 200)):
        response = client.options('/ai-recommendations')
        assert response.status_code == 200

def test_ai_recommendations_invalid_conversation(client):
    """Test handling of invalid conversation data."""
    response = client.post('/ai-recommendations', json={'conversation': 'not_a_list'})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Invalid conversation data'

def test_ai_recommendations_empty_conversation(client):
    """Test handling of empty conversation list."""
    response = client.post('/ai-recommendations', json={'conversation': []})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Invalid conversation data'

def test_ai_recommendations_groq_api_error(client):
    """Test handling of Groq API errors."""
    valid_conversation = [{'role': 'user', 'content': 'Hello'}]
    
    with patch('src.modules.app.create_system_prompt', return_value="test prompt"):
        with patch('src.modules.app.rq.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_post.return_value = mock_response
            
            with patch('src.modules.app.app.logger.error') as mock_logger:
                response = client.post('/ai-recommendations', json={'conversation': valid_conversation})
                assert response.status_code == 500
                data = json.loads(response.data)
                assert 'error' in data
                assert data['error'] == 'AI service error'
                mock_logger.assert_called_once()

def test_ai_recommendations_success_with_recommendations(client):
    """Test successful recommendations when AI determines user is ready for recommendations."""
    valid_conversation = [{'role': 'user', 'content': 'I need a laptop'}]
    
    with patch('src.modules.app.create_system_prompt', return_value="test prompt"):
        with patch('src.modules.app.rq.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'choices': [
                    {
                        'message': {
                            'content': json.dumps({
                                'isReadyForRecommendations': True,
                                'searchQuery': 'laptop'
                            })
                        }
                    }
                ]
            }
            mock_post.return_value = mock_response
            
            with patch('src.modules.app.session', {'username': 'test@example.com'}):
                with patch('src.modules.app.db.get_user_id_by_email', return_value=1):
                    with patch('src.modules.app.db.log_search'):
                        with patch('src.modules.app.searchWalmart') as mock_search:
                            mock_search.return_value = [
                                {
                                    'title': 'Test Laptop',
                                    'price': '$999.99',
                                    'rating': '4.5',
                                    'img_link': 'http://example.com/img.jpg',
                                    'link': 'http://example.com/product'
                                }
                            ]
                            
                            response = client.post('/ai-recommendations', json={'conversation': valid_conversation})
                            assert response.status_code == 200
                            data = json.loads(response.data)
                            assert 'response' in data
                            assert 'recommendations' in data
                            assert len(data['recommendations']) == 1
                            assert data['recommendations'][0]['title'] == 'Test Laptop'

def test_ai_recommendations_search_error(client):
    """Test handling of search errors when trying to fetch products."""
    valid_conversation = [{'role': 'user', 'content': 'I need a laptop'}]
    
    with patch('src.modules.app.create_system_prompt', return_value="test prompt"):
        with patch('src.modules.app.rq.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'choices': [
                    {
                        'message': {
                            'content': json.dumps({
                                'isReadyForRecommendations': True,
                                'searchQuery': 'laptop'
                            })
                        }
                    }
                ]
            }
            mock_post.return_value = mock_response
            
            with patch('src.modules.app.session', {'username': 'test@example.com'}):
                with patch('src.modules.app.db.get_user_id_by_email', return_value=1):
                    with patch('src.modules.app.db.log_search'):
                        with patch('src.modules.app.searchWalmart', side_effect=Exception("Search error")):
                            with patch('src.modules.app.app.logger.error') as mock_logger:
                                response = client.post('/ai-recommendations', json={'conversation': valid_conversation})
                                assert response.status_code == 200
                                data = json.loads(response.data)
                                assert 'response' in data
                                assert data['response'] == 'Oops! Something went wrong while searching for your products.'
                                assert data['recommendations'] == []
                                mock_logger.assert_called_once()

def test_ai_recommendations_continue_conversation(client):
    """Test when AI decides to continue the conversation (not ready for recommendations)."""
    valid_conversation = [{'role': 'user', 'content': 'I need a laptop'}]
    
    with patch('src.modules.app.create_system_prompt', return_value="test prompt"):
        with patch('src.modules.app.rq.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'choices': [
                    {
                        'message': {
                            'content': json.dumps({
                                'isReadyForRecommendations': False,
                                'response': 'What kind of laptop are you looking for?',
                                'nextQuestion': 'What will you use the laptop for?'
                            })
                        }
                    }
                ]
            }
            mock_post.return_value = mock_response
            
            response = client.post('/ai-recommendations', json={'conversation': valid_conversation})
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['response'] == 'What kind of laptop are you looking for?'
            assert data['nextQuestion'] == 'What will you use the laptop for?'
            assert data['recommendations'] == []

def test_ai_recommendations_log_search_error(client):
    """Test handling of errors during search logging."""
    valid_conversation = [{'role': 'user', 'content': 'I need a laptop'}]
    
    with patch('src.modules.app.create_system_prompt', return_value="test prompt"):
        with patch('src.modules.app.rq.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'choices': [
                    {
                        'message': {
                            'content': json.dumps({
                                'isReadyForRecommendations': True,
                                'searchQuery': 'laptop'
                            })
                        }
                    }
                ]
            }
            mock_post.return_value = mock_response
            
            with patch('src.modules.app.session', {'username': 'test@example.com'}):
                with patch('src.modules.app.db.get_user_id_by_email', side_effect=Exception("DB error")):
                    with patch('builtins.print') as mock_print:
                        with patch('src.modules.app.searchWalmart') as mock_search:
                            mock_search.return_value = []
                            
                            response = client.post('/ai-recommendations', json={'conversation': valid_conversation})
                            assert response.status_code == 200
                            data = json.loads(response.data)
                            assert 'response' in data
                            assert 'recommendations' in data
                            assert mock_print.call_count >= 1
                            error_calls = [call for call in mock_print.call_args_list if "Logging search failed" in str(call)]
                            assert len(error_calls) > 0

# Personalized Recommendations Tests
def test_personalized_recommendations_unauthenticated(client):
    """Test handling of unauthenticated requests for personalized recommendations."""
    with patch('src.modules.app.session', {}):
        response = client.get('/personalized-recommendations')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Authentication required'

def test_personalized_recommendations_user_not_found(client):
    """Test handling when the authenticated user is not found in the database."""
    with patch('src.modules.app.session', {'username': 'test@example.com'}):
        with patch('src.modules.app.db.get_user_id_by_email', return_value=None):
            response = client.get('/personalized-recommendations')
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data
            assert data['error'] == 'User not found'

def test_personalized_recommendations_no_search_history(client):
    """Test handling when the user has no search history."""
    with patch('src.modules.app.session', {'username': 'test@example.com'}):
        with patch('src.modules.app.db.get_user_id_by_email', return_value=1):
            with patch('src.modules.app.db.get_search_history', return_value=[]):
                response = client.get('/personalized-recommendations')
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['response'] == "Please search for something first using the AI Recommendation search"
                assert data['recommendations'] == []

def test_personalized_recommendations_groq_api_error(client):
    """Test handling of Groq API errors when processing search queries."""
    search_history = [(1, 1, 'laptop', '', 0, '2023-01-01')]
    
    with patch('src.modules.app.session', {'username': 'test@example.com'}):
        with patch('src.modules.app.db.get_user_id_by_email', return_value=1):
            with patch('src.modules.app.db.get_search_history', return_value=search_history):
                with patch('builtins.print'):
                    with patch('src.modules.app.rq.post') as mock_post:
                        mock_response = MagicMock()
                        mock_response.status_code = 500
                        mock_response.text = "Internal Server Error"
                        mock_post.return_value = mock_response
                        
                        response = client.get('/personalized-recommendations')
                        assert response.status_code == 200
                        data = json.loads(response.data)
                        assert data['response'] == 'Failed to process your history for recommendations.'

def test_personalized_recommendations_groq_parsing_error(client):
    """Test handling of errors when parsing the Groq API response."""
    search_history = [(1, 1, 'laptop', '', 0, '2023-01-01')]
    
    with patch('src.modules.app.session', {'username': 'test@example.com'}):
        with patch('src.modules.app.db.get_user_id_by_email', return_value=1):
            with patch('src.modules.app.db.get_search_history', return_value=search_history):
                with patch('src.modules.app.rq.post') as mock_post:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {
                        'choices': [
                            {
                                'message': {
                                    'content': 'not_valid_json'
                                }
                            }
                        ]
                    }
                    mock_post.return_value = mock_response
                    
                    with patch('builtins.print'):
                        response = client.get('/personalized-recommendations')
                        assert response.status_code == 200
                        data = json.loads(response.data)
                        assert data['response'] == 'Could not parse AI-generated search suggestions.'

def test_personalized_recommendations_search_error(client):
    """Test handling of errors during product search."""
    search_history = [(1, 1, 'laptop', '', 0, '2023-01-01')]
    
    with patch('src.modules.app.session', {'username': 'test@example.com'}):
        with patch('src.modules.app.db.get_user_id_by_email', return_value=1):
            with patch('src.modules.app.db.get_search_history', return_value=search_history):
                with patch('src.modules.app.rq.post') as mock_post:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {
                        'choices': [
                            {
                                'message': {
                                    'content': json.dumps({
                                        'converted': ['laptop']
                                    })
                                }
                            }
                        ]
                    }
                    mock_post.return_value = mock_response
                    
                    with patch('builtins.print'):
                        with patch('src.modules.app.searchWalmart', side_effect=Exception("Search error")):
                            response = client.get('/personalized-recommendations')
                            assert response.status_code == 200
                            data = json.loads(response.data)
                            assert data['response'] == "Here are some personalized picks based on your past searches:"
                            assert data['recommendations'] == []

def test_personalized_recommendations_success(client):
    """Test successful personalized recommendations with valid data."""
    search_history = [(1, 1, 'laptop', '', 0, '2023-01-01')]
    
    with patch('src.modules.app.session', {'username': 'test@example.com'}):
        with patch('src.modules.app.db.get_user_id_by_email', return_value=1):
            with patch('src.modules.app.db.get_search_history', return_value=search_history):
                with patch('src.modules.app.rq.post') as mock_post:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {
                        'choices': [
                            {
                                'message': {
                                    'content': json.dumps({
                                        'converted': ['laptop']
                                    })
                                }
                            }
                        ]
                    }
                    mock_post.return_value = mock_response
                    
                    with patch('builtins.print'):
                        with patch('src.modules.app.searchWalmart') as mock_search:
                            products = [
                                {
                                    'title': 'Test Laptop 1',
                                    'price': '$999.99',
                                    'rating': '4.5',
                                    'img_link': 'http://example.com/img1.jpg',
                                    'link': 'http://example.com/product1'
                                },
                                {
                                    'title': 'Test Laptop 2',
                                    'price': '$1099.99',
                                    'rating': '4.7',
                                    'img_link': 'http://example.com/img2.jpg',
                                    'link': 'http://example.com/product2'
                                },
                                {
                                    'title': 'Test Laptop 3',
                                    'price': '$899.99',
                                    'rating': '4.3',
                                    'img_link': 'http://example.com/img3.jpg',
                                    'link': 'http://example.com/product3'
                                }
                            ]
                            mock_search.return_value = products
                            
                            response = client.get('/personalized-recommendations')
                            assert response.status_code == 200
                            data = json.loads(response.data)
                            assert 'response' in data
                            assert 'recommendations' in data
                            assert len(data['recommendations']) > 0

def test_personalized_recommendations_multiple_queries(client):
    """Test personalized recommendations with multiple search queries."""
    search_history = [
        (1, 1, 'laptop', '', 0, '2023-01-01'),
        (2, 1, 'headphones', '', 0, '2023-01-02'),
        (3, 1, 'mouse', '', 0, '2023-01-03')
    ]
    
    with patch('src.modules.app.session', {'username': 'test@example.com'}):
        with patch('src.modules.app.db.get_user_id_by_email', return_value=1):
            with patch('src.modules.app.db.get_search_history', return_value=search_history):
                with patch('src.modules.app.rq.post') as mock_post:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {
                        'choices': [
                            {
                                'message': {
                                    'content': json.dumps({
                                        'converted': ['laptop', 'headphones', 'mouse']
                                    })
                                }
                            }
                        ]
                    }
                    mock_post.return_value = mock_response
                    
                    with patch('builtins.print'):
                        # Different return values for different search queries
                        search_call_count = [0]  # Using a list to allow modification in the nested function
                        
                        def mock_search_side_effect(*args, **kwargs):
                            search_call_count[0] += 1
                            query = args[0]
                            if query == 'laptop':
                                return [{'title': 'Laptop 1'}, {'title': 'Laptop 2'}, {'title': 'Laptop 3'}]
                            elif query == 'headphones':
                                return [{'title': 'Headphones 1'}, {'title': 'Headphones 2'}, {'title': 'Headphones 3'}]
                            elif query == 'mouse':
                                return [{'title': 'Mouse 1'}, {'title': 'Mouse 2'}, {'title': 'Mouse 3'}]
                            return []
                        
                        with patch('src.modules.app.searchWalmart', side_effect=mock_search_side_effect):
                            response = client.get('/personalized-recommendations')
                            assert response.status_code == 200
                            data = json.loads(response.data)
                            assert 'response' in data
                            assert 'recommendations' in data
                            # Should have called searchWalmart for each query
                            assert search_call_count[0] == 3

def test_personalized_recommendations_with_five_query_limit(client):
    """Test that personalized recommendations only uses the first 5 queries even if more are available."""
    # Create 10 search queries
    search_history = [(i, 1, f'query{i}', '', 0, f'2023-01-{i:02d}') for i in range(1, 11)]
    
    with patch('src.modules.app.session', {'username': 'test@example.com'}):
        with patch('src.modules.app.db.get_user_id_by_email', return_value=1):
            with patch('src.modules.app.db.get_search_history', return_value=search_history):
                with patch('src.modules.app.rq.post') as mock_post:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    # Return 10 converted queries
                    mock_response.json.return_value = {
                        'choices': [
                            {
                                'message': {
                                    'content': json.dumps({
                                        'converted': [f'query{i}' for i in range(1, 11)]
                                    })
                                }
                            }
                        ]
                    }
                    mock_post.return_value = mock_response
                    
                    with patch('builtins.print'):
                        search_call_count = [0]
                        
                        def mock_search(*args, **kwargs):
                            search_call_count[0] += 1
                            return []
                        
                        with patch('src.modules.app.searchWalmart', side_effect=mock_search):
                            response = client.get('/personalized-recommendations')
                            assert response.status_code == 200
                            
                            assert search_call_count[0] <= 5

def test_personalized_recommendations_dataframe_result(client):
    """Test handling of DataFrame results from searchWalmart."""
    search_history = [(1, 1, 'laptop', '', 0, '2023-01-01')]
    
    with patch('src.modules.app.session', {'username': 'test@example.com'}):
        with patch('src.modules.app.db.get_user_id_by_email', return_value=1):
            with patch('src.modules.app.db.get_search_history', return_value=search_history):
                with patch('src.modules.app.rq.post') as mock_post:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {
                        'choices': [
                            {
                                'message': {
                                    'content': json.dumps({
                                        'converted': ['laptop']
                                    })
                                }
                            }
                        ]
                    }
                    mock_post.return_value = mock_response
                    
                    with patch('builtins.print'):
                        # Return a DataFrame from searchWalmart
                        def mock_search_df(*args, **kwargs):
                            df = pd.DataFrame([
                                {'title': 'Laptop 1', 'price': '$999.99', 'rating': '4.5', 'img_link': 'img1.jpg', 'link': 'product1'},
                                {'title': 'Laptop 2', 'price': '$1099.99', 'rating': '4.7', 'img_link': 'img2.jpg', 'link': 'product2'}
                            ])
                            return df
                        
                        with patch('src.modules.app.searchWalmart', side_effect=mock_search_df):
                            response = client.get('/personalized-recommendations')
                            assert response.status_code == 200
                            data = json.loads(response.data)
                            assert 'response' in data
                            assert 'recommendations' in data
                            # Should convert DataFrame to list
                            assert isinstance(data['recommendations'], list)