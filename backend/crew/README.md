# CrewAI Module Documentation

This module contains the CrewAI-based multi-agent system implementation for the job application workflow.

## 📁 Module Structure

```
crew/
├── __init__.py          # Module initialization
├── llm.py              # LLM configuration (OpenAI integration)
├── agents.py           # Agent definitions with roles, goals, and backstories
├── tasks.py            # Task definitions for workflow steps
├── crew.py             # Main crew orchestration and workflow logic
└── README.md           # This file
```

## 🤖 Agents

### 1. CV Analysis Agent
- **Role:** CV Analysis Specialist
- **Goal:** Extract and structure all relevant information from candidate CVs
- **Responsibilities:** Parse CVs, extract skills, experience, education

### 2. Job Fetcher Agent
- **Role:** Job Market Researcher
- **Goal:** Find and retrieve the most relevant job opportunities
- **Responsibilities:** Load job offers, apply filters, maintain job database

### 3. Job Matching Agent
- **Role:** Job Match Analyst
- **Goal:** Accurately match candidate profiles with job offers
- **Responsibilities:** Compute similarity scores, rank jobs, provide explanations

### 4. Cover Letter Agent (LLM-Powered)
- **Role:** Expert French Cover Letter Writer
- **Goal:** Create compelling, personalized French cover letters
- **Responsibilities:** 
  - Write professional letters in French
  - Adapt content to job requirements
  - Optimize for ATS systems
  - Integrate custom messages

### 5. Application Agent
- **Role:** Application Submission Specialist
- **Goal:** Prepare and submit complete application packages
- **Responsibilities:** Format applications, send emails, track submissions

### 6. Coordinator Agent
- **Role:** Job Application Workflow Manager
- **Goal:** Orchestrate all agents for seamless job application experience
- **Responsibilities:** Coordinate workflow, ensure quality, optimize outcomes

## 📋 Tasks

### 1. CV Parsing Task
Extracts structured data from CV text including name, email, skills, experience, education, and languages.

### 2. Job Fetching Task
Retrieves job offers from database with optional filters (type, location, keyword).

### 3. Matching Task
Ranks jobs based on CV compatibility using NLP similarity and skill matching.

### 4. Cover Letter Task
Generates personalized French cover letters using LLM with specific instructions:
- Write ONLY in French
- Professional and formal tone
- Highlight matching skills
- Keep concise (3-4 paragraphs)
- ATS-optimized
- Include proper French salutation and closing

### 5. Application Task
Prepares and submits applications via email with CV data and motivation letter.

## 🔧 Usage

### Basic Setup

```python
from crew.crew import job_application_crew

# The crew is initialized as a singleton
crew = job_application_crew
```

### Analyze CV

```python
# From text
cv_data = crew.analyze_cv(cv_text)

# From file
cv_data = crew.analyze_cv_file('/path/to/cv.pdf')
```

### Fetch Jobs

```python
# All jobs
jobs = crew.fetch_jobs()

# By type
jobs = crew.fetch_jobs(job_type='Full-time')

# By location
jobs = crew.fetch_jobs(location='Paris')
```

### Match Jobs

```python
matched_jobs = crew.match_jobs(
    cv_data=cv_data,
    jobs=jobs,
    top_n=10
)
```

### Generate Cover Letter (LLM-Powered)

```python
cover_letter = crew.generate_cover_letter(
    cv_data=cv_data,
    job_data=job_data,
    custom_message="Je suis particulièrement motivé par ce poste."
)
```

### Complete Workflow

```python
# Get recommendations
recommendations = crew.get_job_recommendations(
    cv_data=cv_data,
    job_type='Full-time',
    location='Paris',
    top_n=10
)

# Generate application package
package = crew.generate_application_package(
    cv_data=cv_data,
    job_id=1,
    custom_message="Custom message"
)

# Submit application
result = crew.submit_application(
    cv_data=cv_data,
    job_data=job_data,
    motivation_letter=cover_letter
)
```

## 🔑 Environment Variables

Required in `.env` file:

```bash
# LLM Configuration (Required)
OPENAI_API_KEY=sk-your-api-key-here
MODEL_NAME=gpt-4o-mini

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

## 🧠 LLM Integration

The system uses OpenAI's API through LangChain for LLM-powered features:

- **Model:** gpt-4o-mini (configurable)
- **Temperature:** 0.7 (balanced creativity)
- **Primary Use:** French cover letter generation
- **Framework:** LangChain + CrewAI

### Cover Letter Generation

The Cover Letter Agent is specifically tuned to:
1. Write exclusively in French
2. Maintain professional business tone
3. Personalize based on:
   - Candidate skills and experience
   - Job title and company
   - Job requirements
   - Custom candidate message
4. Follow French business letter format
5. Optimize for ATS systems

## 🏗️ Architecture

The crew uses a **hybrid architecture**:

### CrewAI Layer (New)
- Agent definitions with roles and goals
- Task orchestration
- LLM-powered cover letter generation
- Workflow management

### Legacy Layer (Preserved)
- CV parsing (reliable regex-based extraction)
- Job fetching (JSON database)
- NLP matching (sentence transformers)
- Email sending (SMTP)

This hybrid approach ensures:
- **Reliability:** Critical operations use proven methods
- **Innovation:** LLM enhances where it adds most value
- **Backward compatibility:** Existing functionality preserved
- **Flexibility:** Easy to extend with more LLM features

## 🔄 Workflow

```
1. Upload CV → CV Analysis Agent
   ↓
2. Parse & Extract → Structured CV Data
   ↓
3. Fetch Jobs → Job Fetcher Agent
   ↓
4. Match & Rank → Matching Agent
   ↓
5. Select Job → User Choice
   ↓
6. Generate Letter → Cover Letter Agent (LLM)
   ↓
7. Review & Edit → User
   ↓
8. Submit → Application Agent
```

## 📊 Example Output

See [SAMPLE_COVER_LETTER.md](../SAMPLE_COVER_LETTER.md) for an example of LLM-generated French cover letter.

## 🚀 Benefits

1. **Professional Cover Letters:** LLM generates high-quality French letters
2. **Personalization:** Each letter tailored to job and candidate
3. **Consistency:** Agents ensure standardized workflow
4. **Scalability:** Easy to add new agents and tasks
5. **Maintainability:** Clear separation of concerns
6. **Traceability:** Verbose mode for debugging

## 🔍 Testing

Run integration tests:

```bash
cd backend
python /tmp/test_integration.py
```

Expected output:
- ✓ All modules import successfully
- ✓ Legacy services work
- ✓ CrewAI wrappers function
- ✓ API routes accessible
- ✓ FastAPI app initialized

## 📝 Notes

- Cover letter generation requires a valid OpenAI API key
- Email sending requires SMTP configuration (or uses simulation mode)
- The system maintains backward compatibility with existing agents
- All endpoints remain unchanged for frontend compatibility

## 🎯 Future Enhancements

Potential areas for expansion:
- Add more LLM-powered agents (interview prep, skill assessment)
- Implement multi-lingual support beyond French
- Add conversation memory for better personalization
- Integrate with external job APIs (LinkedIn, Indeed)
- Add resume enhancement agent
