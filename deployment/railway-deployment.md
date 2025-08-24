# Railway Deployment Configuration

This file contains instructions for deploying the Telegram Hackathon Bot on Railway.

## Prerequisites

1. GitHub account with your bot code
2. Railway account (free tier available)
3. Telegram bot token and channel ID

## Deployment Steps

### 1. Connect Repository

1. Go to [Railway](https://railway.app/)
2. Sign up/Login with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your telegram-hackathon-bot repository

### 2. Configure Environment Variables

In Railway dashboard, go to your project and add these environment variables:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=@your_channel_username_or_chat_id
SCRAPE_INTERVAL_HOURS=6
TELEGRAM_RATE_LIMIT=30
SCRAPING_DELAY=2
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### 3. Configure Buildpacks

Railway should automatically detect Python. If not, add:

```
BUILDPACK_URL=heroku/python
```

### 4. Deploy

1. Railway will automatically build and deploy
2. Check logs to ensure everything is working
3. The bot will start running with the scheduler

### 5. Monitor

- Use Railway dashboard to view logs
- Check your Telegram channel for posts
- Monitor resource usage

## Railway Specific Files

Create these files if needed:

### railway.json (optional)
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python main.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### nixpacks.toml (optional)
```toml
[phases.setup]
nixPkgs = ["python310", "chromium"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[phases.build]
cmds = ["echo 'Build completed'"]

[start]
cmd = "python main.py"
```

## Cost Estimation

- **Free Tier**: $0/month (limited resources, may sleep)
- **Hobby Plan**: $5/month (always on, better performance)

## Troubleshooting

### Common Issues:

1. **Chrome/Selenium issues on Railway**:
   - Railway runs on Linux, Chrome should work
   - Check logs for WebDriver errors
   - Consider using headless Chrome options

2. **Build failures**:
   - Ensure requirements.txt is correct
   - Check Python version compatibility

3. **Environment variables**:
   - Double-check all required variables are set
   - Use Railway dashboard to verify

4. **Memory issues**:
   - Upgrade to Hobby plan if needed
   - Optimize scraping frequency

### Debugging:

1. Set `LOG_LEVEL=DEBUG` for detailed logs
2. Use `python main.py test` to test configuration
3. Check Railway logs for deployment issues
