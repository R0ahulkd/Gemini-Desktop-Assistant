@echo off
echo Setting up Gemini Desktop Assistant...

REM Step 1: Install Python dependencies (if not already installed)
echo Installing Python dependencies...
pip install PyQt6 pynput pillow requests python-dotenv pytesseract

REM Step 2: Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    echo GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE" > .env
    echo Please edit the .env file and add your actual Gemini API key
)

REM Step 3: Register native messaging host
echo Registering native messaging host...
set MANIFEST_PATH=%~dp0native_messaging_host\com.gemini.assistant.json
reg add "HKEY_CURRENT_USER\Software\Google\Chrome\NativeMessagingHosts\com.gemini.assistant" /ve /t REG_SZ /d "%MANIFEST_PATH%" /f

echo Setup complete!
echo.
echo Next steps:
echo 1. Edit the .env file with your Gemini API key
echo 2. Load the Chrome extension from the extension folder
echo 3. Update com.gemini.assistant.json with your actual extension ID
echo 4. Run the Python app: python gemini_desktop_app.py
pause