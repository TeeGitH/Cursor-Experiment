from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse
import uvicorn
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent, ImageMessageContent, AudioMessageContent
import os
import tempfile
import requests
from dotenv import load_dotenv
import logging
from openai import OpenAI
import base64

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

def download_content(message_id):
    """Download content from LINE's servers using the Messaging API directly."""
    url = f'https://api-data.line.me/v2/bot/message/{message_id}/content'
    headers = {'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'}
    
    logger.info(f"Downloading content from {url}")
    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()  # Raise exception for non-2xx responses
        
        # Create a temporary file with appropriate extension based on content type
        content_type = response.headers.get('Content-Type', '')
        logger.info(f"Content type: {content_type}")
        
        extension = ''
        if 'image' in content_type:
            extension = '.jpg'
        elif 'audio' in content_type:
            extension = '.m4a'  # LINE typically uses m4a for audio
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as fp:
            # Stream the content to avoid loading large files into memory
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    fp.write(chunk)
            
            temp_path = fp.name
            logger.info(f"Content saved to temporary file: {temp_path}")
            return temp_path
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading content: {str(e)}")
        raise Exception(f"Failed to download content: {str(e)}")

def encode_image(image_path):
    """Encode image to base64 for OpenAI's Vision API."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

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
    logger.info(f"Received text message: {message_text}")
    
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

# Handle image messages
@handler.add(MessageEvent, message=ImageMessageContent)
def handle_image_message(event):
    logger.info(f"Received image message: {event.message.id}")
    
    try:
        # Download image content
        image_path = download_content(event.message.id)
        logger.info(f"Image downloaded to: {image_path}")
        
        # Encode image to base64
        logger.info(f"Encoding image to base64")
        try:
            base64_image = encode_image(image_path)
            logger.info(f"Image encoded successfully, size: {len(base64_image)} characters")
        except Exception as encode_error:
            logger.error(f"Error encoding image: {str(encode_error)}")
            raise Exception(f"Failed to encode image: {str(encode_error)}")
        
        # Get response from OpenAI's Vision API
        logger.info(f"Calling Vision API")
        try:
            response = client.chat.completions.create(
                model="gpt-4o",  # Updated from gpt-4-vision-preview to gpt-4o
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful assistant analyzing images. First describe what's in the image, including any text content. Then respond to any questions or requests found in the image text."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "1. Describe what's in this image in detail in Thai, including any text content.\n2. If there are any questions or requests in the image, please respond to them in Thai."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=5000
            )
            
            # Extract the response text
            ai_response = response.choices[0].message.content
            logger.info(f"Vision API response received: {ai_response[:100]}...")
        except Exception as vision_error:
            logger.error(f"Vision API error: {str(vision_error)}")
            raise Exception(f"Vision API error: {str(vision_error)}")
        
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
            logger.info(f"Replied to image with AI response in {len(message_chunks)} chunks")
        
        # Clean up the temporary file
        os.unlink(image_path)
        logger.info(f"Temporary file deleted: {image_path}")
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}", exc_info=True)
        # Send error message to user
        try:
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=f"Sorry, I encountered an error processing your image. Technical details: {str(e)[:100]}")]
                    )
                )
        except Exception as reply_error:
            logger.error(f"Error sending error message: {str(reply_error)}")

# Handle audio messages
@handler.add(MessageEvent, message=AudioMessageContent)
def handle_audio_message(event):
    logger.info(f"Received audio message: {event.message.id}")
    
    try:
        # Download audio content
        audio_path = download_content(event.message.id)
        logger.info(f"Audio downloaded to: {audio_path}")
        
        # Transcribe audio using OpenAI's Whisper API
        logger.info(f"Starting transcription of audio file: {audio_path}")
        try:
            with open(audio_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            
            transcription = transcript
            logger.info(f"Audio transcription successful: {transcription}")
        except Exception as transcribe_error:
            logger.error(f"Transcription error: {str(transcribe_error)}")
            raise Exception(f"Failed to transcribe audio: {str(transcribe_error)}")
        
        # Get response from OpenAI based on the transcription
        response = client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=[
                {"role": "system", "content": "You are a helpful assistant responding to transcribed audio. Keep your responses concise and clear."},
                {"role": "user", "content": f"This is a transcription of audio: {transcription}\n\nPlease respond to this."}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Extract the response text
        ai_response = "📝 Transcription: " + transcription + "\n\n✨ Response: " + response.choices[0].message.content
        
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
            logger.info(f"Replied to audio with AI response in {len(message_chunks)} chunks")
        
        # Clean up the temporary file
        os.unlink(audio_path)
        logger.info(f"Temporary file deleted: {audio_path}")
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}", exc_info=True)
        # Send error message to user
        try:
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="Sorry, I encountered an error processing your audio. Please try again later.")]
                    )
                )
        except Exception as reply_error:
            logger.error(f"Error sending error message: {str(reply_error)}")

if __name__ == "__main__":
    logger.info("Starting LINE Bot server...")
    logger.info("To use with ngrok: Run 'ngrok http 8080' in a separate terminal")
    logger.info("Then update your webhook URL in the LINE Developer Console")
    uvicorn.run("OpenAI_Line_Bot_v02:app", host="127.0.0.1", port=8080, reload=True) 
