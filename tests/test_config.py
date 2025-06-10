import os
import pytest
from LegacyArena import MONGO_URI, API_KEY

def test_environment_variables():
    """Ensure required environment variables are set"""
    assert MONGO_URI is not None, "MONGO_URI not set"
    assert API_KEY is not None, "API_KEY not set"
    assert MONGO_URI.startswith("mongodb"), "Invalid MongoDB URI format"

def test_model_pool_validity():
    """Test model pool configuration"""
    from LegacyArena import model_pool
    assert len(model_pool) > 0, "Model pool is empty"
    assert all(isinstance(model, str) for model in model_pool), "Model pool contains non-string values"