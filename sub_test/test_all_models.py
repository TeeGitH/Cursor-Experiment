"""
OpenAI Model Testing Tool
=========================
This script allows you to test various OpenAI models from the model_list.txt file.
Activate your virtual environment before running this script.
"""

import os
import time
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

# Available models to test grouped by category
AVAILABLE_MODELS = {
    "GPT-4 Models": [
        "gpt-4o-2024-05-13",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4-1106-preview",
        "gpt-4-vision-preview",
        "gpt-4"
    ],
    "GPT-3.5 Models": [
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k",
        "gpt-3.5-turbo-instruct"
    ]
}

def test_model(model_name, prompt, show_tokens=True):
    """
    Test a specific OpenAI model with the given prompt
    """
    print(f"\n{'=' * 50}")
    print(f"MODEL: {model_name}")
    print(f"{'=' * 50}")
    print(f"PROMPT: {prompt}")
    print(f"{'-' * 50}")
    print("RESPONSE:")
    
    start_time = time.time()
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150  # Limit response length
        )
        
        elapsed_time = time.time() - start_time
        print(response.choices[0].message.content)
        
        if show_tokens:
            print(f"\nUsage tokens: {response.usage.total_tokens}")
        
        print(f"Response time: {elapsed_time:.2f} seconds")
        return True
    
    except Exception as e:
        print(f"ERROR: {e}")
        print("\nPossible issues:")
        print("- You may not have access to this model with your current API key")
        print("- The model name might be incorrect or deprecated")
        print("- There might be an issue with your API key or network connection")
        return False

def display_menu():
    """
    Display the menu of available models
    """
    print("\n" + "=" * 60)
    print("OPENAI MODEL TESTER".center(60))
    print("=" * 60)
    
    for i, category in enumerate(AVAILABLE_MODELS.keys(), 1):
        print(f"\n{i}. {category}")
        for j, model in enumerate(AVAILABLE_MODELS[category], 1):
            print(f"   {i}.{j} {model}")
    
    print("\n0. Exit")
    print("=" * 60)

def get_model_choice():
    """
    Get the user's model choice
    """
    while True:
        try:
            display_menu()
            print("\nEnter the number for the category (1, 2, etc.)")
            category_choice = int(input("Category choice: "))
            
            if category_choice == 0:
                return None
            
            categories = list(AVAILABLE_MODELS.keys())
            if 0 < category_choice <= len(categories):
                selected_category = categories[category_choice - 1]
                
                print(f"\nSelect a model from {selected_category}:")
                for j, model in enumerate(AVAILABLE_MODELS[selected_category], 1):
                    print(f"{j}. {model}")
                
                model_choice = int(input("Model choice: "))
                models = AVAILABLE_MODELS[selected_category]
                
                if 0 < model_choice <= len(models):
                    return models[model_choice - 1]
                else:
                    print("Invalid model choice. Please try again.")
            else:
                print("Invalid category choice. Please try again.")
        
        except ValueError:
            print("Please enter a number.")
        except Exception as e:
            print(f"Error: {e}")

def main():
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable not found.")
        print("Please create a .env file with your API key.")
        return
    
    print("Welcome to the OpenAI Model Tester!")
    print("This tool lets you test different OpenAI models.")
    
    while True:
        model_name = get_model_choice()
        if not model_name:
            print("Exiting program.")
            break
        
        prompt = input("\nEnter your prompt (or press Enter for default): ")
        if not prompt.strip():
            prompt = "Explain the concept of virtual environments in Python in one paragraph."
        
        success = test_model(model_name, prompt)
        
        choice = input("\nTest another model? (y/n): ").lower()
        if choice != 'y':
            print("Thank you for using the OpenAI Model Tester!")
            break

if __name__ == "__main__":
    main() 