import pytest
import streamlit as st
from unittest.mock import Mock, patch

def test_streamlit_session_fixture(mock_streamlit_session):
    """Test that session state is properly mocked"""
    assert len(mock_streamlit_session) == 0
    mock_streamlit_session['test_key'] = 'test_value'
    assert mock_streamlit_session['test_key'] == 'test_value'

def test_environment_variables():
    """Test that environment variables are properly mocked"""
    import os
    assert os.environ.get('MONGO_URI') == 'mongodb://test:test@localhost/test'
    assert os.environ.get('API_KEY') == 'test-api-key'