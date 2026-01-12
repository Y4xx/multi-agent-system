# Format-Agnostic Job Data Processing

This document explains how the Multi-Agent Job System handles different job data formats seamlessly.

## Overview

The system is designed to be **format-agnostic**, meaning it can process job offers from multiple sources with different data schemas without requiring code changes. This ensures compatibility with various job APIs and data sources.

## Supported Formats

### Old Format (Original Schema)

```json
{
  "id": 1,
  "title": "Senior Python Developer",
  "company": "Tech Innovators Inc.",
  "location": "Paris, France",
  "type": "Full-time",
  "description": "We are looking for an experienced Python developer...",
  "requirements": [
    "5+ years of Python development experience",
    "Experience with FastAPI or Django"
  ],
  "salary": "60000-80000 EUR",
  "posted_date": "2025-01-15",
  "application_email": "hr@techinnovators.com"
}
```

### New Format (Extended Schema)

```json
{
  "id": 16,
  "title": "Cloud Solutions Architect",
  "organization": "TechCloud Innovations",
  "locations_derived": ["Paris", "Remote"],
  "remote_derived": "Hybrid",
  "employment_type": "Full-time",
  "seniority": "Senior",
  "description_text": "We are looking for an experienced Cloud Solutions Architect...",
  "application_email": "careers@techcloud.fr"
}
```

## Field Mapping

The system automatically maps between different field names:

| Old Format | New Format | Description |
|------------|------------|-------------|
| `company` | `organization` | Company/organization name |
| `location` | `locations_derived` | Location(s) - can be string or array |
| `type` | `employment_type` | Employment type (Full-time, Part-time, etc.) |
| `description` | `description_text` | Job description |
| - | `remote_derived` | Remote work policy (new format only) |
| - | `seniority` | Seniority level (new format only) |
| `requirements` | - | List of requirements (old format only) |

## Implementation

### Backend: Format-Agnostic Utilities

The system uses helper functions to handle different formats:

#### 1. `get_job_field(job_data, field_name)`

Retrieves field values regardless of format:

```python
from services.utils import get_job_field

# Works with both formats
company = get_job_field(job_data, 'company')  # Returns 'company' or 'organization'
location = get_job_field(job_data, 'location')  # Returns 'location' or 'locations_derived'
job_type = get_job_field(job_data, 'type')  # Returns 'type' or 'employment_type'
```

#### 2. `create_job_summary(job_data)`

Creates a unified text summary from any format:

```python
from services.utils import create_job_summary

summary = create_job_summary(job_data)
# Returns formatted summary with all available fields
```

### Agents Updated for Format-Agnostic Processing

All agents have been updated to use the format-agnostic helpers:

1. **Matching Agent** - Uses `create_job_summary()` for similarity computation
2. **Motivation Agent** - Uses `get_job_field()` to extract job details
3. **Application Agent** - Works with any format for email composition

### Frontend: Dynamic Field Display

The frontend components handle both formats:

```typescript
// OffersList.tsx
{offer.company || offer.organization}  // Shows either field
{offer.location || (Array.isArray(offer.locations_derived) 
  ? offer.locations_derived.join(', ') 
  : offer.locations_derived)}
{offer.type || offer.employment_type}
{offer.description || offer.description_text}
```

## Adding New Formats

To add support for a new job data format:

### 1. Update Field Mapping

Edit `backend/services/utils.py` and add new field mappings to `get_job_field()`:

```python
field_mapping = {
    'company': ['company', 'organization', 'employer'],  # Add new field name
    # ... other mappings
}
```

### 2. Update Job Summary Function

Edit `create_job_summary()` to handle new fields:

```python
# Add handling for new fields
if job_data.get('new_field'):
    parts.append(f"New Field: {job_data['new_field']}")
```

### 3. Update TypeScript Interface (Optional)

If you want TypeScript type checking, update the interface:

```typescript
// frontend/src/api/apiClient.ts
export interface JobOffer {
  // ... existing fields
  new_field?: string;  // Add optional field
}
```

### 4. Update Frontend Display (If Needed)

Update components to display new fields:

```typescript
{offer.new_field && (
  <Badge>{offer.new_field}</Badge>
)}
```

## Example: Integrating with Different APIs

### LinkedIn Jobs API

```python
def transform_linkedin_job(linkedin_job):
    return {
        "id": linkedin_job["id"],
        "title": linkedin_job["title"],
        "organization": linkedin_job["company"]["name"],
        "locations_derived": linkedin_job["locations"],
        "employment_type": linkedin_job["employmentType"],
        "description_text": linkedin_job["description"],
        # ... map other fields
    }
```

### Indeed API

```python
def transform_indeed_job(indeed_job):
    return {
        "id": indeed_job["jobkey"],
        "title": indeed_job["jobtitle"],
        "company": indeed_job["company"],
        "location": indeed_job["formattedLocation"],
        "type": indeed_job["employmenttype"],
        "description": indeed_job["snippet"],
        # ... map other fields
    }
```

## Benefits

1. **Flexibility**: Support multiple job data sources without code changes
2. **Backward Compatibility**: Existing job offers continue to work
3. **Forward Compatibility**: Easy to add new formats
4. **Maintainability**: Centralized field mapping logic
5. **No Breaking Changes**: Frontend and agents work with all formats

## Testing Format Compatibility

You can test format compatibility:

```python
# backend/services/utils.py test
from services.utils import create_job_summary, get_job_field

# Old format job
old_job = {
    "title": "Developer",
    "company": "ACME Inc.",
    "location": "Paris",
    "type": "Full-time",
    "description": "Great job!"
}

# New format job
new_job = {
    "title": "Developer",
    "organization": "ACME Inc.",
    "locations_derived": ["Paris", "Remote"],
    "employment_type": "Full-time",
    "description_text": "Great job!",
    "seniority": "Mid-level"
}

# Both work with the same code
print(get_job_field(old_job, 'company'))  # ACME Inc.
print(get_job_field(new_job, 'company'))  # ACME Inc.
```

## Migration Strategy

If you have existing job offers in the old format:

1. **No Action Needed**: The system handles both formats automatically
2. **Gradual Migration**: Add new format jobs alongside old format jobs
3. **Mixed Database**: You can have both formats in the same database
4. **API Changes**: Update your job fetching logic when ready

## Best Practices

1. **Always Use Helpers**: Use `get_job_field()` instead of direct field access
2. **Test Both Formats**: Test your changes with both old and new format jobs
3. **Document New Fields**: Update this document when adding new field mappings
4. **Optional Fields**: Make all format-specific fields optional
5. **Fallback Values**: Provide sensible defaults when fields are missing

## Future Enhancements

Possible future improvements:

- [ ] Support for custom field mappings via configuration
- [ ] Automatic format detection and validation
- [ ] Schema versioning for job offers
- [ ] Migration tools to convert between formats
- [ ] REST API to register new format mappings
