# OpenAI-Powered LINE Chatbot

A LINE chatbot powered by OpenAI's GPT-4 model, built with Python, FastAPI, and the LINE Messaging API.

## Features

- Powered by OpenAI's GPT-4 model
- Handles text messages with intelligent responses
- Automatic message splitting for long responses
- Secure webhook handling with signature verification
- Comprehensive error handling and logging

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
   ```

### 4. Run the Application Locally with ngrok

1. Start your FastAPI application
   ```bash
   python OpenAI_Line_Bot.py
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

- `OpenAI_Line_Bot.py`: Main application file with FastAPI server and LINE bot logic
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

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [LINE Messaging API Documentation](https://developers.line.biz/en/docs/messaging-api/)
- [LINE Bot SDK for Python](https://github.com/line/line-bot-sdk-python)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [FastAPI Documentation](https://fastapi.tiangolo.com/) 