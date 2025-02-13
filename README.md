# Twitter Trend Bot

A Twitter bot that monitors trending topics in the USA and generates witty responses using GPT-4. Built with dual account support to handle Twitter API rate limits efficiently.

## Key Features

- 🔄 Dual Twitter account management for handling API limits
- 🔍 USA trending topics monitoring
- 🤖 GPT-4 powered responses
- 🌐 Web-based control panel
- 🔒 Secure authentication
- 📊 Real-time log monitoring

## Tech Stack

- Python 3.x
- Twitter API (tweepy)
- OpenAI GPT-4
- Flask (web interface)
- Schedule (task scheduling)

## Quick Start

1. **Setup Environment**
   ```bash
   git clone https://github.com/sarperhorata/twitter-trend-bot.git
   cd twitter-trend-bot
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Bot**
   - Copy `.env.example` to `.env`
   - Add your Twitter API credentials for both accounts
   - Add your OpenAI API key
   - Set up admin credentials

3. **Run Bot**
   ```bash
   python -m twitter_bot.main
   ```

4. **Access Control Panel**
   - Open `http://localhost:5000`
   - Login with admin credentials
   - Monitor and control bot operations

## Configuration Guide

Check `.env.example` for all required environment variables:
- Twitter API credentials (2 accounts)
- OpenAI API key
- Bot personality settings
- Admin access credentials
- Application settings