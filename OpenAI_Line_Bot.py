from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse
import uvicorn
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import os
from dotenv import load_dotenv
import logging
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Verify credentials are loaded
if not LINE_CHANNEL_SECRET or not LINE_CHANNEL_ACCESS_TOKEN:
    logger.error("LINE credentials not found in .env file")
    logger.info("Please make sure LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN are set in .env file")
else:
    logger.info("LINE credentials loaded successfully")

if not OPENAI_API_KEY:
    logger.error("OpenAI API key not found in .env file")
    logger.info("Please make sure OPENAI_API_KEY is set in .env file")
else:
    logger.info("OpenAI API key loaded successfully")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def split_message(text, max_length=5000):
    """Split a long message into chunks that fit within LINE's message length limit."""
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    # Split by newlines first to keep paragraphs together
    paragraphs = text.split('\n')
    
    for paragraph in paragraphs:
        # If adding this paragraph would exceed the limit, start a new chunk
        if len(current_chunk) + len(paragraph) + 1 > max_length:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = paragraph
        else:
            if current_chunk:
                current_chunk += '\n' + paragraph
            else:
                current_chunk = paragraph
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

# Create FastAPI app
app = FastAPI(title="LINE Bot Sample")

# Initialize LINE SDK components
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Root endpoint for checking if server is running
@app.get("/")
async def root():
    return {"message": "LINE Bot server is running", "status": "OK"}

@app.post("/")
async def root_post(request: Request):
    # Get X-Line-Signature header
    signature = request.headers.get('X-Line-Signature', '')
    
    # Get request body as text
    body = await request.body()
    body_text = body.decode('utf-8')
    
    logger.info(f"Received webhook at root: {body_text}")
    
    # Handle webhook body
    try:
        handler.handle(body_text, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature detected")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    return PlainTextResponse(content='OK')

# Define webhook endpoint
@app.post("/callback")
async def callback(request: Request):
    # Get X-Line-Signature header
    signature = request.headers.get('X-Line-Signature', '')
    
    # Get request body as text
    body = await request.body()
    body_text = body.decode('utf-8')
    
    logger.info(f"Received webhook: {body_text}")
    
    # Handle webhook body
    try:
        handler.handle(body_text, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature detected")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    return PlainTextResponse(content='OK')

# Handle text messages
@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    message_text = event.message.text
    logger.info(f"Received message: {message_text}")
    
    try:
        # Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-4-0125-preview",  # Using the latest GPT-4 model
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Keep your responses concise and clear."},
                {"role": "user", "content": message_text}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Extract the response text
        ai_response = response.choices[0].message.content
        
        # Split the response into chunks if it's too long
        message_chunks = split_message(ai_response)
        
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            
            # Send each chunk as a separate message
            for chunk in message_chunks:
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=chunk)]
                    )
                )
            logger.info(f"Replied with AI response in {len(message_chunks)} chunks")
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        # Send error message to user
        try:
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="Sorry, I encountered an error. Please try again later.")]
                    )
                )
        except Exception as reply_error:
            logger.error(f"Error sending error message: {str(reply_error)}")

if __name__ == "__main__":
    logger.info("Starting LINE Bot server...")
    logger.info("To use with ngrok: Run 'ngrok http 8080' in a separate terminal")
    logger.info("Then update your webhook URL in the LINE Developer Console")
    uvicorn.run("sample_line_bot:app", host="127.0.0.1", port=8080, reload=True) 
