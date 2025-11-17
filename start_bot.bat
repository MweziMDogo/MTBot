@echo off
echo.
echo ========================================
echo   Miner Tycon Bot - Starting...
echo ========================================
echo.

REM Check if .env file exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo.
    echo Please create a .env file with your Discord bot token:
    echo    DISCORD_BOT_TOKEN=your_token_here
    echo.
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Run the bot
echo [OK] Starting bot...
echo.
python bot.py

if errorlevel 1 (
    echo.
    echo [ERROR] Bot crashed. Check the error messages above.
    echo.
    echo If you see dependency errors, run setup.bat first:
    echo    setup.bat
    echo.
    pause
    exit /b 1
)
