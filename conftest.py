import pytest
import os
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for testing"""
    with patch.dict(os.environ, {
        'MONGO_URI': 'mongodb://test:test@localhost/test',
        'API_KEY': 'test-api-key'
    }):
        yield

@pytest.fixture
def mock_streamlit_session():
    """Mock Streamlit session state"""
    import streamlit as st
    st.session_state.clear()
    return st.session_state