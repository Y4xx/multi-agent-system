# Groq-Powered Cover Letter Generator

This document explains the new Groq-powered cover letter generation system with skill-matching capabilities.

## Overview

The cover letter generator has been refactored to use Groq's ultra-fast LLM (Mixtral-8x7B) with a skill-matching driven approach. This ensures:

- **Ultra-targeted content**: Only highlights skills and experiences relevant to the job
- **No clichés**: Enforces professional, concrete language
- **Skill matching**: Analyzes CV skills vs. job requirements
- **PDF export**: Generates modern, ATS-friendly PDF documents
- **Fast generation**: Leverages Groq's high-performance inference

## Configuration

### Environment Variables

Add the following to your `.env` file:

```bash
# Groq Configuration (REQUIRED for cover letter generation)
GROQ_API_KEY=gsk_your_actual_groq_api_key
```

Get your Groq API key from [Groq Console](https://console.groq.com/).

## Features

### 1. Skill-Matching Analysis

The system performs intelligent skill matching:

- **Extracts skills** from the CV (technical and soft skills)
- **Identifies job requirements** from job descriptions
- **Matches skills** between CV and job
- **Reports missing skills** that might be worth mentioning
- **Calculates match percentage** for job compatibility

### 2. Professional Structure

Cover letters follow a strict professional structure:

- **Header**: Candidate contact information
- **Date**: Current date
- **Recipient**: Hiring Manager and company address
- **Salutation**: Professional greeting
- **Opening**: Direct statement of position and interest
- **Body 1**: Concrete experiences matching job requirements
- **Body 2**: Specific skills alignment with the role
- **Closing**: Enthusiasm and call to action
- **Signature**: Professional closing

### 3. No Clichés Policy

The generator actively avoids common clichés:

❌ "I am writing to express my interest..."
❌ "I am a team player..."
❌ "Detail-oriented professional..."
❌ "Excellent communication skills..."

✅ "Led a team of 5 developers in implementing..."
✅ "Reduced deployment time by 60% through..."
✅ "Developed microservices serving 1M+ users..."
✅ "Optimized database queries, improving performance by 40%..."

### 4. PDF Export

Generates professional PDF documents:

- **Modern formatting**: Clean, readable layout
- **ATS-friendly**: Compatible with applicant tracking systems
- **Text normalization**: Ensures proper character encoding
- **Consistent styling**: Professional fonts and spacing

## API Usage

### 1. Generate Cover Letter

```python
POST /generate-letter
{
    "cv_data": {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "skills": ["Python", "FastAPI", "Docker"],
        "experience": [...]
    },
    "job_id": 1,
    "custom_message": "Optional custom message to include"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "job_data": {...},
        "motivation_letter": "Generated cover letter text...",
        "match_explanation": "Why this candidate matches...",
        "skill_match_report": {
            "matched_skills": ["Python", "FastAPI"],
            "missing_skills": ["Kubernetes"],
            "match_percentage": 75.5
        }
    }
}
```

### 2. Get Skill Match Analysis

```python
POST /skill-match
{
    "cv_data": {...},
    "job_id": 1
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "matched_skills": ["Python", "FastAPI", "Docker"],
        "missing_skills": ["Kubernetes", "AWS"],
        "match_percentage": 60.0
    }
}
```

### 3. Export to PDF

```python
POST /export-pdf
{
    "cv_data": {...},
    "job_id": 1,
    "cover_letter": "Cover letter text...",
    "filename": "optional_custom_name"
}
```

**Response:**
```json
{
    "success": true,
    "pdf_path": "/path/to/exported.pdf",
    "filename": "CoverLetter_Company_Position_20260112.pdf",
    "message": "Cover letter exported to PDF successfully"
}
```

## Python Usage Example

```python
from crew.crew import job_application_crew

# Load CV and job data
cv_data = {
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "+1-555-0100",
    "skills": ["Python", "Machine Learning", "TensorFlow", "Docker"],
    "experience": [
        {
            "title": "ML Engineer",
            "company": "Tech Corp",
            "responsibilities": [
                "Built ML models achieving 95% accuracy",
                "Deployed models serving 10M+ predictions/day"
            ]
        }
    ]
}

job_id = 5  # ID of the target job

# Generate cover letter with skill matching
package = job_application_crew.generate_application_package(
    cv_data=cv_data,
    job_id=job_id,
    custom_message="I'm particularly excited about your AI research team."
)

# Access the generated letter
cover_letter = package['motivation_letter']
skill_report = package['skill_match_report']

print(f"Match: {skill_report['match_percentage']:.1f}%")
print(f"Matched skills: {', '.join(skill_report['matched_skills'])}")

# Export to PDF
pdf_path = job_application_crew.export_cover_letter_to_pdf(
    cover_letter_text=cover_letter,
    cv_data=cv_data,
    job_data=package['job_data']
)

print(f"PDF saved to: {pdf_path}")
```

## Advanced Features

### Custom Skill Matching

The skill matching algorithm:

1. **Normalizes** all skills to lowercase for comparison
2. **Extracts keywords** from job descriptions (words > 3 chars)
3. **Performs fuzzy matching** (substring matching)
4. **Ranks** matched skills by relevance
5. **Identifies** top missing skills from requirements

### Text Normalization for PDF

Ensures compatibility with PDF rendering:

- Converts smart quotes to regular quotes
- Replaces em/en dashes with hyphens
- Removes problematic Unicode characters
- Ensures ASCII-safe encoding

### Fallback Mechanism

If Groq API is unavailable:

1. Attempts Groq generation first
2. Falls back to CrewAI with OpenAI if Groq fails
3. Logs errors for debugging
4. Ensures continuous operation

## Best Practices

### 1. Provide Detailed CV Data

Include comprehensive information:
- All relevant skills (technical and soft)
- Detailed work experience with specific achievements
- Educational background
- Quantifiable accomplishments

### 2. Review Generated Letters

Always review generated content:
- Verify accuracy of information
- Check for job-specific customization
- Ensure tone matches company culture
- Add personal touches if needed

### 3. Use Skill Match Reports

Leverage skill analysis:
- Focus on high-match jobs (>70%)
- Address missing skills in custom messages
- Prioritize applications strategically

### 4. Customize When Needed

Use the `custom_message` parameter to:
- Add personal connection to the company
- Mention specific projects or initiatives
- Explain career transitions
- Highlight unique qualifications

## Troubleshooting

### Groq API Connection Issues

```
Error: Connection error
```

**Solution**: Check your GROQ_API_KEY in `.env` and verify network access to Groq API.

### PDF Generation Errors

```
Error: Style 'BodyText' already defined
```

**Solution**: This has been fixed in the latest version. Update your code.

### Low Skill Match Percentage

**Tips**:
- Ensure your CV lists all relevant skills
- Update skills to match industry terminology
- Include both technical and soft skills
- Consider jobs with >60% match for better success

## Performance

- **Cover letter generation**: ~2-5 seconds (Groq)
- **PDF export**: <1 second
- **Skill matching**: <100ms

## Security

- API keys stored in `.env` (never committed)
- Generated PDFs stored in `exports/` (gitignored)
- No sensitive data logged
- Secure HTTPS communication with Groq API

## Future Enhancements

Planned improvements:
- [ ] Multi-language support
- [ ] Industry-specific templates
- [ ] A/B testing for letter effectiveness
- [ ] LinkedIn integration for skill extraction
- [ ] Custom branding for PDFs
- [ ] Batch cover letter generation

## Support

For issues or questions:
1. Check this documentation
2. Review API error messages
3. Verify environment configuration
4. Check Groq API status
5. Open an issue on GitHub
