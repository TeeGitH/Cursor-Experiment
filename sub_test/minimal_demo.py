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

# Get API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client = OpenAI(api_key=api_key)

def main():
    """
    Minimal OpenAI API example
    """
    # Check if API key is set
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please create a .env file with your OpenAI API key like this:")
        print("OPENAI_API_KEY=your-api-key-here")
        return
    
    try:
        # Simple completion example
        print("Asking OpenAI: Tell me about the Python programming language")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Tell me about the Python programming language in 2-3 sentences."}
            ],
            max_tokens=100
        )
        
        print("\nResponse from OpenAI:")
        print(response.choices[0].message.content)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Make sure your API key is valid and you have sufficient credits.")


if __name__ == "__main__":
    main() 