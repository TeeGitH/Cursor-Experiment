import os
import openai
import time
import base64
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

def text_completion_example():
    """
    Example of text completion using GPT model
    """
    print("\n=== TEXT COMPLETION EXAMPLE ===")
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me about the Python programming language in 50 words."}
        ],
        max_tokens=100
    )
    
    print(f"Response: {response.choices[0].message.content}")


def chat_conversation_example():
    """
    Example of a multi-turn chat conversation
    """
    print("\n=== CHAT CONVERSATION EXAMPLE ===")
    
    messages = [
        {"role": "system", "content": "You are a programming assistant who specializes in Python."},
        {"role": "user", "content": "How do I read a file in Python?"},
    ]
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=150
    )
    
    # Add assistant's response to the messages
    messages.append({"role": "assistant", "content": response.choices[0].message.content})
    print(f"Assistant: {response.choices[0].message.content}\n")
    
    # Second user message
    messages.append({"role": "user", "content": "How would I modify that to read only the first 10 lines?"})
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=150
    )
    
    print(f"Assistant: {response.choices[0].message.content}")


def function_calling_example():
    """
    Example of OpenAI function calling capability
    """
    print("\n=== FUNCTION CALLING EXAMPLE ===")
    
    # Define functions that the model can call
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g., San Francisco, CA"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "The temperature unit to use"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ]
    
    # Create a chat completion with function calling
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What's the weather like in New York today?"}
        ],
        tools=tools,
        tool_choice="auto"
    )
    
    message = response.choices[0].message
    
    # Check if the model wants to call a function
    if message.tool_calls:
        print(f"Function to call: {message.tool_calls[0].function.name}")
        print(f"Arguments: {message.tool_calls[0].function.arguments}")
        print("\nIn a real application, you would now call your actual weather API with these parameters")


def streaming_example():
    """
    Example of streaming response from the API
    """
    print("\n=== STREAMING RESPONSE EXAMPLE ===")
    print("Response: ", end="", flush=True)
    
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write a short poem about artificial intelligence."}
        ],
        stream=True,
        max_tokens=150
    )
    
    # Process the stream
    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    
    print("\n")  # Add newlines after the streaming is complete


def encode_image(image_path):
    """
    Encode an image to base64
    """
    if not os.path.exists(image_path):
        return None
        
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def vision_example():
    """
    Example of using GPT-4 Vision to analyze images
    Note: This requires GPT-4 Vision API access
    """
    print("\n=== VISION API EXAMPLE ===")
    
    # Path to an image file
    image_path = "path/to/your/image.jpg"  # Replace with an actual image path
    
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"Image file not found at: {image_path}")
        print("To use this example, replace 'path/to/your/image.jpg' with an actual image path.")
        return
    
    # Encode the image
    base64_image = encode_image(image_path)
    
    if not base64_image:
        print("Failed to encode image.")
        return
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",  # Note: requires GPT-4 Vision API access
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What's in this image?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=300
        )
        
        print(f"Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"Error with Vision API: {str(e)}")
        print("Note: The Vision API requires special access and may not be available to all users.")


def main():
    """
    Main function to run all examples
    """
    print("OpenAI API Demo\n")
    print("Note: You need to set the OPENAI_API_KEY environment variable to use this demo.")
    
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please create a .env file with your OpenAI API key like this:")
        print("OPENAI_API_KEY=your-api-key-here")
        return
    
    try:
        text_completion_example()
        chat_conversation_example()
        function_calling_example()
        streaming_example()
        
        # Vision API requires special access and an image file
        # Uncomment the line below if you have access and an image file
        # vision_example()
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("\nMake sure your API key is valid and you have sufficient credits in your OpenAI account.")


if __name__ == "__main__":
    main() 