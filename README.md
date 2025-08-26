Gemini Desktop Assistant ✨

Description
The Gemini Desktop Assistant is a powerful tool that integrates Google's Generative AI with your desktop environment. This project consists of a Chrome extension and a Python desktop application that work together via Native Messaging. With a simple keyboard shortcut or a click on the extension icon, you can activate the assistant, capture a selected area of your screen, and get an instant AI-powered response based on the extracted text. This is a single-instance application, ensuring it runs efficiently without creating duplicate processes.

Features ⭐

Seamless Integration: Connects your Chrome browser to a local Python application using Native Messaging.

Hotkey Activation: Use Ctrl + Alt + G to start a screen capture and Ctrl + Alt + H to toggle the assistant's UI.

Manual Activation: Click the extension icon in your browser to manually launch the assistant.

Screen OCR: Automatically extracts text from any selected area of your screen.

AI-Powered Responses: Sends the captured text to the Gemini API to generate instant answers and insights.

Single-Instance Mode: The application ensures only one instance is running at a time, preventing resource conflicts.

Project Structure 📁
The project is divided into two main parts: the Chrome Extension and the Python Desktop Application.

Chrome Extension Files 💻
manifest.json: Defines the extension's name, version, permissions, and command hotkeys. It also specifies the popup to be used when the icon is clicked.

background.js: A service worker that listens for the hotkey command and messages from the popup, then triggers the native messaging host.

popup.html: The HTML file for the extension's popup, which contains a button to manually activate the assistant.

popup.js: The JavaScript file for the popup that handles button clicks and sends a message to the background.js script.

Python Application Files 🐍
com.gemini.assistant.json: The Native Messaging Host Manifest file. This JSON file must be registered with the operating system so Chrome knows where to find the Python host script.

host_script.py: The Python script that is launched by the native messaging host. It's responsible for managing and launching the main desktop application (gemini_desktop_app.py) as a single instance.

gemini_desktop_app.py: The main Python application built with PyQt6. It handles the UI, screen capture, OCR using pytesseract, and communication with the Gemini API.

.env: A configuration file to securely store your API key.

Installation and Setup 🔧
Step 1: Clone the Repository
Start by cloning the project from GitHub.

Bash

git clone https://github.com/R0ahulkd/Gemini-Desktop-Assistant
cd your-repo-name
Step 2: Set up the Python Environment
Install Python: Ensure you have Python 3.9 or newer installed.

Install dependencies: Navigate to the project directory and install the required Python libraries.

Bash

pip install -r requirements.txt
(Note: You'll need to create a requirements.txt file listing pyqt6, pynput, requests, python-dotenv, psutil, pytesseract, and pywin32.)

Install Tesseract OCR: Download and install the Tesseract OCR engine from the official GitHub page. Remember to add tesseract.exe to your system's PATH or specify its path in gemini_desktop_app.py.

Step 3: Configure the Gemini API Key
Obtain a Gemini API key from Google AI Studio.

Create a file named .env in the same directory as gemini_desktop_app.py.

Add your API key to the .env file in the following format:

GEMINI_API_KEY="YOUR_API_KEY_HERE"
Step 4: Register the Native Messaging Host (Windows)
This is a crucial step that allows your Chrome extension to communicate with your Python application.

Modify com.gemini.assistant.json:

Update the "path" property to the full, absolute path of your launch_host.bat file. For example:
"path": "C:\\Users\\YourUser\\Path\\to\\your-repo\\native_messaging_host\\launch_host.bat"

Update the "allowed_origins" with your extension's ID. You can find this ID on the Chrome extensions management page (chrome://extensions).

Create a Registry Entry:

Open Notepad and create a file with the .reg extension (e.g., register_host.reg).

Copy and paste the following content into the file, ensuring the path to com.gemini.assistant.json is correct. The path should be the full path to your Native Messaging Host Manifest file.

Code snippet

Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\Software\Google\Chrome\NativeMessagingHosts\com.gemini.assistant]
@="C:\\Users\\YourUser\\Path\\to\\your-repo\\com.gemini.assistant.json"
Save the file and double-click it to add the entry to your Windows Registry. Click "Yes" when prompted.

Step 5: Install and Set up the Chrome Extension
Open your Chrome browser and navigate to chrome://extensions.

Enable "Developer mode" by toggling the switch in the top-right corner.

Click "Load unpacked" and select the chrome-extension directory from your project.

Once loaded, a new extension icon will appear in your toolbar.

Navigate to chrome://extensions/shortcuts to view and customize your hotkeys. The default shortcut for the assistant is Ctrl + Alt + G.

How to Use 🚀
Launch the Assistant: You can either click the extension icon in your browser and then click the "Activate" button, or use the Ctrl + Alt + G hotkey.

Select an Area: Your screen will dim, and a crosshair will appear. Click and drag to select the area you want to capture.

Receive Response: The application will process the image, extract text using OCR, and send it to the Gemini API. The AI's response will appear in the assistant's UI window.

Toggle UI: Use the Ctrl + Alt + H hotkey to hide or show the assistant window.

Clear History: Click the "Clear History" button to erase previous responses.

Screenshots & Video Demonstration 📸
Showcase your project in action! You can embed images and a video here to give users a quick look at the features.

Screenshot 1: Add a screenshot of the assistant UI here.

<img width="1920" height="1080" alt="{BC98065B-C72D-401A-B46E-74B99772A9F0}" src="https://github.com/user-attachments/assets/769bd24c-705a-4672-8af5-9e4babebe490" />


Screenshot 2: Add a screenshot of the screen capture process here.

<img width="1920" height="1080" alt="{270539B9-C861-4204-AC78-46DD807A0D07}" src="https://github.com/user-attachments/assets/f66d9428-8488-42c0-b3c2-4edaf873127e" />


Video Demo: Add a link to a video demonstration.

[Watch a video demonstration here](https://drive.google.com/file/d/1ZPeBCvVm0K0_Ff0CeWr8eqzpXHwPpgYI/view?usp=sharing)

Contributing 🤝
We welcome contributions! Please feel free to fork the repository, make changes, and submit a pull request.

