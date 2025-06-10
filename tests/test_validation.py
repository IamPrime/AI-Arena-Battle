import pytest
from src.utils.validation import InputValidator

class TestInputValidator:
    def test_valid_prompt(self):
        valid, error = InputValidator.validate_prompt("What is Python?")
        assert valid is True
        assert error is None
    
    def test_empty_prompt(self):
        valid, error = InputValidator.validate_prompt("")
        assert valid is False
        assert "empty" in error.lower()
    
    def test_long_prompt(self):
        long_prompt = "x" * 2001
        valid, error = InputValidator.validate_prompt(long_prompt)
        assert valid is False
        assert "too long" in error.lower()