@echo off
echo.
echo ========================================
echo   Miner Tycon Bot - Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [OK] Python found
python --version

REM Install dependencies
echo.
echo [INFO] Installing dependencies from requirements.txt...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [OK] Dependencies installed successfully!
echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Create a .env file with your Discord bot token:
echo    DISCORD_BOT_TOKEN=your_token_here
echo.
echo 2. Run start_bot.bat to start the bot
echo.
pause
