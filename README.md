# 🤖 ComplexFlow-Arena — LLM Battle Platform

A Streamlit application for comparing LLM responses with anonymous voting.

## 🚀 Quick Start

1. **Setup Environment**

    ```bash
    cp .env.example .env
    # Edit .env with your credentials
    ```

2. **Run with Docker**

    ```bash
    docker build -t complexflow-arena .
    docker run --env-file .env -p 8501:8501 complexflow-arena
    ```

3. **Access**: <http://localhost:8501>

## 📚 Full Documentation

- [Complete Setup Guide](docs/DOCUMENTATION.md)
- [API Documentation](docs/API.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
