# OpenAI-Powered LINE Chatbot

A LINE chatbot powered by OpenAI's GPT-4 model, built with Python, FastAPI, and the LINE Messaging API.

## Features

- Powered by OpenAI's GPT-4 model
- Handles text messages with intelligent responses
- Automatic message splitting for long responses
- Secure webhook handling with signature verification
- Comprehensive error handling and logging
- Image recognition and analysis (v02)
- Audio transcription and response (v02)
- Multi-modal communication support (v02)

## Version History

### v01 Features
- Text message handling with GPT-4
- Automatic message splitting for responses exceeding LINE's character limit
- Secure webhook verification
- Error handling and logging
- System configurations and environment variable management

### v02 Features (All v01 features plus:)
- **Image Processing**: Analyzes images, describes content, and identifies text in images
- **Text-in-Image Response**: Recognizes and responds to questions or requests found in image text
- **Audio Transcription**: Converts voice messages to text using Whisper API
- **Audio Response**: Responds to transcribed audio content
- **Enhanced Token Management**: Increased token limits for more detailed responses
- **Multi-modal Communication**: Seamless handling of text, image, and audio messages

### v03 Features (All v02 features plus:)
- **OpenAI Assistants API Integration**: Uses the new OpenAI Assistants API for more consistent and contextual conversations
- **Thread Management**: Maintains conversation threads for each user, enabling more coherent multi-turn conversations
- **Enhanced Error Handling**: More detailed error logging and user-friendly error messages
- **Improved Image Processing**: Better handling of image analysis with the Assistants API
- **Streamlined Audio Processing**: More efficient audio transcription and response pipeline
- **Background Task Processing**: Asynchronous handling of long-running tasks
- **Comprehensive Logging**: Detailed logging for better debugging and monitoring
- **Environment Variable Validation**: Automatic verification of required environment variables at startup

## Prerequisites

- Python 3.9 or higher
- A LINE developer account
- A LINE channel with Messaging API enabled
- An OpenAI API key
- ngrok (for local development)

## Setup

### 1. LINE Developer Account Setup

1. Create a provider on [LINE Developers Console](https://developers.line.biz/console/)
2. Create a new Messaging API channel under your provider
3. Get your Channel Secret from the "Basic settings" tab
4. Issue a Channel Access Token from the "Messaging API" tab

### 2. OpenAI Setup

1. Create an account on [OpenAI Platform](https://platform.openai.com/)
2. Generate an API key from your account settings
3. Make sure you have access to the GPT-4 model

### 3. Environment Setup

1. Clone this repository
   ```bash
   git clone https://github.com/yourusername/openai-line-bot.git
   cd openai-line-bot
   ```

2. Create a virtual environment and activate it
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\Activate.ps1
   ```

3. Install the required packages
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your credentials
   ```
   LINE_CHANNEL_SECRET=your_channel_secret_here
   LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token_here
   OPENAI_API_KEY=your_openai_api_key_here
   ASSISTANT_ID=your_openai_assistant_id_here
   ```

### 4. Run the Application Locally with ngrok

1. Start your FastAPI application. Choose the version you want to run:
   ```bash
   # For text-only version:
   python OpenAI_Line_Bot_v01.py
   
   # For version with image and audio support:
   python OpenAI_Line_Bot_v02.py
   ```

2. In a new terminal window, start ngrok to expose your local server
   ```bash
   ngrok http 8080
   ```

3. Copy the HTTPS URL provided by ngrok (e.g., `https://a1b2c3d4.ngrok.io`)

4. Set the webhook URL in LINE Developers Console:
   - Go to your channel settings in LINE Developers Console
   - Under the "Messaging API" tab, set the Webhook URL to:
     `https://your-ngrok-url/`
   - Make sure to turn on "Use webhook"

5. Test your bot by sending a message in the LINE app

## Project Structure

- `OpenAI_Line_Bot_v01.py`: Initial version with text-only message processing
- `OpenAI_Line_Bot_v02.py`: Enhanced version with image and audio processing capabilities
- `OpenAI_Line_Bot_v03.py`: Version with OpenAI Assistants API integration
- `requirements.txt`: Required Python packages
- `.env`: Environment variables file (create this file with your credentials)

## Features in Detail

### Message Handling
- Automatically splits long responses into multiple messages (LINE's 5,000 character limit)
- Preserves paragraph structure when splitting messages
- Handles errors gracefully with user-friendly messages

### OpenAI Integration
- Uses GPT-4 model for intelligent responses
- Configurable system prompt
- Adjustable response parameters (temperature, max_tokens)

### Security
- LINE signature verification for webhook security
- Environment variable management for sensitive credentials
- Comprehensive error handling and logging

### Multi-modal Capabilities (v02)
- **Image Analysis**: Processes images using OpenAI's Vision API (GPT-4o)
- **Text Recognition**: Identifies and extracts text content from images
- **Image Content Response**: Responds to questions or instructions found in images
- **Audio Processing**: Transcribes voice messages using Whisper API
- **Combined Response Format**: Returns both transcription and contextual response for audio

### Running a Specific Version
To run version 1 (text-only bot):
```bash
python OpenAI_Line_Bot_v01.py
```

To run version 2 (with image and audio support):
```bash
python OpenAI_Line_Bot_v02.py
```

To run version 3 (with OpenAI Assistants API integration):
```bash
python OpenAI_Line_Bot_v03.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [LINE Messaging API Documentation](https://developers.line.biz/en/docs/messaging-api/)
- [LINE Bot SDK for Python](https://github.com/line/line-bot-sdk-python)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [FastAPI Documentation](https://fastapi.tiangolo.com/) 