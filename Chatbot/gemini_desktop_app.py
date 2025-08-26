# gemini_desktop_app.py - Single Instance Version

import sys
import os
import time
import socket
import threading
from PyQt6.QtCore import Qt, QPoint, QRect, QThread, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QMessageBox, QScrollArea, QTextEdit
from PyQt6.QtGui import QPixmap, QScreen, QPainter, QColor, QFont
from pynput import keyboard
from PIL import ImageGrab
import requests
from dotenv import load_dotenv
import pytesseract

# Load environment variables
load_dotenv()

# --- Configuration ---
SINGLE_INSTANCE_PORT = 12345  # Port for single instance check
CAPTURE_HOTKEY = {keyboard.Key.f12}  # F12 for screen capture
TOGGLE_UI_HOTKEY = {keyboard.Key.f11}  # F11 to show/hide UI

# API Configuration
GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("Warning: GEMINI_API_KEY not found in environment variables or .env file.")

# --- Single Instance Management ---
class SingleInstanceChecker:
    def __init__(self, port=SINGLE_INSTANCE_PORT):
        self.port = port
        self.socket = None
    
    def is_another_instance_running(self):
        """Check if another instance is already running"""
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(1)
            result = test_socket.connect_ex(('localhost', self.port))
            test_socket.close()
            return result == 0  # 0 means connection successful = another instance running
        except:
            return False
    
    def start_server(self):
        """Start the single instance server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('localhost', self.port))
            self.socket.listen(1)
            print(f"Single instance server started on port {self.port}")
            
            # Start server in background thread
            def server_thread():
                while True:
                    try:
                        conn, addr = self.socket.accept()
                        print(f"Connection from existing instance: {addr}")
                        conn.close()
                    except:
                        break
            
            threading.Thread(target=server_thread, daemon=True).start()
            return True
        except Exception as e:
            print(f"Failed to start single instance server: {e}")
            return False
    
    def stop_server(self):
        """Stop the single instance server"""
        if self.socket:
            self.socket.close()

# --- Helper Functions ---
def perform_ocr(image_path):
    """Uses pytesseract to extract text from an image."""
    try:
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        text = pytesseract.image_to_string(image_path)
        print(f"OCR extracted text: '{text.strip()}'")
        return text
    except Exception as e:
        print(f"Error during OCR: {e}")
        return None

def call_generative_ai_api(prompt):
    """Calls the Generative AI API with the given prompt."""
    if not API_KEY:
        return "Error: API Key not configured for Generative AI."

    headers = {"Content-Type": "application/json"}
    params = {"key": API_KEY}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "text/plain"}
    }

    print(f"\nCalling Generative AI with prompt: '{prompt}'")
    try:
        response = requests.post(GEMINI_API_BASE_URL, headers=headers, params=params, json=payload, timeout=30)
        response.raise_for_status()
        json_response = response.json()

        if json_response and json_response.get('candidates'):
            first_candidate = json_response['candidates'][0]
            if first_candidate.get('content') and first_candidate['content'].get('parts'):
                first_part = first_candidate['content']['parts'][0]
                if first_part.get('text'):
                    ai_response = first_part['text']
                    print(f"AI Response: {ai_response.strip()}")
                    return ai_response.strip()
        
        print("AI response structure unexpected:", json_response)
        return "Error: Could not parse AI response."

    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}")
        return f"Error connecting to AI: {e}"
    except Exception as e:
        print(f"An unexpected error occurred during API call: {e}")
        return f"Unexpected error: {e}"

# --- Hotkey Listener Thread ---
class HotkeyListener(QThread):
    capturePressed = pyqtSignal()
    toggleUIPressed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_keys = set()
        self.is_running = True

    def run(self):
        def on_press(key):
            if not self.is_running:
                return
                
            try:
                self.current_keys.add(key)
                
                if key == keyboard.Key.f12:
                    print("F12 (Capture) detected!")
                    self.capturePressed.emit()
                
                elif key == keyboard.Key.f11:
                    print("F11 (Toggle UI) detected!")
                    self.toggleUIPressed.emit()
                    
            except Exception as e:
                print(f"Error in on_press: {e}")

        def on_release(key):
            try:
                self.current_keys.discard(key)
                if key == keyboard.Key.esc and keyboard.Key.ctrl in self.current_keys:
                    print("Ctrl+Esc pressed, stopping listener")
                    self.is_running = False
                    return False
            except Exception as e:
                print(f"Error in on_release: {e}")

        try:
            print("Starting keyboard listener... F12=Capture, F11=Toggle UI")
            with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                listener.join()
        except Exception as e:
            print(f"Keyboard listener error: {e}")

    def stop(self):
        self.is_running = False
        self.quit()
        self.wait()

# --- Screen Capture Widget ---
class SelectionWindow(QWidget):
    selectionFinished = pyqtSignal(QRect)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.showFullScreen()

        self.screen = QApplication.primaryScreen()
        self.screenshot = self.screen.grabWindow(0)
        self.begin = QPoint()
        self.end = QPoint()
        self.selecting = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.screenshot)

        if self.selecting:
            painter.setPen(QColor(255, 0, 0, 200))
            painter.setBrush(QColor(0, 0, 255, 50))
            rect = QRect(self.begin, self.end).normalized()
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.begin = event.pos()
            self.end = event.pos()
            self.selecting = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.selecting:
            self.end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.selecting:
            self.selecting = False
            rect = QRect(self.begin, self.end).normalized()
            if not rect.isEmpty() and rect.width() > 0 and rect.height() > 0:
                self.selectionFinished.emit(rect)
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        super().keyPressEvent(event)

# --- Main Assistant Application ---
class MyAssistant(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_hotkey_listener()
        self.selection_window = None
        self.request_count = 0
        
        # Auto-hide timer
        self.auto_hide_timer = QTimer()
        self.auto_hide_timer.timeout.connect(self.auto_hide)
        self.auto_hide_timer.setSingleShot(True)
        
        # Start hidden
        self.hide()

    def setup_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle("Gemini Desktop Assistant")
        self.setGeometry(100, 100, 450, 350)
        self.offset = QPoint()

        # Main layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Status label
        self.status_label = QLabel("Ready - F12: Capture | F11: Toggle UI | Instance: Single")
        self.status_label.setStyleSheet("""
            color: white; 
            font-size: 12px; 
            font-weight: bold;
            padding: 8px; 
            background-color: rgba(0, 100, 200, 180); 
            border-radius: 5px;
            margin: 2px;
        """)
        self.layout.addWidget(self.status_label)

        # Create scrollable text area for responses
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: rgba(50, 50, 50, 200);
                border: 2px solid rgba(100, 100, 100, 150);
                border-radius: 8px;
            }
            QScrollBar:vertical {
                background-color: rgba(100, 100, 100, 100);
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(150, 150, 150, 150);
                border-radius: 6px;
            }
        """)
        
        # Text display widget
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setStyleSheet("""
            QTextEdit {
                color: #E0E0E0; 
                font-size: 11px; 
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: transparent;
                border: none;
                padding: 10px;
                line-height: 1.4;
            }
        """)
        self.result_display.setText("AI responses will appear here...\n\nPress F12 to capture screen area\nPress F11 to show/hide this window\n\nSingle instance mode: Extension won't create duplicates")
        
        self.scroll_area.setWidget(self.result_display)
        self.layout.addWidget(self.scroll_area)

        # Control buttons
        button_layout = QVBoxLayout()
        
        self.clear_button = QPushButton("Clear History")
        self.clear_button.clicked.connect(self.clear_history)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(200, 100, 100, 150); 
                color: white; 
                padding: 6px; 
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: rgba(220, 120, 120, 180);
            }
        """)
        button_layout.addWidget(self.clear_button)
        
        self.test_button = QPushButton("Test Capture")
        self.test_button.clicked.connect(self.start_screen_capture)
        self.test_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(100, 150, 100, 150); 
                color: white; 
                padding: 6px; 
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: rgba(120, 170, 120, 180);
            }
        """)
        button_layout.addWidget(self.test_button)
        
        self.layout.addLayout(button_layout)

    def setup_hotkey_listener(self):
        try:
            print("Setting up hotkey listener...")
            self.hotkey_thread = HotkeyListener()
            self.hotkey_thread.capturePressed.connect(self.start_screen_capture)
            self.hotkey_thread.toggleUIPressed.connect(self.toggle_visibility)
            self.hotkey_thread.start()
            print("Hotkey listener setup complete")
        except Exception as e:
            print(f"Hotkey setup error: {e}")

    def toggle_visibility(self):
        """Toggle the visibility of the assistant window"""
        if self.isVisible():
            print("Hiding assistant window")
            self.hide()
        else:
            print("Showing assistant window")
            self.show()
            self.raise_()
            self.activateWindow()

    def clear_history(self):
        """Clear the response history"""
        self.result_display.clear()
        self.result_display.setText("History cleared. Ready for new captures!\n\nPress F12 to capture screen area")
        self.request_count = 0
        self.update_status("History cleared - Ready for capture")

    def update_status(self, message, timeout=3000):
        """Update status message with optional auto-clear"""
        self.status_label.setText(message)
        if timeout > 0:
            QTimer.singleShot(timeout, lambda: self.status_label.setText("Ready - F12: Capture | F11: Toggle UI | Instance: Single"))

    def add_response(self, question, answer):
        """Add a new Q&A pair to the display"""
        self.request_count += 1
        timestamp = time.strftime("%H:%M:%S")
        
        # Format the new response
        separator = "\n" + "="*50 + "\n"
        new_content = f"""
Request #{self.request_count} - {timestamp}
Question: {question[:100]}{'...' if len(question) > 100 else ''}
Answer: {answer}
"""
        
        # Add to existing content
        current_content = self.result_display.toPlainText()
        if "AI responses will appear here..." in current_content:
            self.result_display.clear()
            new_content = new_content.strip()
        
        self.result_display.append(separator + new_content)
        
        # Auto-scroll to bottom
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)

    def mouseReleaseEvent(self, event):
        self.offset = QPoint()

    def start_screen_capture(self):
        print("Starting screen capture...")
        self.update_status("Select an area on your screen...", 0)
        self.hide()

        self.selection_window = SelectionWindow()
        self.selection_window.selectionFinished.connect(self.process_selection)
        self.selection_window.show()

    def process_selection(self, rect: QRect):
        self.show()
        self.update_status("Processing selected area...", 0)
        QApplication.processEvents()

        # Capture the selected region
        screen = QApplication.primaryScreen()
        screenshot_pixmap = screen.grabWindow(0, rect.x(), rect.y(), rect.width(), rect.height())

        if screenshot_pixmap.isNull():
            self.update_status("Error: Could not capture screen.", 5000)
            self.add_response("Screen capture failed", "Screenshot failed. Check your system permissions.")
            return

        # Save to a temporary file for OCR
        temp_image_path = "temp_screenshot.png"
        screenshot_pixmap.save(temp_image_path)

        # Perform OCR
        self.update_status("Extracting text from image...", 0)
        extracted_text = perform_ocr(temp_image_path)
        
        # Clean up temp file
        try:
            os.remove(temp_image_path)
        except:
            pass

        if extracted_text and extracted_text.strip():
            self.update_status("Text extracted. Calling AI...", 0)
            ai_response = call_generative_ai_api(extracted_text)
            self.add_response(extracted_text.strip(), ai_response)
        else:
            self.update_status("No text found in selection.", 5000)
            self.add_response("No text detected", "Could not extract text from the selected area.")

        self.update_status("Ready - F12: Capture | F11: Toggle UI | Instance: Single")

    def auto_hide(self):
        """Auto-hide the window after inactivity"""
        if self.isVisible():
            print("Auto-hiding assistant window")
            self.hide()

    def closeEvent(self, event):
        """Clean up when closing"""
        if hasattr(self, 'hotkey_thread'):
            self.hotkey_thread.stop()
        if hasattr(self, 'auto_hide_timer'):
            self.auto_hide_timer.stop()
        event.accept()

# --- Main Application Entry Point ---
if __name__ == "__main__":
    # Single instance check
    instance_checker = SingleInstanceChecker()
    
    if instance_checker.is_another_instance_running():
        print("Another instance is already running. Exiting...")
        sys.exit(1)
    
    # Create .env file if it doesn't exist
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("GEMINI_API_KEY=\"YOUR_GEMINI_API_KEY_HERE\"\n")
        print("\n*** IMPORTANT: A '.env' file has been created. ***")
        print("Please add your Gemini API Key to the .env file.")

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Start single instance server
    instance_checker.start_server()
    
    assistant = MyAssistant()
    
    print("\n" + "="*50)
    print("Gemini Desktop Assistant Started (Single Instance)")
    print("="*50)
    print("Hotkeys:")
    print("  F12  - Capture screen area")
    print("  F11  - Show/Hide assistant window")
    print("  Ctrl+Esc - Stop hotkey listener")
    print("="*50)
    
    try:
        sys.exit(app.exec())
    finally:
        instance_checker.stop_server()