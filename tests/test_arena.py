import pytest
from unittest.mock import patch, MagicMock
from LegacyArena import store_vote, call_model

def test_store_vote():
    """Test vote storage functionality"""
    with patch('LegacyArena.collection') as mock_collection:
        store_vote("test prompt", "model1", "model2", "A")
        mock_collection.insert_one.assert_called_once()

@patch('LegacyArena.requests.post')
def test_call_model_success(mock_post):
    """Test successful API call"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": {"content": "Test response"}}
    mock_post.return_value = mock_response
    
    result = call_model("test prompt", "test_model")
    assert result == "Test response"

@patch('LegacyArena.requests.post')
def test_call_model_error(mock_post):
    """Test API error handling"""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Server Error"
    mock_post.return_value = mock_response
    
    result = call_model("test prompt", "test_model")
    assert "[Error 500:" in result