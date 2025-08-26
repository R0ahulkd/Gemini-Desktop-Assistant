@ECHO OFF
echo Launching Native Host: %date% %time% >> "C:\Users\R0ahu\Desktop\host_launch.log"
"C:\Users\R0ahu\AppData\Local\Programs\Python\Python313\python.exe" "C:\Users\R0ahu\OneDrive\Documents\Programming\Python\Chatbot\native_messaging_host\host_script.py"
echo Exit code: %errorlevel% >> "C:\Users\R0ahu\Desktop\host_launch.log"