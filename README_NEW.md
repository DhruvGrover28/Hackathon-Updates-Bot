# Telegram Hackathon Bot

A production-ready Telegram bot that automatically scrapes hackathon listings from multiple websites and posts updates to your Telegram channel.

## Features

- **Multi-source scraping**: Automatically scrapes hackathons from Unstop.com, DevPost.com, and Devfolio.co
- **Real-time updates**: Schedules automatic scraping every 6 hours
- **Smart deduplication**: Prevents posting duplicate hackathons using hash-based detection
- **Comprehensive coverage**: Includes both live scraping and curated hackathon database
- **Robust error handling**: Continues operation even if individual sources fail
- **Database persistence**: SQLite database stores all hackathons and posting status
- **Rate limiting**: Respects Telegram API limits with built-in delays
- **Unicode safe**: All output is clean and compatible with various terminal encodings

## Architecture

### Core Components

- **clean_auto_bot.py**: Main scheduler that orchestrates all operations
- **live_scraper.py**: Real-time scraping engine using Selenium and requests
- **comprehensive_scraper.py**: Curated hackathon database with 2025 events
- **telegram_bot.py**: Telegram API integration with formatting and rate limiting
- **database.py**: SQLite database management with deduplication
- **simple_poster.py**: Utility for posting any unposted hackathons

### Scraping Strategy

1. **Requests-first approach**: Attempts lightweight HTTP requests initially
2. **Selenium fallback**: Uses Chrome WebDriver for dynamic content when needed
3. **Multiple selectors**: Tries various CSS selectors to find hackathon elements
4. **Data validation**: Ensures extracted data meets quality standards before posting

## Installation

### Prerequisites

- Python 3.8 or higher
- Chrome browser (for Selenium WebDriver)
- Telegram Bot Token
- Telegram Channel

### Setup

1. Clone the repository:
```bash
git clone https://github.com/DhruvGrover28/Hackathon-Updates-Bot.git
cd Hackathon-Updates-Bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` file with your credentials:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=@your_channel_username
```

### Getting Telegram Credentials

1. **Bot Token**: Message @BotFather on Telegram to create a new bot
2. **Channel ID**: Create a public channel and use @username format, or get numeric ID for private channels

## Usage

### Local Development

Run the bot locally:
```bash
python clean_auto_bot.py
```

### Manual Operations

Test live scraping:
```bash
python live_scraper.py
```

Post any unposted hackathons:
```bash
python simple_poster.py
```

Run comprehensive scraping:
```bash
python comprehensive_scraper.py
```

## Deployment

### Render (Recommended)

1. Create account at render.com
2. Connect your GitHub repository
3. Add environment variables in Render dashboard
4. Deploy automatically from main branch

### Heroku

1. Install Heroku CLI
2. Create new Heroku app
3. Set environment variables
4. Deploy using Git:
```bash
heroku git:remote -a your-app-name
git push heroku main
```

### Other Platforms

The bot works on any platform supporting Python and Chrome WebDriver:
- Render
- PythonAnywhere
- DigitalOcean
- AWS
- Google Cloud Platform

## Scheduling

The bot runs on the following schedule:

- **Live scraping**: Every 6 hours
- **Comprehensive scraping**: Daily at 9:00 AM
- **Posting check**: Every 2 hours
- **Initial run**: Immediately on startup

## Database Schema

SQLite database with the following structure:

### hackathons table
- id (PRIMARY KEY)
- title (TEXT)
- description (TEXT)
- date_info (TEXT)
- url (TEXT)
- hash (TEXT UNIQUE) - for deduplication
- posted_to_channel (BOOLEAN)
- created_at (TIMESTAMP)

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| TELEGRAM_BOT_TOKEN | Bot token from @BotFather | Yes |
| TELEGRAM_CHANNEL_ID | Channel username (@channel) or ID | Yes |

### Customization

- **Scraping frequency**: Modify schedule in `clean_auto_bot.py`
- **Target websites**: Add new scrapers in `live_scraper.py`
- **Message format**: Update templates in `telegram_bot.py`
- **Database location**: Change path in `database.py`

## Monitoring

### Logs

The bot provides comprehensive logging:
- INFO: Normal operations and statistics
- WARNING: Recoverable issues
- ERROR: Failed operations

### Database Statistics

Check current status:
```python
from database import Database
db = Database()
stats = db.get_stats()
print(f"Total: {stats['total']}, Posted: {stats['posted']}")
```

## Troubleshooting

### Common Issues

**Chrome WebDriver errors**:
- Ensure Chrome browser is installed
- WebDriver will auto-download compatible version

**Unicode encoding errors**:
- All emojis have been removed for compatibility
- Use UTF-8 terminal encoding if available

**Telegram API errors**:
- Check bot token validity
- Ensure bot is added to target channel as admin
- Verify channel ID format (@username or numeric)

**Memory usage**:
- Bot automatically closes WebDriver sessions
- Database size grows with hackathon count

### Performance Optimization

- **Headless browsing**: Chrome runs in headless mode by default
- **Request caching**: HTTP sessions reuse connections
- **Selective scraping**: Only processes new/updated content
- **Batch operations**: Groups database operations for efficiency

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This bot is for educational purposes. Ensure compliance with website terms of service and robots.txt files. Use respectful scraping practices with appropriate delays.

## Support

For issues and questions:
1. Check existing GitHub issues
2. Create new issue with detailed description
3. Include logs and error messages
4. Specify environment details (OS, Python version)

---

Built with Python, Selenium, BeautifulSoup, and python-telegram-bot
