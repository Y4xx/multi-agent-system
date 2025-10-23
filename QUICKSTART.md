# 🚀 Quick Start Guide

Get the Multi-Agent Job Application System running in minutes!

## 📋 Prerequisites

- Python 3.8+ installed
- Node.js 18+ installed
- Terminal/Command prompt

## ⚡ Fast Setup (5 minutes)

### Step 1: Start the Backend (Terminal 1)

```bash
# Navigate to backend
cd backend

# Install dependencies (one-time setup)
pip install -r requirements.txt

# Start the server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend should now be running at `http://localhost:8000`

### Step 2: Start the Frontend (Terminal 2)

```bash
# Navigate to frontend (in a NEW terminal)
cd frontend

# Install dependencies (one-time setup)
npm install

# Start development server
npm run dev
```

✅ Frontend should now be running at `http://localhost:5173`

### Step 3: Use the Application

1. Open your browser to `http://localhost:5173`
2. Click "Choose File" and select a CV (PDF, DOCX, or TXT)
3. Click "Upload" - the system will automatically:
   - Parse your CV
   - Find matching jobs
   - Display top 10 matches with scores
4. Click "Generate Letter" on any job to:
   - Create a personalized motivation letter
   - Review and edit if needed
   - Send the application

## 📝 Creating a Test CV

Don't have a CV ready? Create a simple text file:

```bash
cat > sample_cv.txt << 'EOT'
John Smith
john.smith@email.com
+33 6 12 34 56 78

PROFESSIONAL SUMMARY
Experienced Full Stack Developer with 5+ years in Python, React, and TypeScript.

TECHNICAL SKILLS
- Programming: Python, JavaScript, TypeScript
- Frameworks: React, FastAPI, Django
- Cloud: AWS, Docker, Kubernetes
- ML: TensorFlow, scikit-learn

WORK EXPERIENCE
Senior Software Engineer at Tech Solutions Inc.
- Developed web applications with React and FastAPI
- Implemented ML models for data processing

EDUCATION
Master of Science in Computer Science
University of Paris

LANGUAGES
French, English
EOT
```

Then upload this `sample_cv.txt` file!

## 🧪 Test the API Directly

### Health Check
```bash
curl http://localhost:8000/
```

### Get All Jobs
```bash
curl http://localhost:8000/job-offers
```

### Upload CV via API
```bash
curl -X POST "http://localhost:8000/upload-cv" \
  -F "file=@sample_cv.txt"
```

## 🔧 Common Issues

### Backend won't start
- Make sure port 8000 is available
- Check Python version: `python --version` (should be 3.8+)
- Reinstall dependencies: `pip install -r requirements.txt`

### Frontend won't start  
- Make sure port 5173 is available
- Check Node version: `node --version` (should be 18+)
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`

### CORS errors in browser
- Make sure backend is running on port 8000
- Check browser console for actual error
- Try clearing browser cache

## 📧 Email Configuration (Optional)

By default, emails are simulated. To send real emails:

1. Create `.env` file in `backend/` directory
2. Add credentials:
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=your-app-password
   ```
3. Restart backend

## 🎯 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the code in `backend/agents/` to see how agents work
- Customize the UI in `frontend/src/components/`
- Add more job offers in `backend/data/job_offers.json`

## 💡 Tips

- The system includes 15 sample job offers by default
- Match scores show how well your CV matches each job
- You can edit the motivation letter before sending
- All applications are logged (check via API or notifications)

Enjoy your automated job search! 🎉
