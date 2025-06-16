import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
assistant_id = os.getenv('ASSISTANT_ID')

print(f"API key found: {bool(api_key)}")
print(f"Assistant ID found: {bool(assistant_id)}")

if api_key and assistant_id:
    try:
        client = OpenAI(api_key=api_key)
        
        # Test Assistant
        print(f"Testing Assistant ID: {assistant_id}")
        
        # Create a thread
        thread = client.beta.threads.create()
        print(f"✅ Created thread: {thread.id}")
        
        # Add a message
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content="Hello! Please respond with a simple greeting."
        )
        print(f"✅ Added message to thread")
        
        # Create a run
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )
        print(f"✅ Created run: {run.id}")
        
        # Wait for completion
        import time
        while run.status in ['queued', 'in_progress']:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            print(f"Run status: {run.status}")
        
        if run.status == 'completed':
            # Get messages
            messages = client.beta.threads.messages.list(
                thread_id=thread.id,
                order="desc",
                limit=1
            )
            
            if messages.data:
                response = messages.data[0].content[0].text.value
                print(f"✅ Assistant response: {response}")
            else:
                print("❌ No response found")
        else:
            print(f"❌ Run failed with status: {run.status}")
            if hasattr(run, 'last_error') and run.last_error:
                print(f"Error: {run.last_error}")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
else:
    print("❌ Missing API key or Assistant ID") 