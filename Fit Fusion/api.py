import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QStackedWidget, \
    QTextEdit, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPalette, QBrush
import google.generativeai as genai
import speech_recognition as sr  # Added for voice recognition



class FitnessAIAssistant:
    def __init__(self, api_key):
        """Initialize the Fitness AI Assistant."""
        self.api_key = api_key
        try:
            print("Initializing FitnessAIAssistant...")
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.system_prompt = "You are an expert in fitness, health, and nutrition."
            self.chat = None
            self.initialize_chat()
            print("FitnessAIAssistant initialized successfully.")
        except Exception as e:
            print(f"Error initializing FitnessAIAssistant: {e}")

    def initialize_chat(self):
        """Initialize chat session with Generative AI."""
        try:
            self.chat = self.model.start_chat(history=[])
            self.chat.send_message(self.system_prompt)
            print("Chat initialized with system prompt.")
        except Exception as e:
            print(f"Error during chat initialization: {e}")

    def send_query(self, query: str) -> str:
        """Send a query to the AI model."""
        try:
            if not self.chat:
                self.initialize_chat()
            response = self.chat.send_message(query)
            print(f"AI Response: {response.text}")
            return response.text
        except Exception as e:
            print(f"Error sending query: {e}")
            return "Sorry, there was an error processing your query."


class LoginSignupApp(QWidget):
    def __init__(self, api_key, gemini_api_key):
        """Initialize the application."""
        super().__init__()
        self.fitness_ai = FitnessAIAssistant(gemini_api_key)
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        self.setWindowTitle("Fitness App")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QStackedWidget(self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.central_widget)

        self.init_main_ui()
        self.init_chat_ui()

        self.central_widget.setCurrentIndex(0)

    def init_main_ui(self):
        """Initialize the main UI."""
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)

        label = QLabel("Welcome to the Fitness App!")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        btn_chat = QPushButton("Chat with Assistant")
        btn_chat.clicked.connect(self.show_chat_ui)
        layout.addWidget(btn_chat)

        self.central_widget.addWidget(main_widget)

    def init_chat_ui(self):
        """Initialize the chat UI."""
        chat_widget = QWidget()
        layout = QVBoxLayout(chat_widget)

        self.chat_output = QTextEdit()
        self.chat_output.setReadOnly(True)
        layout.addWidget(self.chat_output)

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your message or press 'Voice'")
        layout.addWidget(self.chat_input)

        btn_send = QPushButton("Send")
        btn_send.clicked.connect(self.handle_text_input)
        layout.addWidget(btn_send)

        btn_voice = QPushButton("Voice")
        btn_voice.clicked.connect(self.handle_voice_input)
        layout.addWidget(btn_voice)

        self.central_widget.addWidget(chat_widget)

    def show_chat_ui(self):
        """Switch to chat UI."""
        self.central_widget.setCurrentIndex(1)

    def handle_text_input(self):
        """Handle text input from the user."""
        user_query = self.chat_input.text().strip()
        if not user_query:
            QMessageBox.warning(self, "Input Error", "Please enter a message.")
            return
        self.chat_output.append(f"You: {user_query}")
        self.chat_input.clear()
        response = self.fitness_ai.send_query(user_query)
        self.chat_output.append(f"Assistant: {response}")

    def handle_voice_input(self):
        """Handle voice input."""
        try:
            with self.microphone as source:
                self.chat_output.append("Listening for your voice...")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source)

            voice_query = self.recognizer.recognize_google(audio)
            self.chat_output.append(f"You (Voice): {voice_query}")
            response = self.fitness_ai.send_query(voice_query)
            self.chat_output.append(f"Assistant: {response}")
        except sr.UnknownValueError:
            self.chat_output.append("Sorry, I didn't catch that. Please try again.")
        except sr.RequestError as e:
            self.chat_output.append(f"Error accessing voice recognition service: {e}")
        except Exception as e:
            self.chat_output.append(f"Error: {e}")


if __name__ == "__main__":
    api_key = "e5968cb05a3b42a4845c016350e83f17"
    gemini_api_key = "AIzaSyA1RJISbzG7WJ0T_ZRQIEVj_WWkhiHKml4"

    app = QApplication(sys.argv)
    window = LoginSignupApp(api_key, gemini_api_key)
    window.show()
    sys.exit(app.exec_())
