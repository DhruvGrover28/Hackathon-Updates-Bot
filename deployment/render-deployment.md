# Render Deployment Configuration

This file contains instructions for deploying the Telegram Hackathon Bot on Render.

## Prerequisites

1. GitHub account with your bot repository
2. Render account (free tier available)
3. Telegram Bot Token
4. Telegram Channel ID

## Deployment Steps

### 1. Create Render Account
1. Go to [Render](https://render.com/)
2. Sign up using your GitHub account
3. Connect your GitHub repository

### 2. Create New Web Service
1. Click "New +" → "Web Service"
2. Connect your repository
3. Configure the service:
   - **Name**: hackathon-updates-bot
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python render_bot.py`

### 3. Environment Variables
In Render dashboard, go to your service and add these environment variables:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=your_channel_id_here
```

### 4. Build Configuration
Render should automatically detect Python. If not, add:
- **Python Version**: 3.9+
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python render_bot.py`

### 5. Deploy
1. Render will automatically build and deploy
2. Monitor build logs for any issues
3. Check service logs after deployment

## Monitoring

- Use Render dashboard to view logs
- Bot runs every 6 hours automatically
- Check `/health` endpoint for status

## Render Specific Files

- `render_bot.py` - Main bot file for Render deployment
- `requirements.txt` - Python dependencies

### render_bot.py Features
- HTTP health check endpoint
- Scheduled execution every 6 hours
- Automatic restart on failures
- Comprehensive logging

## Troubleshooting

### Common Issues

1. **Chrome/Selenium issues on Render**:
   - Uses fallback scraping methods
   - Some sites may block requests
   - Consider using proxy services

2. **Environment Variables**:
   - Double-check variable names
   - Ensure no extra spaces
   - Use Render dashboard to verify

3. **Build Failures**:
   - Check Python version compatibility
   - Verify requirements.txt syntax
   - Check Render logs for deployment issues

4. **Bot Not Responding**:
   - Verify Telegram token is correct
   - Check channel ID format
   - Ensure bot has admin permissions

## Cost Information

- **Free Tier**: Available with limitations
- **Starter Plan**: $7/month for always-on service
- **Professional**: $25/month for production workloads

## Alternative Deployment Methods

If Render doesn't work:
1. Try PythonAnywhere
2. Use GitHub Actions (free)
3. Deploy on a VPS with cron jobs

## Support

For Render-specific issues:
- Check Render documentation
- Contact Render support
- Use Render community forums
