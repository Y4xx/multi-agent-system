# 🤖 Multi-Agent System for Intelligent Job & Internship Discovery and Application Automation

An **AI-powered full-stack application** powered by **CrewAI** that automates the entire process of discovering, matching, and applying to jobs or internships — from CV analysis to sending **LLM-generated French cover letters**.

> **🆕 Now powered by CrewAI with OpenAI LLM integration for professional French cover letter generation!**

---

## 🚀 Project Overview

This system uses **CrewAI multi-agent framework** with **OpenAI's LLM** to handle each step of the application process:

1. **Upload a CV** → The system analyzes it.
2. **Fetch job/internship offers** (from database or APIs).
3. **Match the CV** with the best offers using NLP.
4. **Display the top 10 matching offers**.
5. **Generate a personalized French "lettre de motivation"** using AI (LLM).
6. **Automatically send job applications via email.**

The entire workflow is managed by a **CrewAI-based coordinator agent** that orchestrates all other specialized agents.

---

## 🧠 System Architecture

### **Frontend**
- **Tech Stack:** React + TypeScript + Tailwind CSS + Shadcn/UI
- **Purpose:** User interface for uploading CVs, viewing offers, and sending applications.
- **Communication:** RESTful API calls to FastAPI backend.

### **Backend (CrewAI-Powered)**
- **Tech Stack:** Python + FastAPI + CrewAI + OpenAI + LangChain
- **Architecture:** Multi-agent system with LLM integration
- **Purpose:** Hosts all agents, APIs, and data processing logic.
- **Database:** JSON (SQLite for future use)
- **Communication:** REST API (CORS enabled)

---

## 🤖 CrewAI Agents Overview

| Agent | Role | Capabilities |
|-------|------|--------------|
| **CV Analysis Agent** | CV Analysis Specialist | Parses and extracts structured data from CVs (PDF, DOCX, TXT) |
| **Job Fetcher Agent** | Job Market Researcher | Fetches and filters job offers by type, location, or keyword |
| **Matching Agent** | Job Match Analyst | Computes similarity scores and ranks jobs by compatibility |
| **Cover Letter Agent** | Expert French Writer | **Generates personalized French cover letters using LLM** |
| **Application Agent** | Submission Specialist | Prepares and sends job applications via email |
| **Coordinator Agent** | Workflow Manager | Orchestrates the entire workflow between agents |

### 🌟 Key Feature: Groq-Powered Skill-Matching Cover Letters

The **Cover Letter Agent** uses Groq's ultra-fast LLM (Mixtral-8x7B) with skill-matching to generate:
- ✅ **Skill-matching driven**: Analyzes CV skills vs. job requirements
- ✅ **Ultra-targeted**: Highlights only concrete, relevant experiences
- ✅ **Professional structure**: Strict format without clichés
- ✅ **ATS-optimized**: PDF export with proper formatting
- ✅ **PDF generation**: Modern, professional PDF documents
- ✅ **Text normalization**: Ensures PDF compatibility
- ✅ **Match reports**: Detailed skill analysis for each job

[See example cover letter](backend/SAMPLE_COVER_LETTER.md)

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

