# 🤖 Multi-Agent System for Intelligent Job & Internship Discovery and Application Automation

An **AI-powered full-stack application** that automates the entire process of discovering, matching, and applying to jobs or internships — from CV analysis to sending personalized applications.

---

## 🚀 Project Overview

This system uses **multiple intelligent agents** to handle each step of the application process:

1. **Upload a CV** → The system analyzes it.
2. **Fetch job/internship offers** (from dummy data or APIs).
3. **Match the CV** with the best offers.
4. **Display the top 10 matching offers**.
5. **Generate a personalized “lettre de motivation.”**
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
- **Database:** SQLite
- **Communication:** REST API (CORS enabled)

---

## 🧩 Agents Overview

| Agent | Description |
|--------|-------------|
| `cv_analysis_agent.py` | Parses and extracts structured data from uploaded CVs. |
| `job_fetcher_agent.py` | Fetches job/internship offers (dummy data or external API). |
| `matching_agent.py` | Computes similarity between CV and offers using NLP embeddings. |
| `motivation_agent.py` | Generates a personalized “lettre de motivation.” |
| `application_agent.py` | Sends job applications via email. |
| `coordinator_agent.py` | Orchestrates the entire workflow between agents. |

---

## ⚙️ Folder Structure

multi-agent-system/
├── backend/
│ ├── main.py
│ ├── agents/
│ │ ├── cv_analysis_agent.py
│ │ ├── job_fetcher_agent.py
│ │ ├── matching_agent.py
│ │ ├── motivation_agent.py
│ │ ├── application_agent.py
│ │ └── coordinator_agent.py
│ ├── services/
│ │ ├── nlp_service.py
│ │ ├── email_service.py
│ │ └── utils.py
│ └── data/
│ ├── job_offers.json
│ └── parsed_cv.json
└── frontend/
├── src/
│ ├── components/
│ │ ├── UploadCV.tsx
│ │ ├── OffersList.tsx
│ │ ├── LetterPreview.tsx
│ │ └── ApplicationStatus.tsx
│ ├── api/
│ │ └── apiClient.ts
│ ├── App.tsx
│ ├── index.tsx
│ └── lib/
│ └── utils.ts



---

## 🔗 Backend API Endpoints

| Endpoint | Method | Description |
|-----------|---------|-------------|
| `/upload-cv` | `POST` | Upload a CV and extract structured data. |
| `/job-offers` | `GET` | Fetch available job/internship offers. |
| `/match-offers` | `POST` | Return top 10 offers matched with the CV. |
| `/generate-letter` | `POST` | Generate a personalized motivation letter. |
| `/apply` | `POST` | Send email applications automatically. |

---

## 🧠 Backend Requirements

- **Framework:** FastAPI
- **NLP Models:** spaCy or sentence-transformers
- **Email Sending:** smtplib or yagmail
- **Database:** SQLite
- **Server:** Uvicorn

### Example Installation & Run

```bash
# Backend setup
cd backend
pip install fastapi uvicorn spacy sentence-transformers yagmail
uvicorn main:app --reload
