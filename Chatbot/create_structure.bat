@echo off
echo Creating correct directory structure...

REM Create the native_messaging_host directory if it doesn't exist
if not exist "native_messaging_host" (
    mkdir native_messaging_host
    echo Created native_messaging_host directory
)

REM Create the Chrome extension directory if it doesn't exist
if not exist "chrome_extension" (
    mkdir chrome_extension
    echo Created chrome_extension directory
)

echo.
echo Directory structure should be:
echo Chatbot/
echo ├── native_messaging_host/
echo │   ├── com.gemini.assistant.json
echo │   ├── host_script.py
echo │   └── launch_host.bat
echo ├── chrome_extension/
echo │   ├── manifest.json
echo │   ├── background.js
echo │   ├── popup.html
echo │   └── popup.js
echo ├── gemini_desktop_app.py
echo ├── .env
echo └── test files...
echo.

pause