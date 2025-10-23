# 🤖 Multi-Agent System for Intelligent Job & Internship Discovery and Application Automation

An **AI-powered full-stack application** that automates the entire process of discovering, matching, and applying to jobs or internships — from CV analysis to sending personalized applications.

---

## 🚀 Project Overview

This system uses **multiple intelligent agents** to handle each step of the application process:

1. **Upload a CV** → The system analyzes it.
2. **Fetch job/internship offers** (from dummy data or APIs).
3. **Match the CV** with the best offers.
4. **Display the top 10 matching offers**.
5. **Generate a personalized "lettre de motivation."**
6. **Automatically send job applications via email.**

The entire workflow is managed by a **coordinator agent** that orchestrates all other agents.

---

## 🧠 System Architecture

### **Frontend**
- **Tech Stack:** React + TypeScript + Tailwind CSS + Shadcn/UI
- **Purpose:** User interface for uploading CVs, viewing offers, and sending applications.
- **Communication:** RESTful API calls to FastAPI backend.

### **Backend**
- **Tech Stack:** Python + FastAPI
- **Purpose:** Hosts all agents, APIs, and data processing logic.
- **Database:** SQLite (for future use)
- **Communication:** REST API (CORS enabled)

---

## 🧩 Agents Overview

| Agent | Description |
|--------|-------------|
| `cv_analysis_agent.py` | Parses and extracts structured data from uploaded CVs. |
| `job_fetcher_agent.py` | Fetches job/internship offers (dummy data or external API). |
| `matching_agent.py` | Computes similarity between CV and offers using NLP. |
| `motivation_agent.py` | Generates a personalized "lettre de motivation." |
| `application_agent.py` | Sends job applications via email. |
| `coordinator_agent.py` | Orchestrates the entire workflow between agents. |

---

## 🛠️ Setup Instructions

### Prerequisites

- **Python 3.8+** for backend
- **Node.js 18+** for frontend
- **pip** and **npm** package managers

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables (optional):**
   ```bash
   cp .env.example .env
   # Edit .env to add your email credentials for actual email sending
   # If not configured, emails will be simulated
   ```

4. **Start the backend server:**
   ```bash
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173`

---

## 🎯 Usage Guide

1. **Upload Your CV**
   - Click on the file input to select your CV (PDF, DOCX, or TXT format)
   - Click "Upload" to process your CV
   - The system will automatically extract your information and find matching jobs

2. **Browse Matching Jobs**
   - View the top 10 jobs matched to your CV
   - Each job shows a match score indicating compatibility
   - Jobs are sorted by match score (highest first)

3. **Generate Motivation Letter**
   - Click "Generate Letter" on any job card
   - Review and edit the AI-generated motivation letter
   - The letter is personalized based on your CV and the job requirements

4. **Send Application**
   - Review the generated letter in the preview modal
   - Make any final edits if needed
   - Click "Send Application" to submit your application
   - Receive confirmation notification

---

## 🔗 Backend API Endpoints

| Endpoint | Method | Description |
|-----------|---------|-------------|
| `/` | `GET` | Health check endpoint |
| `/upload-cv` | `POST` | Upload a CV and extract structured data. |
| `/job-offers` | `GET` | Fetch available job/internship offers. |
| `/match-offers` | `POST` | Return top 10 offers matched with the CV. |
| `/generate-letter` | `POST` | Generate a personalized motivation letter. |
| `/apply` | `POST` | Send email applications automatically. |
| `/job/{job_id}` | `GET` | Get specific job by ID. |
| `/applications` | `GET` | Get application history. |

---

## 🧰 Key Features

### Backend Features
- ✅ CV parsing and data extraction (PDF, DOCX, TXT)
- ✅ NLP-based job matching using text similarity
- ✅ Intelligent motivation letter generation
- ✅ Email application automation (with simulation mode)
- ✅ RESTful API with FastAPI
- ✅ CORS enabled for frontend integration
- ✅ Comprehensive error handling

### Frontend Features
- ✅ Modern React + TypeScript application
- ✅ Responsive design with Tailwind CSS
- ✅ Beautiful UI components (Shadcn/UI inspired)
- ✅ Real-time notifications
- ✅ CV upload with file validation
- ✅ Interactive job cards with match scores
- ✅ Letter preview and editing
- ✅ Application status tracking

---

## 📊 Sample Data

The system includes 15 sample job offers in `backend/data/job_offers.json` covering:
- Full-time positions (Python, React, ML, DevOps, etc.)
- Internships (Full-stack, AI/ML Research, Software Engineering)
- Various locations across France
- Different experience levels

---

## 🔒 Email Configuration

By default, the system simulates email sending. To enable actual email sending:

1. Create a `.env` file in the backend directory
2. Add your SMTP credentials:
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=your-app-password
   ```

**Note:** For Gmail, you need to use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

---

## 🧪 Testing

### Test Backend Endpoints

```bash
# Health check
curl http://localhost:8000/

# Get all job offers
curl http://localhost:8000/job-offers

# Upload CV (replace with your file path)
curl -X POST "http://localhost:8000/upload-cv" \
  -F "file=@/path/to/your/cv.pdf"
```

### Test Frontend

1. Open `http://localhost:5173` in your browser
2. Upload a sample CV
3. Browse matched jobs
4. Generate and preview motivation letters
5. Submit applications

---

## 📝 Project Structure

```
multi-agent-system/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── agents/                 # Agent modules
│   │   ├── cv_analysis_agent.py
│   │   ├── job_fetcher_agent.py
│   │   ├── matching_agent.py
│   │   ├── motivation_agent.py
│   │   ├── application_agent.py
│   │   └── coordinator_agent.py
│   ├── services/               # Utility services
│   │   ├── nlp_service.py
│   │   ├── email_service.py
│   │   └── utils.py
│   ├── data/                   # Data files
│   │   ├── job_offers.json
│   │   └── parsed_cv.json
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── components/         # React components
    │   │   ├── UploadCV.tsx
    │   │   ├── OffersList.tsx
    │   │   ├── LetterPreview.tsx
    │   │   ├── ApplicationStatus.tsx
    │   │   └── ui/             # UI components
    │   ├── api/
    │   │   └── apiClient.ts    # API integration
    │   ├── lib/
    │   │   └── utils.ts        # Utilities
    │   ├── App.tsx             # Main app component
    │   └── main.tsx            # Entry point
    ├── package.json
    └── tailwind.config.js
```

---

## 🤝 Contributing

This is a demonstration project showcasing a multi-agent AI system. Feel free to:
- Add more job sources
- Improve the NLP matching algorithm
- Enhance the motivation letter generation
- Add more UI features
- Integrate with real job boards APIs

---

## 📧 Support

For questions or feedback, please open an issue in the repository.

---

**Built with ❤️ using AI-powered agents**
