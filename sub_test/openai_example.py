"""
OpenAI API Example - Model Testing Script
This script demonstrates how to use different OpenAI models listed in model_list.txt
Make sure to create a .env file with your OPENAI_API_KEY
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# Build path to the .env file in the parent directory
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
dotenv_path = parent_dir / '.env'

# Load environment variables from .env file in parent directory
load_dotenv(dotenv_path=dotenv_path)

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def test_openai_model(model_name, prompt):
    """
    Test an OpenAI model with the given prompt
    """
    print(f"\nTesting model: {model_name}")
    print(f"Prompt: {prompt}")
    print("Response:")
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150  # Limit response length
        )
        
        print(response.choices[0].message.content)
        print(f"\nUsage tokens: {response.usage.total_tokens}")
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable not found.")
        print("Please create a .env file with your API key.")
        return
    
    # Define test prompt
    prompt = "Explain the concept of virtual environments in Python in one paragraph."
    
    # List of models to test
    models = [
        "gpt-3.5-turbo",      # Default, less expensive
        "gpt-4o-mini",        # More affordable GPT-4 option
        # "gpt-4o-2024-05-13",  # Most capable
    ]
    
    # Test each model
    for model in models:
        success = test_openai_model(model, prompt)
        print("-" * 60)

if __name__ == "__main__":
    main() 