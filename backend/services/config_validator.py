"""
Configuration validator to check all required environment variables.
"""
import os
from typing import Dict, List

def validate_config() -> Dict[str, any]:
    """
    Validate all required configuration. 
    
    Returns:
        Dictionary with validation results
    """
    results = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Check required variables
    required_vars = {
        'OPENAI_API_KEY': 'Required for CrewAI fallback',
        'GROQ_API_KEY': 'Required for Groq cover letter generation'
    }
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            if var == 'GROQ_API_KEY':
                results['warnings'].append(f"{var} not set: {description}")
            else:
                results['valid'] = False
                results['errors'].append(f"{var} not set: {description}")
    
    return results

def print_config_status():
    """Print configuration status on startup."""
    results = validate_config()
    
    print("\n" + "="*50)
    print("🔧 CONFIGURATION STATUS")
    print("="*50)
    
    if results['errors']:
        print("\n❌ ERRORS:")
        for error in results['errors']:
            print(f"  - {error}")
    
    if results['warnings']:
        print("\n⚠️  WARNINGS:")
        for warning in results['warnings']:
            print(f"  - {warning}")
    
    if results['valid'] and not results['warnings']:
        print("\n✅ All configuration valid!")
    
    print("="*50 + "\n")
    
    return results['valid']
