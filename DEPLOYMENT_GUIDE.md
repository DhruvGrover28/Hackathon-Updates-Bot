# 🚀 Production-Ready Telegram Hackathon Bot

## 📋 Project Overview

This is a complete, production-ready Telegram bot that:
- 🔍 Scrapes hackathon information from Unstop.com
- 🚫 Prevents duplicate posts using database deduplication
- 📱 Posts formatted updates to your Telegram channel
- 🔄 Runs automatically on a schedule
- 🛡️ Includes comprehensive error handling and logging
- ⚡ Respects rate limits and includes safety mechanisms

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   main.py       │    │   scraper.py     │    │ telegram_bot.py │
│   (Orchestrator)│◄──►│   (Web Scraper)  │    │ (Bot Interface) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   database.py   │    │  Unstop.com      │    │ Telegram API    │
│   (SQLite DB)   │    │  (Target Site)   │    │ (Channel Posts) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Core Components:

1. **`main.py`** - Main orchestrator with scheduling and CLI interface
2. **`scraper.py`** - Web scraping with Selenium and fallback mechanisms
3. **`telegram_bot.py`** - Telegram API integration with rate limiting
4. **`database.py`** - SQLite database for deduplication and statistics

## 📁 Complete File Structure

```
telegram-hackathon-bot/
├── main.py                    # Main application entry point
├── scraper.py                 # Unstop.com scraping logic
├── telegram_bot.py           # Telegram bot functionality  
├── database.py               # Database management
├── setup.py                  # Configuration setup script
├── requirements.txt          # Python dependencies
├── .env                      # Environment configuration
├── .env.example             # Environment template
├── .gitignore               # Git ignore rules
├── README.md                # Comprehensive documentation
├── Procfile                 # Heroku deployment
└── deployment/              # Deployment configurations
    ├── github-actions.yml   # GitHub Actions workflow
    ├── render-deployment.md # Render platform guide
    ├── pythonanywhere-deployment.md # PythonAnywhere guide
    └── cron-script.sh       # Linux cron job script
```

## 🔧 Setup Instructions

### 1. Environment Setup
```bash
# Clone/download the project
cd telegram-hackathon-bot

# Create virtual environment (optional but recommended)
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run setup check
python setup.py
```

### 2. Telegram Bot Configuration

#### Get Bot Token:
1. Message **@BotFather** on Telegram
2. Send `/newbot`
3. Choose a name and username for your bot
4. Copy the token provided

#### Get Channel ID:
1. Add your bot to your channel as an administrator
2. Send a test message to your channel
3. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
4. Find your channel ID in the response (starts with `-100`)

#### Configure .env:
```bash
# Edit .env file with your credentials
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ
TELEGRAM_CHANNEL_ID=-1001234567890
```

### 3. Testing
```bash
# Test configuration and connections
python main.py test

# Run scraping and posting once
python main.py once

# Send status update
python main.py status
```

### 4. Production Deployment
```bash
# Start with scheduler (production mode)
python main.py
```

## 🚀 Deployment Options

### Option 1: PythonAnywhere (Free/Paid)
- **Free tier**: 1 scheduled task
- **Setup**: Upload files, install dependencies, create scheduled task
- **Command**: `python3.10 main.py once`
- **Schedule**: Every 6 hours
- **Cost**: Free (limited) or $5/month

### Option 2: Render (Free/Paid)
- **Setup**: Connect GitHub repo, add environment variables
- **Auto-deployment**: Pushes trigger deployments
- **Cost**: Free tier available, $7/month for always-on

### Option 3: GitHub Actions (Free)
- **Setup**: Add workflow file to `.github/workflows/`
- **Scheduled runs**: Using cron syntax
- **Secrets**: Store bot credentials in repository secrets
- **Cost**: Free (with usage limits)

### Option 4: VPS/Cloud Server
- **Setup**: Install Python, dependencies, setup cron job
- **Flexibility**: Full control over environment
- **Cost**: Variable ($5-20/month depending on provider)

### Option 5: Heroku
- **Setup**: Connect repo, add Procfile, set environment variables
- **Note**: Free tier discontinued, paid plans only
- **Cost**: $7/month minimum

## ⚙️ Configuration Options

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | - | ✅ |
| `TELEGRAM_CHANNEL_ID` | Channel ID or @username | - | ✅ |
| `SCRAPE_INTERVAL_HOURS` | Hours between scraping | 6 | ❌ |
| `TELEGRAM_RATE_LIMIT` | Messages per minute | 30 | ❌ |
| `SCRAPING_DELAY` | Delay between requests (seconds) | 2 | ❌ |
| `LOG_LEVEL` | Logging verbosity | INFO | ❌ |
| `ENVIRONMENT` | Environment type | development | ❌ |

