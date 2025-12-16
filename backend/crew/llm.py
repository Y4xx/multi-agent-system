"""
LLM Configuration for CrewAI.
Handles OpenAI API integration and model configuration.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

def get_llm():
    """
    Get configured LLM instance for CrewAI.
    
    Returns:
        ChatOpenAI instance configured with API key and model
    """
    api_key = os.getenv('OPENAI_API_KEY')
    model_name = os.getenv('MODEL_NAME', 'gpt-4o-mini')
    
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found in environment variables. "
            "Please set it in your .env file."
        )
    
    llm = ChatOpenAI(
        model=model_name,
        temperature=0.7,
        api_key=api_key
    )
    
    return llm