3. **Configure environment variables (REQUIRED for LLM):**
   ```bash
   cp .env.example .env
   # Edit .env to add your OpenAI API key and email credentials
   ```
   
   **Required in `.env` file:**
   ```bash
   # LLM Configuration (REQUIRED)
   OPENAI_API_KEY=sk-your-actual-openai-api-key
   MODEL_NAME=gpt-4o-mini
   
   # Groq Configuration (REQUIRED for cover letter generation)
   GROQ_API_KEY=gsk-your-actual-groq-api-key
   
   # Email Configuration (OPTIONAL - for actual email sending)
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=your-app-password
   
   # Google OAuth 2.0 Configuration (OPTIONAL - for Gmail API integration)
   GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
   ```
   
   > **Get OpenAI API Key:** Visit [OpenAI Platform](https://platform.openai.com/) to create an account and generate an API key.
   
   > **Get Groq API Key:** Visit [Groq Console](https://console.groq.com/) to create an account and generate an API key for ultra-fast LLM inference.
   
   > **Get Google OAuth Credentials:** Visit [Google Cloud Console](https://console.cloud.google.com/) to create OAuth 2.0 credentials for Gmail API access.

4. **Start the backend server:**
   ```bash
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   The backend will be available at `http://localhost:8000`
   
   > **📖 For detailed deployment instructions, see [DEPLOYMENT_GUIDE.md](backend/DEPLOYMENT_GUIDE.md)**

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
   - Jobs support both old and new data formats seamlessly

3. **Configure Gmail Integration (Optional)**
   - Navigate to Settings page
   - Click "Connect Gmail Account"
   - Authorize the application to send emails on your behalf
   - Once connected, applications will be sent from your Gmail address

4. **Generate Motivation Letter**
   - Click "Generate Letter" on any job card
   - Review and edit the AI-generated motivation letter
   - The letter is personalized based on your CV and the job requirements

5. **Send Application**
   - Review the generated letter in the preview modal
   - Make any final edits if needed
   - Click "Send Application" to submit your application
   - If Gmail is connected, the email will be sent from your account
   - Receive confirmation notification

---

## 🔗 Backend API Endpoints

| Endpoint | Method | Description |
|-----------|---------|-------------|
| `/` | `GET` | Health check endpoint |
| `/upload-cv` | `POST` | Upload a CV and extract structured data. |
| `/job-offers` | `GET` | Fetch available job/internship offers. |
| `/match-offers` | `POST` | Return top 10 offers matched with the CV. |
| `/generate-letter` | `POST` | Generate a personalized motivation letter using Groq LLM. |
| `/apply` | `POST` | Send email applications automatically. |
| `/export-pdf` | `POST` | Export cover letter to PDF format. |
| `/skill-match` | `POST` | Get detailed skill match analysis. |
| `/job/{job_id}` | `GET` | Get specific job by ID. |
| `/applications` | `GET` | Get application history. |
| `/auth/google` | `GET` | Initiate Gmail OAuth 2.0 flow. |
| `/auth/google/callback` | `GET` | Handle OAuth callback. |
| `/auth/google/status` | `GET` | Check Gmail connection status. |
| `/auth/google/disconnect` | `POST` | Disconnect Gmail account. |

---

## 🧰 Key Features

### Backend Features (CrewAI-Powered)
- ✅ **CrewAI multi-agent architecture** with specialized roles
- ✅ **Groq LLM-powered cover letter generation** with skill-matching
- ✅ **Skill-matching analysis** between CV and job requirements
- ✅ **Professional PDF export** for cover letters
- ✅ **Gmail OAuth 2.0 integration** for professional email sending
- ✅ **Format-agnostic job data processing** supporting multiple schemas
- ✅ CV parsing and data extraction (PDF, DOCX, TXT)
- ✅ NLP-based job matching using text similarity
- ✅ **Ultra-targeted, ATS-optimized cover letters** with no clichés
- ✅ Email application automation (SMTP + Gmail API)
- ✅ RESTful API with FastAPI
- ✅ CORS enabled for frontend integration
- ✅ Comprehensive error handling
- ✅ **Hybrid architecture** (CrewAI + legacy services for reliability)

### Frontend Features
- ✅ Modern React + TypeScript application
- ✅ **Settings page with Gmail OAuth integration**
- ✅ Responsive design with Tailwind CSS
- ✅ Beautiful UI components (Shadcn/UI inspired)
- ✅ Real-time notifications
- ✅ CV upload with file validation
- ✅ Interactive job cards with match scores
- ✅ **Support for multiple job data formats**
- ✅ Letter preview and editing
- ✅ Application status tracking

---

## 📊 Sample Data

The system includes 18 sample job offers in `backend/data/job_offers.json` covering:
- Full-time positions (Python, React, ML, DevOps, etc.)
- Internships (Full-stack, AI/ML Research, Software Engineering)
- Various locations across France
- Different experience levels
- **Multiple data formats** (old and new schemas)

**Old Format Fields:** `title`, `company`, `location`, `type`, `description`, `requirements`

**New Format Fields:** `title`, `organization`, `locations_derived`, `remote_derived`, `employment_type`, `seniority`, `description_text`

The system seamlessly handles both formats, ensuring compatibility with any job data source.

---

## 🔒 Email Configuration

The system supports **two email methods**:

### 1. Gmail OAuth 2.0 (Recommended)
Connect your Gmail account through the Settings page for:
- ✅ Professional appearance (emails from your address)
- ✅ Better deliverability
- ✅ Emails appear in your Sent folder
- ✅ Secure OAuth 2.0 authentication

**Setup:**
1. Create OAuth credentials in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Gmail API
3. Add credentials to `.env` file
4. Navigate to Settings in the app and click "Connect Gmail Account"

### 2. SMTP (Alternative)
Use traditional SMTP for email sending:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

**Note:** For Gmail, you need to use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

If neither is configured, the system will **simulate** email sending for testing purposes.

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

## 🆕 What's New in v2.0 (CrewAI)

### Major Changes
1. **🤖 CrewAI Integration**
   - Multi-agent framework with specialized agent roles
   - Proper agent orchestration with tasks and workflows
   - Better separation of concerns

2. **🧠 LLM-Powered Cover Letters**
   - Uses OpenAI GPT-4o-mini for cover letter generation
   - Professional French business letters
   - Personalized to each job and candidate
   - ATS-optimized formatting

3. **🏗️ New Architecture**
   - `crew/` module with agents, tasks, and orchestration
   - `api/` module with clean route definitions
   - Hybrid approach: CrewAI + reliable legacy services

4. **📚 Enhanced Documentation**
   - [DEPLOYMENT_GUIDE.md](backend/DEPLOYMENT_GUIDE.md) - Complete deployment instructions
   - [crew/README.md](backend/crew/README.md) - CrewAI module documentation
   - [SAMPLE_COVER_LETTER.md](backend/SAMPLE_COVER_LETTER.md) - Example output

### Migration Notes
- **✅ Backward Compatible:** All existing API endpoints work unchanged
- **✅ Frontend Compatible:** No changes needed to existing frontend
- **✅ Legacy Preserved:** Original agents still available as fallback
- **🔑 New Requirement:** OpenAI API key now required for cover letter generation

---

## 📝 Project Structure

```
multi-agent-system/
├── backend/
│   ├── main.py                 # FastAPI application (CrewAI-powered)
│   ├── crew/                   # 🆕 CrewAI module
│   │   ├── __init__.py
│   │   ├── agents.py           # Agent definitions
│   │   ├── tasks.py            # Task definitions
│   │   ├── crew.py             # Workflow orchestration
│   │   ├── llm.py              # LLM configuration
│   │   └── README.md           # Module documentation
│   ├── api/                    # 🆕 API routes module
│   │   ├── __init__.py
│   │   └── routes.py           # Refactored endpoints
│   ├── agents/                 # Legacy agents (still used)
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
│   ├── requirements.txt        # Updated with CrewAI
│   ├── .env.example            # 🆕 Includes OpenAI config
│   ├── DEPLOYMENT_GUIDE.md     # 🆕 Deployment instructions
│   └── SAMPLE_COVER_LETTER.md  # 🆕 Example output
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
