import sys
import json
import struct
import subprocess
import os
import psutil
import time

def is_app_running():
    """Check if gemini_desktop_app.py is already running"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and any('gemini_desktop_app.py' in arg for arg in proc.info['cmdline']):
                    print(f"Found existing process: PID {proc.info['pid']}")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        print(f"Error checking processes: {e}")
    return False

def kill_existing_app():
    """Kill existing instances of the app"""
    killed_count = 0
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and any('gemini_desktop_app.py' in arg for arg in proc.info['cmdline']):
                    print(f"Killing existing process: PID {proc.info['pid']}")
                    proc.terminate()
                    killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        print(f"Error killing processes: {e}")
    
    if killed_count > 0:
        time.sleep(1)  # Wait for processes to terminate
    return killed_count

# Read the message from Chrome
raw_length = sys.stdin.buffer.read(4)
if not raw_length:
    sys.exit(0)

message_length = struct.unpack('@I', raw_length)[0]
message = sys.stdin.buffer.read(message_length).decode('utf-8')
data = json.loads(message)

if data.get("action") == "trigger_assistant":
    app_path = r'C:\Users\R0ahu\OneDrive\Documents\Programming\Python\Chatbot\gemini_desktop_app.py'
    
    # Check if app is already running
    if is_app_running():
        print("App is already running. Killing existing instances...")
        killed = kill_existing_app()
        response_message = f"Restarted assistant (killed {killed} existing instances)"
    else:
        response_message = "Assistant launched"
    
    # Launch the Python application
    try:
        subprocess.Popen([sys.executable, app_path], 
                        creationflags=subprocess.CREATE_NO_WINDOW)
        print(f"Launched: {app_path}")
        
        # Send response back to Chrome
        response = {"status": "success", "message": response_message}
    except Exception as e:
        print(f"Error launching app: {e}")
        response = {"status": "error", "message": f"Failed to launch: {e}"}
    
    response_json = json.dumps(response)
    response_length = struct.pack('@I', len(response_json))
    sys.stdout.buffer.write(response_length)
    sys.stdout.buffer.write(response_json.encode('utf-8'))
    sys.stdout.buffer.flush()