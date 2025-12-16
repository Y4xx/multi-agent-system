# 🚀 CrewAI Deployment Guide

Complete guide for deploying the CrewAI-powered Multi-Agent Job Application System.

## 📋 Prerequisites

- Python 3.8+
- pip package manager
- OpenAI API key
- (Optional) SMTP email account for real email sending

## 🔧 Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/Y4xx/multi-agent-system.git
cd multi-agent-system/backend
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Key dependencies installed:
- `crewai==0.28.8` - Multi-agent framework
- `langchain-openai==0.0.5` - OpenAI LLM integration
- `fastapi==0.104.1` - Web framework
- `python-dotenv==1.0.0` - Environment variable management

### 4. Configure Environment Variables

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Required Configuration:**

```bash
# LLM Configuration (REQUIRED)
OPENAI_API_KEY=sk-your-actual-openai-api-key
MODEL_NAME=gpt-4o-mini

# Email Configuration (OPTIONAL - for real email sending)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

**Getting an OpenAI API Key:**
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create new secret key
5. Copy and paste into `.env` file

**Email Configuration Notes:**
- If not configured, system will simulate email sending
- For Gmail, use [App Password](https://support.google.com/accounts/answer/185833), not regular password
- For other providers, update SMTP_SERVER and SMTP_PORT accordingly

### 5. Verify Installation

```bash
# Test imports
python -c "from crew.crew import job_application_crew; print('✓ Installation successful')"
```

## 🏃 Running the Application

### Development Mode

```bash
# Start FastAPI server with auto-reload
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at: `http://localhost:8000`

### Production Mode

```bash
# Use gunicorn for production
pip install gunicorn

# Run with multiple workers
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker (Alternative)

```dockerfile
# Create Dockerfile in backend/
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t job-app-crewai .
docker run -p 8000:8000 --env-file .env job-app-crewai
```

## 🧪 Testing the Deployment

### 1. Health Check

```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "message": "Multi-Agent Job Application System API (CrewAI-powered)",
  "status": "running",
  "version": "2.0.0",
  "architecture": "CrewAI Multi-Agent System"
}
```

### 2. Test Job Offers

```bash
curl http://localhost:8000/job-offers
```

Should return list of 15 job offers.

### 3. Test CV Upload

```bash
curl -X POST http://localhost:8000/upload-cv \
  -F "file=@/path/to/your/cv.pdf"
```

### 4. Test Cover Letter Generation

```bash
curl -X POST http://localhost:8000/generate-letter \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {
      "name": "Test User",
      "skills": ["Python", "React"],
      "experience": [],
      "education": []
    },
    "job_id": 1
  }'
```

This will generate a French cover letter using the LLM.

## 📊 API Documentation

Once running, access interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔒 Security Considerations

### API Key Security

1. **Never commit `.env` file** - Already in `.gitignore`
2. **Use environment variables** in production
3. **Rotate keys regularly**
4. **Set usage limits** on OpenAI dashboard

### Email Security

1. **Use App Passwords** for Gmail
2. **Enable 2FA** on email account
3. **Consider simulation mode** for testing
4. **Validate recipient emails** before sending

### Rate Limiting

Consider adding rate limiting in production:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/generate-letter")
@limiter.limit("10/hour")  # Limit LLM calls
async def generate_letter(request: Request, ...):
    ...
```

## 🌐 Frontend Integration

The backend is designed to work with the existing React frontend without changes.

### CORS Configuration

Already configured for:
- `http://localhost:3000` (React default)
- `http://localhost:5173` (Vite default)

Add more origins if needed in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://your-production-domain.com"
    ],
    ...
)
```

## 📈 Monitoring

### Logging

Add structured logging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

### OpenAI API Usage

Monitor your usage at: https://platform.openai.com/usage

### Application Metrics

Consider adding:
- Request count per endpoint
- Response times
- Error rates
- LLM token usage

## 🐛 Troubleshooting

### Issue: "OPENAI_API_KEY not found"

**Solution:** 
- Ensure `.env` file exists in backend directory
- Check API key is correctly formatted: `OPENAI_API_KEY=sk-...`
- Restart the server after updating `.env`

### Issue: "No module named 'crewai'"

**Solution:**
```bash
pip install crewai==0.28.8
```

### Issue: "Connection refused to OpenAI API"

**Solution:**
- Check internet connection
- Verify API key is valid
- Check OpenAI service status: https://status.openai.com/

### Issue: Cover letters not in French

**Solution:**
- Verify using correct model (gpt-4o-mini or gpt-4)
- Check task description in `crew/tasks.py` has French instructions
- Ensure temperature is reasonable (0.7)

### Issue: "No space left on device" during pip install

**Solution:**
```bash
# Clean pip cache
pip cache purge

# Install without cache
pip install --no-cache-dir -r requirements.txt
```

## 🔄 Updating

### Update Dependencies

```bash
pip install --upgrade -r requirements.txt
```

### Update CrewAI

```bash
pip install --upgrade crewai
```

### Database Migrations

Currently using JSON files. For future SQL database:
```bash
# Will be added when migrating to SQL
alembic upgrade head
```

## 📦 Production Checklist

- [ ] Environment variables configured
- [ ] OpenAI API key is valid and has credits
- [ ] CORS origins include production domain
- [ ] Rate limiting implemented
- [ ] Logging configured
- [ ] Error handling tested
- [ ] Backup strategy for job data
- [ ] Monitoring setup
- [ ] SSL/TLS certificate configured
- [ ] Database backups (if using SQL)

## 🎯 Performance Optimization

### 1. Caching

Consider caching job offers:

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def get_cached_jobs():
    return job_fetcher_agent.fetch_all_jobs()
```

### 2. Async Operations

Most operations are already async-compatible via FastAPI.

### 3. LLM Response Caching

For repeated similar requests:

```python
from langchain.cache import InMemoryCache
import langchain
langchain.llm_cache = InMemoryCache()
```

## 💰 Cost Management

### OpenAI API Costs

**gpt-4o-mini pricing (as of Dec 2024):**
- Input: ~$0.15 per 1M tokens
- Output: ~$0.60 per 1M tokens

**Estimated costs per cover letter:**
- Average: ~500 tokens input + 300 tokens output
- Cost: ~$0.0003 per letter
- 1000 letters: ~$0.30

**Cost optimization tips:**
1. Use `gpt-4o-mini` instead of `gpt-4` (10x cheaper)
2. Implement caching for similar requests
3. Set usage limits on OpenAI dashboard
4. Monitor token usage in logs

## 📞 Support

For issues or questions:
1. Check [GitHub Issues](https://github.com/Y4xx/multi-agent-system/issues)
2. Review [crew/README.md](crew/README.md) for module documentation
3. Check [SAMPLE_COVER_LETTER.md](SAMPLE_COVER_LETTER.md) for examples

## 🎓 Additional Resources

- [CrewAI Documentation](https://docs.crewai.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
