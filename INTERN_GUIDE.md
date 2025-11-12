# Quick Start Guide for Intern

## 🎯 What is this?

This is a simple service that lets you request data downloads without needing the API key. Just submit a request, and you'll get notified on Telegram when it's done!

## 📱 How to Use

### First Time Setup

1. **Make sure you have Python 3** installed:
   ```bash
   python3 --version
   ```

2. **Install requests library** (if not already installed):
   ```bash
   pip install requests
   ```

3. **You're ready to go!**

### Requesting a Download

Use the simple `client.py` script:

```bash
python client.py \
  --exchange binance \
  --symbols BTC-USDT ETH-USDT \
  --start-date 2024-01-01 \
  --end-date 2024-01-02
```

**You'll get:**
- A Job ID (e.g., `Job ID: 123`)
- A Telegram notification when it starts
- A Telegram notification when it completes (or fails)

### Checking Status

```bash
python client.py --job-id 123
```

### Listing Your Recent Requests

```bash
python client.py --list-jobs
```

## 📋 Examples

### Example 1: Download trades for BTC and ETH

```bash
python client.py \
  --exchange binance \
  --symbols BTC-USDT ETH-USDT \
  --start-date 2024-01-01 \
  --end-date 2024-01-31
```

### Example 2: Download multiple data types

```bash
python client.py \
  --exchange binance \
  --symbols BTC-USDT \
  --start-date 2024-01-01 \
  --end-date 2024-01-02 \
  --data-types trades book_change_l2
```

### Example 3: Check your last 10 jobs

```bash
python client.py --list-jobs --limit 10
```

## 📍 Where is My Data?

Downloaded data will be in: `./datasets/`

The files are organized by exchange and date.

## ⏱ How Long Does it Take?

- Small downloads (1-2 days): 10-20 minutes
- Medium downloads (1 week): 30-45 minutes
- Large downloads (1 month): 1-2 hours

**Important:** You don't need to wait! The download runs in the background, and you'll get a Telegram notification when it's done.

## 🆘 Common Issues

### "Connection refused" error

The service might not be running. Ask your supervisor to start it:
```bash
docker-compose up -d
```

### "User not authorized" error

Your username needs to be added to the allowed users list. Ask your supervisor.

### "Job failed" notification

Check the error message in Telegram or run:
```bash
python client.py --job-id <YOUR_JOB_ID>
```

Common reasons:
- Invalid date format (use YYYY-MM-DD)
- Invalid exchange name
- Invalid symbol name
- Network issues

## 💡 Pro Tips

1. **Split large downloads**: Instead of downloading 1 year at once, split it into months
2. **Check before downloading**: Make sure you really need the data
3. **Use list-jobs often**: Keep track of what you've requested
4. **Note your Job IDs**: Write them down so you can check status later

## 🔔 Telegram Notifications

You should see messages like:

**When job starts:**
```
🚀 Download Started

Job ID: 123
Exchange: binance
Symbols: BTC-USDT, ETH-USDT
Date Range: 2024-01-01 to 2024-01-02
Requested by: your_username
```

**When job completes:**
```
✅ Download Completed

Job ID: 123
Exchange: binance
Symbols: BTC-USDT, ETH-USDT
Duration: 15.3 minutes
```

## 📞 Need Help?

1. Check the job status with `--job-id`
2. Look at recent jobs with `--list-jobs`
3. If still stuck, contact your supervisor with the Job ID

## ✅ Checklist Before Requesting Download

- [ ] I know the exchange name (e.g., binance, coinbase)
- [ ] I have the correct symbol names (e.g., BTC-USDT)
- [ ] My dates are in YYYY-MM-DD format
- [ ] I checked that this data hasn't been downloaded already
- [ ] The date range is reasonable (not too large)

Happy downloading! 🚀