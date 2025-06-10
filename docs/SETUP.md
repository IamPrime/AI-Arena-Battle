# 🚀 Setup Documentation

## 📋 Prerequisites

Before starting, ensure you have:

- **Docker Desktop** (version 4.0 or higher)
  - [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
  - Verify installation: `docker --version`
- **MongoDB Atlas account**
  - [Create free account](https://www.mongodb.com/cloud/atlas/register)
  - Set up a cluster and obtain connection string
- **Purdue RCAC GenAI Studio API access token**
  - Contact RCAC staff for API access
  - Token format: `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM       | 4GB     | 8GB+        |
| Storage   | 2GB     | 5GB+        |
| CPU       | 2 cores | 4+ cores    |

## ⚙️ Environment Configuration

### 1. Clone the Repository

```bash
git clone https://github.rcac.purdue.edu/RCAC-Staff/ComplexFlow-Arena.git
cd ComplexFlow-Arena
```

### 2. Create Environment File

Create a `.env` file in the project root directory:

> ⚠️ **Important**: Keep the structure exactly as shown. Do not change the position or format of variables.

```env
# MongoDB Atlas connection string
MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority&appName=<app-name>

# API Key for RCAC GenAI Studio
API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional: Debug logging level (uncomment for development)
# STREAMLIT_LOGGER_LEVEL=debug
```

### 3. Configure MongoDB Atlas

1. **Create a new cluster** in MongoDB Atlas
2. **Set up database user**:
   - Go to Database Access
   - Add new database user with read/write permissions
3. **Configure network access**:
   - Go to Network Access
   - Add IP address (0.0.0.0/0 for development, specific IPs for production)
4. **Get connection string**:
   - Go to Clusters → Connect → Connect your application
   - Copy the connection string and replace `<username>`, `<password>`, and `<cluster>` in your `.env` file

### Environment Variables Reference

| Variable                 | Description                     | Required | Default |
|-------------------------|---------------------------------|----------|---------|
| `MONGO_URI`             | MongoDB Atlas connection string | ✅ Yes   | None    |
| `API_KEY`               | RCAC GenAI Studio API key       | ✅ Yes   | None    |
| `STREAMLIT_LOGGER_LEVEL`| Debug logging level             | ❌ No    | info    |
| `SHOW_DEBUG`            | Show debug info in UI           | ❌ No    | false   |

## 🐳 Docker Deployment (Recommended)

### Quick Start

1. **Copy example environment file**:

    ```bash
    cp .env.example .env
    ```

2. **Edit environment file with your credentials**:

    ```bash
    nano .env
    # or use your preferred text editor
    ```

3. **Build the Docker image**:

    ```bash
    docker build -t complexflow-arena .
    ```

4. **Run the container**:

    ```bash
    docker run --env-file .env -p 8501:8501 complexflow-arena
    ```

5. **Access the application**:
   - Open your browser and navigate to: <http://localhost:8501>

### Advanced Docker Options

#### Run with Custom Port

```bash
docker run --env-file .env -p 8080:8501 complexflow-arena
# Access at: http://localhost:8080
```

#### Run with Volume Mounting (Development)

```bash
docker run --env-file .env -p 8501:8501 -v $(pwd):/app complexflow-arena
```

#### Run in Background (Detached Mode)

```bash
docker run -d --name complexflow-arena --env-file .env -p 8501:8501 complexflow-arena
```

#### View Container Logs

```bash
docker logs complexflow-arena
```

#### Stop and Remove Container

```bash
docker stop complexflow-arena
docker rm complexflow-arena
```

## 💻 Local Development Setup

### 1. Install Python Dependencies

Ensure you have Python 3.8+ installed:

```bash
python --version
```

Install required packages:

```bash
python -m venv venv # Optionally create a virtual environment
source venv/Scripts/activate # Activate the virtual environment
pip install pip-tools
pip-compile requirements.in
pip install -r requirements.txt
```

### 2. Set Environment Variables

For Unix/Linux/macOS:

```bash
export MONGO_URI="your_mongodb_connection_string"
export API_KEY="your_api_key"
export SHOW_DEBUG=true  # Optional: "false" for development
```

For Windows (Command Prompt):

```cmd
set MONGO_URI=your_mongodb_connection_string
set API_KEY=your_api_key
set SHOW_DEBUG=true # Optional: "false" for development
```

For Windows (PowerShell):

```powershell
$env:MONGO_URI="your_mongodb_connection_string"
$env:API_KEY="your_api_key"
$env:SHOW_DEBUG="true" # Optional: "false" for development
```

### 3. Run the Application

```bash
streamlit run Arena.py
```

### Development with Debug Mode

Enable debug logging:

```bash
streamlit run Arena.py --logger.level debug
```

Or set in environment:

```bash
export STREAMLIT_LOGGER_LEVEL=debug
streamlit run Arena.py
```

## ✅ Verification & Testing

After setup, verify everything is working correctly:

### 1. Basic Functionality Test

1. ✅ Navigate to <http://localhost:8501>
2. ✅ Application loads without errors
3. ✅ Enter a test prompt (e.g., "Hello, how are you?")
4. ✅ Verify two model responses appear
5. ✅ Test the voting functionality (A, B, Tie, Both are bad)
6. ✅ Confirm votes are saved (no error messages appear)

### 2. Database Verification

Check MongoDB Atlas dashboard:

1. ✅ Navigate to your MongoDB Atlas cluster
2. ✅ Browse collections
3. ✅ Verify new vote entries appear after testing

### 3. Debug Information

If `SHOW_DEBUG=true` is set:

1. ✅ Debug panel appears in sidebar
2. ✅ Check for any error messages
3. ✅ Verify API response times are reasonable

### 4. API Connectivity Test

Test API connection manually:

```bash
curl -X POST "https://genai.rcac.purdue.edu/api/chat/completions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:70b-instruct-q4_K_M",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": false
  }'
```

## 🔄 Updates and Maintenance

### Updating the Application

#### Docker Update

```bash
# Pull latest image
docker pull complexflow-arena:latest

# Stop current container
docker stop complexflow-arena
docker rm complexflow-arena

# Run updated container
docker run -d --name complexflow-arena --env-file .env -p 8501:8501 complexflow-arena:latest
```

#### Local Development Update

```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart application
streamlit run Arena.py
```

### Backup and Security

#### Environment File Security

- ✅ Never commit `.env` files to version control
- ✅ Store backup of `.env` file securely
- ✅ Rotate API keys regularly
- ✅ Use environment-specific configurations

#### MongoDB Maintenance

- ✅ Monitor MongoDB Atlas storage usage
- ✅ Set up automated backups in Atlas
- ✅ Review and rotate database credentials periodically

#### Docker Security

```bash
# Remove unused images
docker image prune

# Remove unused containers
docker container prune

# View resource usage
docker stats
```

## 🆘 Quick Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Port 8501 already in use | Use different port: `-p 8080:8501` |
| Environment variables not found | Check `.env` file exists and format |
| MongoDB connection failed | Verify connection string and network access |
| API key invalid | Check API key format starts with `sk-` |
| Docker build fails | Ensure Docker Desktop is running |

### Getting Help

1. **Check logs**: `docker logs complexflow-arena`
2. **Review troubleshooting guide**: See `docs/TROUBLESHOOTING.md`
3. **Contact support**: Reach out to RCAC staff for API issues

## 📚 Next Steps

After successful setup:

1. 📖 Read the [API Documentation](API.md)
2. 🛠️ Review [Troubleshooting Guide](TROUBLESHOOTING.md)
3. 🧪 Explore different model comparisons
4. 📊 Monitor usage and performance

---

> 💡 **Tip**: For production deployment, consider using Docker Compose for easier management and additional services like reverse proxy or monitoring.
