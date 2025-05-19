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

# Verify credentials are loaded
if not LINE_CHANNEL_SECRET or not LINE_CHANNEL_ACCESS_TOKEN:
    logger.error("LINE credentials not found in .env file")
    logger.info("Please make sure LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN are set in .env file")
else:
    logger.info("LINE credentials loaded successfully")

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
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            
            # Echo the received message back to the user
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=f"You said: {message_text}")]
                )
            )
            logger.info(f"Replied to message: {message_text}")
    except Exception as e:
        logger.error(f"Error sending reply: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting LINE Bot server...")
    logger.info("To use with ngrok: Run 'ngrok http 8080' in a separate terminal")
    logger.info("Then update your webhook URL in the LINE Developer Console")
    uvicorn.run("sample_line_bot:app", host="127.0.0.1", port=8080, reload=True) 