## 🔍 Features

### Web Scraping
- **Multi-method scraping**: Selenium for dynamic content + aiohttp fallback
- **Pagination support**: Handles multiple pages of results
- **Robust selectors**: Multiple CSS selectors for different layouts
- **Error handling**: Graceful fallbacks when scraping fails
- **Rate limiting**: Respectful delays between requests

### Deduplication
- **Hash-based**: Uses title+URL hash to prevent duplicates
- **Database tracking**: SQLite database stores all hackathons
- **Posted status**: Tracks which hackathons have been posted

### Telegram Integration
- **Formatted messages**: Rich markdown formatting with emojis
- **Rate limiting**: Respects Telegram API limits
- **Error handling**: Retry logic with exponential backoff
- **Status updates**: Daily status reports with statistics

### Monitoring & Logging
- **Comprehensive logging**: File and console logging
- **Statistics tracking**: Database stores scraping statistics
- **Error tracking**: Detailed error logs and reporting
- **Health checks**: Built-in connection testing

## 🛠️ Usage Commands

```bash
# Test bot configuration
python main.py test

# Run once (manual execution)
python main.py once

# Send status update to channel
python main.py status

# Run with scheduler (production)
python main.py
```

## 📊 Message Format Example

```
🚀 *AI Hackathon 2024*

📅 *Date:* Dec 15-17, 2024

📝 Build innovative AI solutions that solve real-world problems. Open to students and professionals worldwide.

🔗 [Register Here](https://unstop.com/hackathons/ai-hackathon-2024)

#Hackathon #Competition #Tech #Coding
```

## 🔧 Customization

### Modify Message Format
Edit `format_hackathon_message()` in `telegram_bot.py`:
```python
def format_hackathon_message(self, hackathon: Dict) -> str:
    # Customize your message format here
    return f"🚀 {hackathon['title']}\n..."
```

### Add New Scraping Targets
Extend `scraper.py` to support additional websites:
```python
def scrape_other_site(self):
    # Add new scraping logic
    pass
```

### Multiple Channels
Modify `telegram_bot.py` to support multiple channels:
```python
CHANNELS = ['@channel1', '@channel2']
for channel in CHANNELS:
    await self.send_message_to_channel(message, channel)
```

## 🐛 Troubleshooting

### Common Issues

1. **Chrome/Selenium Issues**:
   ```bash
   pip install --upgrade webdriver-manager
   ```

2. **Telegram Rate Limits**:
   - Reduce `TELEGRAM_RATE_LIMIT` in .env
   - Increase delays between messages

3. **Scraping Failures**:
   - Website layout changed - update CSS selectors
   - Enable debug logging: `LOG_LEVEL=DEBUG`

4. **Import Errors**:
   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

### Debug Mode
```bash
# Enable debug logging in .env
LOG_LEVEL=DEBUG

# Run with verbose output
python main.py once
```

## 📈 Monitoring

### Log Files
- `bot.log` - Application logs
- Console output for real-time monitoring

### Database
- `hackathons.db` - SQLite database with all data
- View stats: `python -c "from database import Database; print(Database().get_stats())"`

### Telegram Status
- Daily status updates sent to channel
- Manual status: `python main.py status`

## 🔒 Security & Best Practices

1. **Environment Variables**: Store sensitive data in .env (never commit to git)
2. **Rate Limiting**: Built-in respect for API limits
3. **Error Handling**: Comprehensive error catching and logging
4. **Graceful Failures**: Bot continues running even if individual operations fail
5. **Backup Strategy**: Database is persistent across runs

## 💰 Cost Analysis

### Free Options:
- **GitHub Actions**: Free (with limits)
- **PythonAnywhere**: Free tier available
- **Render**: Free tier available

### Low-Cost Options:
- **PythonAnywhere Hacker**: $5/month
- **Render Web Service**: $7/month
- **DigitalOcean Droplet**: $6/month
- **AWS t2.micro**: ~$8/month

### Recommended for Production:
- **Render Web Service**: $7/month (easiest setup)
- **PythonAnywhere Hacker**: $5/month (good for Python)
- **VPS with cron**: $5-10/month (full control)

## 🎯 Success Metrics

- **Uptime**: >99% availability
- **Accuracy**: No duplicate posts
- **Performance**: <5 seconds per scraping cycle
- **Reliability**: Graceful error handling
- **User Experience**: Well-formatted, timely posts

---

**🎉 Your Telegram Hackathon Bot is ready for production!**

This implementation provides enterprise-grade reliability with comprehensive error handling, monitoring, and deployment options suitable for any scale of operation.
