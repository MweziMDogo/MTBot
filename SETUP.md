# Setup & Deployment Guide

## Quick Start (Windows)

### 1. Install Python Dependencies
```bash
setup.bat
```
This will automatically install all required packages from `requirements.txt`.

### 2. Configure Bot Token
Create a `.env` file in the bot directory:
```
DISCORD_BOT_TOKEN=your_discord_bot_token_here
```

### 3. Start the Bot
```bash
start_bot.bat
```

The bot will now connect to Discord and be ready for commands!

---

## Manual Setup (Alternative)

If batch files don't work for you:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python bot.py
```

---

## Troubleshooting

### "Python not found"
- Python is not installed or not in PATH
- Install from https://www.python.org/
- **Important:** Check "Add Python to PATH" during installation
- Restart your computer after installation

### "ModuleNotFoundError: No module named 'discord'"
- Run `setup.bat` to install dependencies
- Or manually run: `pip install -r requirements.txt`

### ".env file not found"
- Create a `.env` file in the bot directory
- Add your Discord bot token: `DISCORD_BOT_TOKEN=your_token_here`
- Get a token from https://discord.com/developers/applications

### Bot crashes immediately
- Check that `.env` file has your valid bot token
- Run `setup.bat` again to ensure all dependencies are installed
- Check logs in `logs/` directory for detailed errors

---

## Project Structure
```
Miner Tycon Bot/
├── bot.py                 # Entry point
├── requirements.txt       # Dependencies (auto-installed by setup.bat)
├── .env                   # Bot token (create this)
├── setup.bat             # One-click setup (Windows)
├── start_bot.bat         # One-click start (Windows)
├── commands/             # Bot commands
├── database/             # SQLite database
├── config/               # Configuration
├── modals/               # Discord modals
├── views/                # Discord UI components
├── utils/                # Utilities
├── scripts/              # Scripts (populate_sample_data.py)
└── logs/                 # Runtime logs
```

---

## For Linux/Mac Users

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "DISCORD_BOT_TOKEN=your_token_here" > .env

# Run the bot
python bot.py
```

---

## Stopping the Bot

**Windows (Batch):** Close the `start_bot.bat` window or press `Ctrl+C`

**Terminal:** Press `Ctrl+C` to stop the bot gracefully

---

## Support

For issues:
1. Check the `logs/` directory for error messages
2. Verify `.env` file has a valid token
3. Run `setup.bat` to reinstall dependencies
4. Check Discord bot permissions in Developer Portal

