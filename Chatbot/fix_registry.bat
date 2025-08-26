@echo off
echo Fixing registry path...

REM Remove the incorrect registry entry first
reg delete "HKEY_CURRENT_USER\Software\Google\Chrome\NativeMessagingHosts\com.gemini.assistant" /f

REM Add the correct path (note: single native_messaging_host folder)
set MANIFEST_PATH=C:\Users\R0ahu\OneDrive\Documents\Programming\Python\Chatbot\native_messaging_host\com.gemini.assistant.json

echo Registering with correct path: %MANIFEST_PATH%
reg add "HKEY_CURRENT_USER\Software\Google\Chrome\NativeMessagingHosts\com.gemini.assistant" /ve /t REG_SZ /d "%MANIFEST_PATH%" /f

echo Registry fixed!
echo.
echo Verifying the manifest file exists...
if exist "%MANIFEST_PATH%" (
    echo ✅ Manifest file found at: %MANIFEST_PATH%
) else (
    echo ❌ Manifest file NOT found at: %MANIFEST_PATH%
    echo Please check if the file exists or adjust the path
)

pause