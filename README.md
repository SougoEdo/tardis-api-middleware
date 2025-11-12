# Tardis Download Service

A secure API service for managing Tardis historical data downloads with Telegram notifications.

## 🎯 Features

- ✅ **Secure API**: Keep your Tardis API key secure, only accessible to the server
- 📱 **Telegram Notifications**: Real-time updates on download progress
- 📊 **Job Tracking**: SQLite database to track all download jobs
- 🔒 **User Authentication**: Control who can submit download requests
- 🐳 **Docker Ready**: Easy deployment with Docker Compose
- 🚀 **Background Processing**: Non-blocking downloads with status tracking
- 📝 **Auto Documentation**: Interactive API docs at `/docs`

## 📋 Prerequisites

- Docker and Docker Compose
- Tardis API key (from https://tardis.dev/)
- Telegram Bot (create with @BotFather)

## 🚀 Quick Start

### 1. Clone or Copy the Project

```bash
mkdir tardis-download-service
cd tardis-download-service
# Copy all files to this directory
```

### 2. Create Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow instructions
3. Save the bot token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
4. Get your chat ID:
   - Send a message to your bot
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Look for `"chat":{"id":123456789}` in the response

### 3. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Required variables:**
```bash
TARDIS_API_KEY=your_tardis_api_key_here
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

**Optional variables:**
```bash
# Restrict access to specific users (comma-separated)
ALLOWED_USERS=intern_username,another_user

# Add API token authentication
API_TOKEN=your_secret_token_here
```

### 4. Start the Service

```bash
# Build and start
docker-compose up -d

# Check logs
docker-compose logs -f

# Check if service is running
curl http://localhost:8000/health
```

## 📖 Usage

### Option 1: Using the Python Client (Recommended for Intern)

The intern can use the simple Python client script:

```bash
# Submit a download job
python client.py \
  --exchange binance \
  --symbols BTC-USDT ETH-USDT \
  --start-date 2024-01-01 \
  --end-date 2024-01-02

# Check job status
python client.py --job-id 123

# List recent jobs
python client.py --list-jobs
```

**If API token is enabled:**
```bash
python client.py \
  --api-token your_secret_token \
  --exchange binance \
  --symbols BTC-USDT \
  --start-date 2024-01-01 \
  --end-date 2024-01-02
```

### Option 2: Using cURL

```bash
# Submit download job
curl -X POST "http://localhost:8000/download" \
  -H "Content-Type: application/json" \
  -H "X-Username: intern_name" \
  -d '{
    "exchange": "binance",
    "symbols": ["BTC-USDT", "ETH-USDT"],
    "start_date": "2024-01-01",
    "end_date": "2024-01-02",
    "data_types": ["trades"]
  }'

# Check job status
curl "http://localhost:8000/jobs/1" \
  -H "X-Username: intern_name"

# List all jobs
curl "http://localhost:8000/jobs" \
  -H "X-Username: intern_name"
```

### Option 3: Interactive API Documentation

Visit `http://localhost:8000/docs` in your browser for interactive API documentation.

## 🔔 Telegram Notifications

You'll receive notifications for:
- ✅ **Job Started**: When download begins
- ✅ **Job Completed**: When download finishes successfully
- ❌ **Job Failed**: If download encounters an error

Example notification:
```
🚀 Download Started

Job ID: 123
Exchange: binance
Symbols: BTC-USDT, ETH-USDT
Date Range: 2024-01-01 to 2024-01-02
Requested by: intern_name
```

## 📁 File Structure

```
download-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── models.py            # Pydantic models
│   ├── database.py          # SQLite operations
│   ├── downloader.py        # Download logic
│   └── telegram_notifier.py # Telegram integration
├── datasets/                # Downloaded data (mounted volume)
├── data/                    # SQLite database (mounted volume)
├── logs/                    # Application logs (mounted volume)
├── client.py                # Python client script
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## 🔐 Security Considerations

1. **API Key Protection**: The Tardis API key is only in the Docker container environment
2. **User Authentication**: Use `ALLOWED_USERS` to restrict access
3. **API Token**: Optionally add `API_TOKEN` for additional security
4. **Network Isolation**: Run on internal network, don't expose to public internet

## 🛠 Advanced Configuration

### Customize Output Path

Set a different default output path:
```bash
DEFAULT_OUTPUT_PATH=/data/tardis-downloads
```

### Change Port

Modify in `docker-compose.yml`:
```yaml
ports:
  - "9000:8000"  # External:Internal
```

### Add More Allowed Users

```bash
ALLOWED_USERS=intern1,intern2,developer1
```

## 📊 Monitoring

### Check Service Health

```bash
curl http://localhost:8000/health
```

### View Logs

```bash
# Real-time logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Logs for specific service
docker-compose logs download-service
```

### Database Location

The SQLite database is stored in `./data/downloads.db` and persists between restarts.

## 🔄 Maintenance

### Update the Service

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

### Backup Database

```bash
cp data/downloads.db data/downloads.db.backup
```

### Clean Up Old Data

```bash
# Remove old datasets
rm -rf datasets/old_data

# Restart service
docker-compose restart
```

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs

# Verify environment variables
docker-compose config

# Check port availability
netstat -tuln | grep 8000
```

### Telegram Notifications Not Working

1. Verify bot token: `echo $TELEGRAM_BOT_TOKEN`
2. Check chat ID is correct
3. Ensure bot was started (send `/start` to your bot)
4. For groups: ensure bot is added and has permission to send messages

### Downloads Failing

1. Check Tardis API key is valid
2. Verify network connectivity from container
3. Check logs for specific error messages
4. Ensure sufficient disk space in `./datasets`

### Permission Issues

```bash
# Fix permissions on mounted volumes
sudo chown -R $USER:$USER datasets data logs
```

## 📝 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Detailed health status |
| POST | `/download` | Submit download job |
| GET | `/jobs` | List all jobs |
| GET | `/jobs/{job_id}` | Get specific job details |
| GET | `/jobs/{job_id}/status` | Quick status check |
| GET | `/docs` | Interactive API documentation |

## 🤝 For the Intern

### Daily Workflow

1. **Submit a download request:**
   ```bash
   python client.py --exchange binance --symbols BTC-USDT \
                    --start-date 2024-01-01 --end-date 2024-01-02
   ```

2. **You'll receive a Job ID** (e.g., Job ID: 123)

3. **Watch Telegram** for notifications about progress

4. **Check status anytime:**
   ```bash
   python client.py --job-id 123
   ```

5. **Downloaded data** will be in `./datasets/` directory

### Tips

- Downloads run in background - you don't need to wait
- Large downloads may take 30-60 minutes
- You'll get notified on Telegram when complete
- Use `--list-jobs` to see all your recent requests
- Data is organized by exchange/date in the datasets folder

## 📧 Support

For issues or questions, contact your supervisor or check the logs:
```bash
docker-compose logs -f
```

## 📄 License

Internal use only.