# Python LINE Chatbot Example

A simple LINE chatbot built with Python, Flask, and the LINE Messaging API.

## Features

- Responds to text messages
- Handles basic commands (`/help`, `/about`, `/sticker`)
- Uses quick reply buttons for easy interaction
- Responds to follow/unfollow events

## Prerequisites

- Python 3.9 or higher
- A LINE developer account
- A LINE channel with Messaging API enabled
- ngrok (for local development)

## Setup

### 1. LINE Developer Account Setup

1. Create a provider on [LINE Developers Console](https://developers.line.biz/console/)
2. Create a new Messaging API channel under your provider
3. Get your Channel Secret from the "Basic settings" tab
4. Issue a Channel Access Token from the "Messaging API" tab

### 2. Environment Setup

1. Clone this repository
   ```bash
   git clone https://github.com/yourusername/line-chatbot-example.git
   cd line-chatbot-example
   ```

2. Create a virtual environment and activate it
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.sample` and fill in your LINE credentials
   ```
   LINE_CHANNEL_SECRET=your_channel_secret_here
   LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token_here
   PORT=5000
   DEBUG=true
   ```

### 3. Run the Application Locally with ngrok

1. Start your Flask application
   ```bash
   python app.py
   ```

2. In a new terminal window, start ngrok to expose your local server
   ```bash
   ngrok http 5000
   ```

3. Copy the HTTPS URL provided by ngrok (e.g., `https://a1b2c3d4.ngrok.io`)

4. Set the webhook URL in LINE Developers Console:
   - Go to your channel settings in LINE Developers Console
   - Under the "Messaging API" tab, set the Webhook URL to:
     `https://your-ngrok-url/callback`
   - Make sure to turn on "Use webhook"

5. Test your bot by sending a message in the LINE app

## Project Structure

- `app.py`: Main application file with Flask server and LINE bot logic
- `requirements.txt`: Required Python packages
- `.env.sample`: Sample environment variables file

## Deployment

### To Deploy on Heroku

1. Create a Heroku account and install the Heroku CLI
2. Initialize a git repository (if not already done)
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

3. Create a Heroku app
   ```bash
   heroku create your-app-name
   ```

4. Set the environment variables on Heroku
   ```bash
   heroku config:set LINE_CHANNEL_SECRET=your_channel_secret_here
   heroku config:set LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token_here
   ```

5. Deploy to Heroku
   ```bash
   git push heroku master
   ```

6. Update your webhook URL in LINE Developers Console to your Heroku app URL:
   `https://your-app-name.herokuapp.com/callback`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [LINE Messaging API Documentation](https://developers.line.biz/en/docs/messaging-api/)
- [LINE Bot SDK for Python](https://github.com/line/line-bot-sdk-python) 