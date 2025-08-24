#!/bin/bash

# Cron job script for VPS/Linux server deployment
# This script runs the Telegram hackathon bot

# Set the working directory
cd /path/to/telegram-hackathon-bot

# Activate virtual environment (if using one)
source .venv/bin/activate

# Set environment variables (if not in .env file)
# export TELEGRAM_BOT_TOKEN="your_token"
# export TELEGRAM_CHANNEL_ID="@your_channel"

# Run the bot
python main.py once >> cron.log 2>&1

# Optional: Clean up old logs (keep last 30 days)
find . -name "*.log" -type f -mtime +30 -delete 2>/dev/null

# Exit
exit 0
