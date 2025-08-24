# PythonAnywhere Deployment Guide

Deploy your Telegram Hackathon Bot on PythonAnywhere (free tier available).

## Prerequisites

1. PythonAnywhere account (free tier available)
2. Your bot files uploaded to PythonAnywhere
3. Telegram bot token and channel ID

## Step-by-Step Deployment

### 1. Upload Files

**Option A: Git Clone**
```bash
cd ~
git clone https://github.com/yourusername/telegram-hackathon-bot.git
cd telegram-hackathon-bot
```

**Option B: File Upload**
1. Use PythonAnywhere file manager
2. Upload all bot files to `/home/yourusername/telegram-hackathon-bot/`

### 2. Install Dependencies

Open a Bash console in PythonAnywhere:

```bash
cd ~/telegram-hackathon-bot
pip3.10 install --user -r requirements.txt
```

### 3. Configure Environment

Create `.env` file:
```bash
cp .env.example .env
nano .env  # Edit with your credentials
```

Add your configuration:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=@your_channel_username
SCRAPE_INTERVAL_HOURS=6
TELEGRAM_RATE_LIMIT=20
SCRAPING_DELAY=3
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### 4. Test the Bot

```bash
cd ~/telegram-hackathon-bot
python3.10 main.py test
```

### 5. Setup Scheduled Tasks

1. Go to PythonAnywhere Dashboard
2. Click on "Tasks" tab
3. Create a new scheduled task:

**Command:**
```
cd /home/yourusername/telegram-hackathon-bot && python3.10 main.py once
```

**Schedule Options:**
- **Every 6 hours**: Set hour to `*/6` and minute to `0`
- **Twice daily**: Create two tasks at specific hours (e.g., 9:00 and 21:00)
- **Daily**: Set to run once per day

**Example for every 6 hours:**
- Hour: `*/6`
- Minute: `0`
- Command: `cd /home/yourusername/telegram-hackathon-bot && python3.10 main.py once`

### 6. Setup Logging (Optional)

Create a daily status task:
- Hour: `9`
- Minute: `0`
- Command: `cd /home/yourusername/telegram-hackathon-bot && python3.10 main.py status`

## Monitoring

### Check Logs

```bash
cd ~/telegram-hackathon-bot
tail -f bot.log
```

### View Database Stats

```bash
cd ~/telegram-hackathon-bot
python3.10 -c "
from database import Database
db = Database()
print(db.get_stats())
"
```

### Manual Execution

```bash
cd ~/telegram-hackathon-bot
python3.10 main.py once
```

## Free Tier Limitations

- **CPU seconds**: Limited per day
- **Scheduled tasks**: 1 task on free tier
- **Always-on tasks**: Not available on free tier

## Optimization for Free Tier

1. **Reduce scraping frequency**: Set `SCRAPE_INTERVAL_HOURS=12` or `24`
2. **Lower rate limits**: Set `TELEGRAM_RATE_LIMIT=10`
3. **Increase delays**: Set `SCRAPING_DELAY=5`
4. **Combine tasks**: Use single task that does both scraping and posting

### Optimized Single Task

Modify the scheduled task to run less frequently but do more work:

**Command:**
```
cd /home/yourusername/telegram-hackathon-bot && python3.10 main.py once && sleep 300 && python3.10 main.py status
```

**Schedule**: Once or twice daily instead of every 6 hours

## Troubleshooting

### Common Issues

1. **Import errors**:
   ```bash
   pip3.10 install --user package_name
   ```

2. **Chrome/Selenium issues**:
   - Chrome might not be available on free tier
   - The bot includes fallback scraping methods
   - Check logs for specific errors

3. **Task not running**:
   - Check task logs in dashboard
   - Verify file paths are correct
   - Ensure Python version is 3.10

4. **Permission errors**:
   ```bash
   chmod +x ~/telegram-hackathon-bot/main.py
   ```

### Debug Mode

Enable detailed logging:
```bash
# Edit .env file
LOG_LEVEL=DEBUG
```

Then check logs:
```bash
tail -100 ~/telegram-hackathon-bot/bot.log
```

## Upgrading to Paid Plan

If you need more resources:

1. **Hacker Plan** ($5/month):
   - More CPU seconds
   - Multiple scheduled tasks
   - SSH access

2. **Web Developer Plan** ($12/month):
   - Always-on tasks
   - More storage and bandwidth

## File Structure on PythonAnywhere

```
/home/yourusername/telegram-hackathon-bot/
├── main.py
├── scraper.py
├── telegram_bot.py
├── database.py
├── .env
├── requirements.txt
├── bot.log
└── hackathons.db
```

## Backup Strategy

Regular backup of your database:
```bash
cd ~/telegram-hackathon-bot
cp hackathons.db backups/hackathons_$(date +%Y%m%d).db
```

Add this to a weekly scheduled task.
