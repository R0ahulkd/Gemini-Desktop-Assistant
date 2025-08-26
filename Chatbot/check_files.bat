@echo off
echo Checking your current files...
echo.

echo === Contents of launch_host.bat ===
type "native_messaging_host\launch_host.bat"
echo.

echo === Contents of host_script.py (first 20 lines) ===
powershell "Get-Content 'native_messaging_host\host_script.py' | Select-Object -First 20"
echo.

echo === Contents of com.gemini.assistant.json ===
type "native_messaging_host\com.gemini.assistant.json"
echo.

echo === Python executable test ===
python --version
where python
echo.

pause