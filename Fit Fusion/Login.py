import datetime
import random
import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QStackedWidget, \
    QTabWidget, QSizePolicy, QHBoxLayout, QMessageBox, QTextEdit, QSlider, QComboBox, QDialog, QProgressBar, \
    QScrollArea, QGridLayout, QAction
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QPixmap, QBrush, QPalette, QIcon
import speech_recognition as sr  # Added for voice recognition
import threading
# Backend
import google.generativeai as genai
import requests
from PyQt5.QtGui import QMovie  # For animated GIFs
import time
import playsound  # To play audio cues


import pyttsx3  # For text-to-speech
from gtts import gTTS  # Optional alternative for text-to-speech
import os  # To handle audio playback

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import mplcursors



class BMI:
    def __init__(self):
        self.weight_kg = 0.0
        self.height_m = 0.0
        self.age = 0

    def get_bmi_category(self, bmi):
        if bmi < 18.5:
            return "You are Underweight"
        elif 18.5 <= bmi <= 24.9:
            return "You are Normal weight"
        elif 25.0 <= bmi <= 29.9:
            return "You are Overweight"
        else:
            return "You are Suffering from obesity"

class BMIMetric(BMI):
    def __init__(self, weight_kg, height_cm, age):
        super().__init__()
        self.weight_kg = weight_kg
        self.height_m = height_cm / 100  # Convert height from cm to meters
        self.age = age

    def calculate_bmi(self):
        return self.weight_kg / (self.height_m ** 2)
class MealPlanner:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.spoonacular.com/mealplanner/generate"

        # Initialize Gemini AI
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = self.model.start_chat(history=[])

        self.system_prompt = """
        You are FitFusion AI, a health and nutrition expert. Provide meal plans based on calorie requirements,
        dietary preferences, and health goals. Ensure the meals are diverse, nutritious, and practical.
        """

    def get_meal_plan(self, target_calories, dietary_preferences=None):
        """Fetch a meal plan using Spoonacular or Gemini AI."""
        params = {
            "apiKey": self.api_key,
            "timeFrame": "day",
            "targetCalories": target_calories,
        }

        # Try Spoonacular API first
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Spoonacular API error: {e}")

        # Fall back to Gemini AI if Spoonacular fails
        try:
            user_query = f"Suggest meals for {target_calories} calories. Preferences: {dietary_preferences or 'None'}."
            self.chat.send_message(self.system_prompt)
            ai_response = self.chat.send_message(user_query)
            return {"ai_generated": ai_response.text}
        except Exception as e:
            print(f"Gemini AI error: {e}")
            return None


class FitnessAIAssistant:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.system_prompt = """
        You are FitFusion AI, an expert in fitness, nutrition, and health. Respond concisely to user queries.
        """
        self.chat = None
        self.initialize_chat()

    def initialize_chat(self):
        """Initialize the chat object with the system prompt."""
        try:
            self.chat = self.model.start_chat(history=[])
            self.chat.send_message(self.system_prompt)
        except Exception as e:
            print(f"Error initializing Gemini AI chat: {e}")

    def send_query(self, user_query: str) -> str:
        """Send a query to Gemini AI and return the response."""
        try:
            if not self.chat:
                self.initialize_chat()
            response = self.chat.send_message(user_query)
            return response.text
        except Exception as e:
            print(f"Error communicating with Gemini AI: {str(e)}")
            return "Sorry, I couldn't process your request at the moment."


class WorkoutPlanner:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_exercises(self, muscle=None, name=None, exercise_type=None):
        base_url = 'https://api.api-ninjas.com/v1/exercises'
        params = {}

        # Add query parameters if they are provided
        if muscle:
            params['muscle'] = muscle
        if name:
            params['name'] = name
        if exercise_type:
            params['type'] = exercise_type

        response = requests.get(base_url, headers={'X-Api-Key': self.api_key}, params=params)

        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return []

    def filter_exercises(self, exercises, filter_key, filter_value):
        return [exercise for exercise in exercises if exercise.get(filter_key) == filter_value]

    def format_exercise_details(self, exercises, total_time):
        if not exercises:
            return "No exercises found for the given criteria."

        time_per_exercise = total_time / len(exercises)
        details = "<h3>Workout Plan:</h3>"
        for idx, exercise in enumerate(exercises, start=1):
            details += f"<b>Exercise {idx}:</b> {exercise['name']}<br>"
            details += f"Type: {exercise['type']}<br>"
            details += f"Equipment: {exercise.get('equipment', 'N/A')}<br>"
            details += f"Difficulty: {exercise['difficulty']}<br>"
            details += f"Instructions: {exercise['instructions']}<br>"
            details += f"Allocated Time: {time_per_exercise:.2f} seconds<br><br>"
        return details

class LoginSignupApp(QWidget):
    def __init__(self, api_key,gemini_api_key):
        super().__init__()
        self.PALE_BLUE = "#B0E0E6"
        self.DARK_BLUE = "#0057B7"
        self.VERY_LIGHT_BLUE = "#E0FFFF"
        self.FONT_FAMILY = "'Segoe UI', Arial, sans-serif"

        self.fitness_ai_assistant = FitnessAIAssistant(gemini_api_key)
        self.meal_planner = MealPlanner(api_key)  # Create an instance of MealPlanner

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone(sample_rate=16000, chunk_size=1024)
        self.voice_assistant_active = False
        # Pre-adjust ambient noise once during initialization
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

        self.central_widget = QStackedWidget(self)

        self.setWindowTitle('FitFusion: Fitness Tracker')
        self.setGeometry(100, 100, 800, 600)  # Set window size
        self.central_widget = QStackedWidget(self)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.central_widget)

        # Add back and forward buttons
        self.back_button = QPushButton("Back")
        self.forward_button = QPushButton("Forward")
        self.get_current_user_id()
        # Set button styles
        self.set_back_button_style(self.back_button)
        self.set_forward_button_style(self.forward_button)

        # Connect buttons to their respective functions
        self.back_button.clicked.connect(self.go_back)
        self.forward_button.clicked.connect(self.go_forward)

        # Add buttons to the layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.forward_button)

        self.layout().addLayout(button_layout)

        # Initialize history stack
        self.history = []
        self.current_index = -1
        # Call the initialize_database function at the start of your application
        self.initialize_database()
        self.init_main_ui()
        self.init_login_ui()
        self.init_signup_ui()
        self.init_forgot_password_ui()
        self.init_welcome_ui()

        self.central_widget.setCurrentIndex(0)  # Start with the main UI
        self.add_to_history(0)  # Add main UI to history

    def set_button_style(self, button):
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.PALE_BLUE}; 
                color: {self.DARK_BLUE}; 
                font-size: 18px;
                padding: 10px 20px;
                border: 1px solid {self.DARK_BLUE}; 
                border-radius: 4px;
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            QPushButton:hover {{
                background-color: {self.VERY_LIGHT_BLUE}; 
                transform: scale(1.05);
            }}
        """)

    def set_text_field_style(self, text_field):
        text_field.setStyleSheet(f"""
            font-size: 24px;
            padding: 12px;
            border: 2px solid {self.DARK_BLUE}; 
            border-radius: 5px;
            background-color: {self.VERY_LIGHT_BLUE}; 
        """)

    def set_navigation_button_style(self, button):
        button.setStyleSheet(f"""
            QPushButton {{
                font-size: 18px;
                color: {self.DARK_BLUE}; 
                background: transparent;
                border: none;
            }}
            QPushButton:hover {{
                color: {self.PALE_BLUE}; 
                text-decoration: underline;
            }}
        """)

    def set_cta_button_style(self, button):
        button.setStyleSheet(f"""
            QPushButton {{
                font-size: 20px;
                font-weight: bold;
                color: white;
                background: linear-gradient(90deg, {self.DARK_BLUE}, {self.PALE_BLUE}); 
                padding: 15px 30px;
                border: none;
                border-radius: 25px;
            }}
            QPushButton:hover {{
                background: linear-gradient(90deg, {self.DARK_BLUE}, {self.VERY_LIGHT_BLUE}); 
            }}
        """)

    def set_background_image(self, image_path):
        self.central_widget.setStyleSheet(f"""
            QStackedWidget {{
                border-image: url({image_path}) 0 0 0 0 stretch stretch;
                animation: background-animation 30s linear infinite;
            }}
            @keyframes background-animation {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}
        """)

    def set_back_button_style(self, button):
            button.setStyleSheet("""
                QPushButton {
                    background-color: #B0E0E6;  /* Pale Blue */
                    color: #0057B7;             /* Dark Blue */
                    font-size: 18px;
                    padding: 10px 20px;
                    border: 1px solid #0057B7;  /* Dark Blue Border */
                    border-radius: 4px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                QPushButton:hover {
                    background-color: #E0FFFF;  /* Very Light Blue */
                    transform: scale(1.05);
                }
            """)

    def set_forward_button_style(self, button):
            button.setStyleSheet("""
                QPushButton {
                    background-color: #B0E0E6;  /* Pale Blue */
                    color: #0057B7;             /* Dark Blue */
                    font-size: 18px;
                    padding: 10px 20px;
                    border: 1px solid #0057B7;  /* Dark Blue Border */
                    border-radius: 4px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                QPushButton:hover {
                    background-color: #E0FFFF;  /* Very Light Blue */
                    transform: scale(1.05);
                }
            """)

    def add_to_history(self, index):
        """Add the current index to the history."""
        if self.current_index + 1 < len(self.history):
            self.history = self.history[:self.current_index + 1]

        self.history.append(index)
        self.current_index += 1

    def go_back(self):
        """Navigate to the previous view."""
        if self.current_index > 0:
            self.current_index -= 1
            self.central_widget.setCurrentIndex(self.history[self.current_index])

    def go_forward(self):
        """Navigate to the next view."""
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            self.central_widget.setCurrentIndex(self.history[self.current_index])

    def init_main_ui(self):

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Set background image
        self.set_background_image("full-shot-couple-doing-workout-exercises.jpg")

        # HEADER SECTION
        self.create_header(main_layout)

        # About Us, Features, Contact Sections
        self.create_info_sections(main_layout)

        # CENTERED LOGIN/REGISTER BOX
        self.create_login_register_box(main_layout)

        # Motivational Quote Section
        self.create_quote_section(main_layout)

        self.central_widget.addWidget(main_widget)

    def create_header(self, layout):
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)

        # Logo Section
        logo_label = QLabel("🏋️ FitFusion", self)
        logo_label.setStyleSheet("""
            font-size: 35px;
            font-weight: bold;
            color: #B0E0E6;  /* Pale Blue */
            font-family: 'Segoe UI', Arial, sans-serif;
        """)
        logo_label.setAlignment(Qt.AlignLeft)
        header_layout.addWidget(logo_label)

        additional_logo_label = QLabel(self)
        additional_logo_label.setPixmap(QPixmap("email_logo.png"))  # Replace with actual image path
        additional_logo_label.setScaledContents(True)
        additional_logo_label.setMaximumSize(100, 100)
        header_layout.addWidget(additional_logo_label)

        # Navigation Section
        nav_layout = QHBoxLayout()
        nav_links = {
            "About Us": self.toggle_about_us,
            "Features": self.toggle_features,
            "Contact": self.toggle_contact
        }

        for link, function in nav_links.items():
            nav_button = QPushButton(link, self)
            nav_button.setStyleSheet("""
                QPushButton {
                    background-color: #B0E0E6;  /* Pale Blue */
                    border: 1px solid #0057B7;  /* Dark Blue Border */
                    color: #0057B7;  /* Dark Blue */
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 15px;
                    padding: 10px;
                    border-radius: 5px;
                    margin-left: 10px;
                }
                QPushButton:hover {
                    background-color: #E0FFFF;  /* Very Light Blue */
                }
            """)
            nav_button.setToolTip(f"Learn more about {link}")
            nav_button.clicked.connect(function)
            nav_layout.addWidget(nav_button)

        nav_widget = QWidget()
        nav_widget.setLayout(nav_layout)
        nav_widget.setStyleSheet("""
            QWidget {
                background-color: white;  
                border-radius: 15px;
                padding: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
        """)

        header_layout.addWidget(nav_widget)
        header_layout.addStretch(1)

        layout.addLayout(header_layout)

    def create_info_sections(self, layout):
        self.about_us_section = self.create_info_section(
            "About FitFusion",
            "FitFusion is your personal fitness companion, helping you achieve your goals. "
            "Our mission is to make fitness accessible, enjoyable, and efficient for everyone. "
            "Whether you're a beginner or a pro, FitFusion has something for you."
        )
        layout.addWidget(self.about_us_section)

        self.features_section = self.create_info_section(
            "Features",
            "<ul>"
            "<li><strong>Meal Planning:</strong> Personalized meal plans to meet your nutritional needs.</li>"
            "<li><strong>Fitness Tracking:</strong> Track your workouts, progress, and set goals.</li>"
            "<li><strong>AI-Driven Advice:</strong> Get tailored fitness advice based on your data and preferences.</li>"
            "<li><strong>Community Support:</strong> Join groups, share your progress, and get motivated.</li>"
            "</ul>"
        )
        layout.addWidget(self.features_section)

        self.contact_section = self.create_info_section(
            "Contact Us",
            "Have questions or need support? Reach out to us!<br>"
            "Email: <a href='mailto:contact@fitfusion.com' style='color: #0057B7;'>contact@fitfusion.com</a><br>"
            "Phone: +1-800-123-4567<br>"
            "Follow us on social media for updates and tips:<br>"
            "<a href='https://twitter.com/fitfusion' style='color: #0057B7;'>Twitter</a> | "
            "<a href='https://www.facebook.com/fitfusion' style='color: #0057B7;'>Facebook</a> | "
            "<a href='https://www.instagram.com/fitfusion' style='color: #0057B7;'>Instagram</a>"
        )
        layout.addWidget(self.contact_section)

    def create_info_section(self, title, content):
        section = QWidget()
        layout = QVBoxLayout(section)
        section.setStyleSheet("""
            QWidget {
                background-color: #E0FFFF; 
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                margin-top: 10px;
            }
        """)

        title_label = QLabel(f"<h2 style='color: #0057B7;'>{title}</h2>")  # Use direct color code
        content_label = QLabel(content)
        content_label.setStyleSheet("font-size: 16px; font-family: 'Segoe UI', Arial, sans-serif; color: #333;")
        content_label.setWordWrap(True)  # Enable word wrap to properly display multiline text

        layout.addWidget(title_label)
        layout.addWidget(content_label)
        section.hide()
        return section

    def create_login_register_box(self, layout):
        box_widget = QWidget()
        box_layout = QVBoxLayout(box_widget)
        box_widget.setStyleSheet("""
               QWidget {
                   background-color: white; 
                   border-radius: 15px;
                   padding: 20px;
                   max-width: 400px;
                   margin: 0 auto;
                   box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
               }
           """)

        tagline_label = QLabel("Your Fitness Journey Starts Today!", self)
        tagline_label.setStyleSheet(f"""
               font-size: 20px;
               font-weight: bold;
               color: {self.DARK_BLUE}; 
               font-family: {self.FONT_FAMILY};
               margin-bottom: 15px;
           """)
        tagline_label.setAlignment(Qt.AlignCenter)
        box_layout.addWidget(tagline_label)

        box_layout.addSpacing(10)

        btn_login = QPushButton("Login", self)

        self.set_button_style(btn_login)
        btn_login.setToolTip("Click to login to your account")
        btn_login.clicked.connect(self.switch_to_login)
        box_layout.addWidget(btn_login)

        btn_signup = QPushButton("Sign Up", self)
        self.set_button_style(btn_signup)
        btn_signup.setToolTip("Click to create a new account")
        btn_signup.clicked.connect(self.switch_to_signup)
        box_layout.addWidget(btn_signup)

        layout.addStretch(1)
        layout.addWidget(box_widget, alignment=Qt.AlignCenter)
        layout.addStretch(1)


    def create_quote_section(self, layout):
        quotes = [
            "Believe you can and you're halfway there.",
            "Your limitation—it's only your imagination.",
            "Push yourself, because no one else is going to do it for you.",
            "Great things never come from comfort zones.",
            "Success doesn’t just find you. You have to go out and get it."
        ]
        random_quote = random.choice(quotes)
        quote_box_widget = QWidget()
        quote_box_layout = QVBoxLayout(quote_box_widget)
        quote_box_widget.setStyleSheet("""
                   QWidget {
                       background-color: white; 
                       border-radius: 15px;
                       padding: 20px;
                       max-width: 400px;
                       margin: 0 auto;
                       box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                   }
               """)

        quote_label = QLabel(f"\"{random_quote}\"", self)
        quote_label.setStyleSheet("""
                   font-size: 18px;
                   font-weight: bold;
                   color: #333;
                   font-family: 'Segoe UI', Arial, sans-serif;
                   text-align: center;
               """)
        quote_box_layout.addWidget(quote_label)

        layout.addWidget(quote_box_widget, alignment=Qt.AlignCenter)


    def toggle_about_us(self):
        self.features_section.hide()
        self.contact_section.hide()
        self.about_us_section.setVisible(not self.about_us_section.isVisible())


    def toggle_features(self):
        self.about_us_section.hide()
        self.contact_section.hide()
        self.features_section.setVisible(not self.features_section.isVisible())


    def toggle_contact(self):
        self.about_us_section.hide()
        self.features_section.hide()
        self.contact_section.setVisible(not self.contact_section.isVisible())



    def switch_to_login(self):
        self.central_widget.setCurrentIndex(1)  # Switch to login
        self.add_to_history(1)  # Add login UI to history

    def switch_to_signup(self):
        self.central_widget.setCurrentIndex(2)  # Switch to signup
        self.add_to_history(2)  # Add signup UI to history

    def init_login_ui(self):
        """Login UI with enhanced interaction"""
        login_widget = QWidget()
        layout = QVBoxLayout(login_widget)

        # Login Box
        box_widget = QWidget()
        box_layout = QVBoxLayout(box_widget)
        box_widget.setStyleSheet("""
            QWidget {
                background-color: #E0FFFF;  /* Very Light Blue */
                border-radius: 15px;
                padding: 30px;  /* Increased padding for better spacing */
                max-width: 600px;  /* Increased width for a larger box */
                margin: 20px auto;  /* Increased margin for better positioning */
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
        """)

        # Login Form UI with Custom Styling
        email_label = QLabel("Email: ", self)
        email_label.setStyleSheet("font-size: 30px; color: #0057B7; font-weight: bold;")  # Dark Blue
        box_layout.addWidget(email_label)

        self.login_email = QLineEdit(self)
        self.set_text_field_style(self.login_email)
        self.login_email.setPlaceholderText("Enter your email")
        box_layout.addWidget(self.login_email)

        password_label = QLabel("Password: ", self)
        password_label.setStyleSheet("font-size: 30px; color: #0057B7; font-weight: bold;")  # Dark Blue
        box_layout.addWidget(password_label)

        self.login_password = QLineEdit(self)
        self.set_text_field_style(self.login_password)
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setPlaceholderText("Enter your password")
        box_layout.addWidget(self.login_password)

        # Login button with animation and feedback
        btn_login = QPushButton("Login", self)
        self.set_button_style(btn_login)
        btn_login.setStyleSheet(btn_login.styleSheet() + "font-size: 25px; margin-top: 20px; font-weight: bold;")
        btn_login.clicked.connect(self.on_login_button_click)
        box_layout.addWidget(btn_login)

        # Feedback label
        self.login_feedback = QLabel("", self)
        self.login_feedback.setStyleSheet("font-size: 25px; color: #0057B7;")  # Dark Blue
        box_layout.addWidget(self.login_feedback)

        # Forgot Password Button
        btn_forgot_password = QPushButton("Forgot Password?", self)
        self.set_button_style(btn_forgot_password)
        btn_forgot_password.clicked.connect(self.open_forgot_password_window)
        box_layout.addWidget(btn_forgot_password)

        layout.addStretch(1)
        layout.addWidget(box_widget, alignment=Qt.AlignCenter)
        layout.addStretch(1)

        self.central_widget.addWidget(login_widget)

    def on_login_button_click(self):
        """Triggered when the login button is clicked."""
        email = self.login_email.text().strip()
        password = self.login_password.text().strip()

        if not email:
            self.login_feedback.setText("Please enter your email.")
            return
        if not password:
            self.login_feedback.setText("Please enter your password.")
            return

        self.login_feedback.setText("")  # Clear previous feedback
        self.login_database()

    def login_database(self):
        """Check credentials in the database for login"""
        email = self.login_email.text().strip()
        password = self.login_password.text().strip()

        try:
            conn = sqlite3.connect("1.db")
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM test WHERE email=? AND password=?", (email, password))
            row = cur.fetchone()  # Fetch a single record
        except sqlite3.Error as e:
            self.login_feedback.setStyleSheet("font-size: 25px; color: red;")
            self.login_feedback.setText(f"Database error: {e}")
            return
        finally:
            conn.close()  # Ensure the connection is closed

        if row:
            user_id, user_name = row  # Retrieve ID and name
            self.current_user_id = user_id  # Store the user ID in an instance attribute
            self.login_feedback.setStyleSheet("font-size: 25px; color: white;")
            self.login_feedback.setText(f"Login successful. Welcome {user_name}!")
            self.show_welcome_frame(user_name)  # Show welcome frame upon successful login
        else:
            self.login_feedback.setStyleSheet("font-size: 25px; color: white;")
            self.login_feedback.setText("No such user found. Please sign up or check your credentials.")

    def open_forgot_password_window(self, event):
        """Open the forgot password dialog"""
        self.central_widget.setCurrentIndex(3)  # Switch to forgot password UI
        self.add_to_history(3)  # Add forgot password UI to history

    def init_forgot_password_ui(self):
        """Forgot Password UI"""
        forgot_widget = QWidget()
        layout = QVBoxLayout(forgot_widget)

        # Forgot Password Box
        box_widget = QWidget()
        box_layout = QVBoxLayout(box_widget)
        box_widget.setStyleSheet("""
            QWidget {
                background-color: #E0FFFF;  /* Very Light Blue */
                border-radius: 15px;
                padding: 20px;
                max-width: 400px;
                margin: 0 auto;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
        """)

        # Label and input for email
        email_label = QLabel("Enter your registered email:", self)
        email_label.setStyleSheet("font-size: 25px; color: #0057B7; font-weight: bold;")  # Dark Blue
        box_layout.addWidget(email_label)

        self.forgot_email = QLineEdit(self)
        self.set_text_field_style(self.forgot_email)
        self.forgot_email.setPlaceholderText("Enter your email")
        box_layout.addWidget(self.forgot_email)

        # Submit button for password reset
        btn_reset = QPushButton("Reset Password", self)
        self.set_button_style(btn_reset)
        btn_reset.setStyleSheet(btn_reset.styleSheet() + "font-size: 25px; margin-top: 20px; font-weight: bold;")
        btn_reset.clicked.connect(self.reset_password)
        box_layout.addWidget(btn_reset)

        # Feedback label
        self.forgot_password_feedback = QLabel("", self)
        self.forgot_password_feedback.setStyleSheet("font-size: 25px; color: #0057B7;")  # Dark Blue
        box_layout.addWidget(self.forgot_password_feedback)

        layout.addStretch(1)
        layout.addWidget(box_widget, alignment=Qt.AlignCenter)
        layout.addStretch(1)

        self.central_widget.addWidget(forgot_widget)

    def reset_password(self):
        """Simulate password reset process (for now just a placeholder)"""
        email = self.forgot_email.text().strip()

        if not email:
            self.forgot_password_feedback.setText("Please enter your email.")
            return

        # Here you would typically send the email for password reset
        # For now, we will simulate this with a message
        self.forgot_password_feedback.setText(
            "Password reset instructions sent")
        # Do not switch back to the main UI; stay on the forgot password screen

    def init_login_ui(self):
        login_widget = QWidget()
        layout = QVBoxLayout(login_widget)

        # Login Box
        box_widget = QWidget()
        box_layout = QVBoxLayout(box_widget)
        box_widget.setStyleSheet("""
            QWidget {
                background-color: #E0FFFF; /* Very Light Blue */
                border-radius: 15px;
                padding: 20px;
                max-width: 400px;
                margin: 0 auto;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
        """)

        # Login Form UI with Custom Styling
        email_label = QLabel("Email: ", self)
        email_label.setStyleSheet("font-size: 30px; color: #0057B7; font-weight: bold;")  # Dark Blue
        box_layout.addWidget(email_label)

        self.login_email = QLineEdit(self)
        self.set_text_field_style(self.login_email)
        self.login_email.setPlaceholderText("Enter your email")
        box_layout.addWidget(self.login_email)

        password_label = QLabel("Password: ", self)
        password_label.setStyleSheet("font-size: 30px; color: #0057B7; font-weight: bold;")  # Dark Blue
        box_layout.addWidget(password_label)

        self.login_password = QLineEdit(self)
        self.set_text_field_style(self.login_password)
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setPlaceholderText("Enter your password")
        box_layout.addWidget(self.login_password)

        # Login button with animation and feedback
        btn_login = QPushButton("Login", self)
        self.set_button_style(btn_login)
        btn_login.setStyleSheet(btn_login.styleSheet() + "font-size: 25px; margin-top: 20px; font-weight: bold;")
        btn_login.clicked.connect(self.on_login_button_click)
        box_layout.addWidget(btn_login)

        # Feedback label
        self.login_feedback = QLabel("", self)
        self.login_feedback.setStyleSheet("font-size: 25px; color: #0057B7;")  # Dark Blue
        box_layout.addWidget(self.login_feedback)

        # Forgot Password Button
        btn_forgot_password = QPushButton("Forgot Password?", self)
        self.set_button_style(btn_forgot_password)
        btn_forgot_password.clicked.connect(self.open_forgot_password_window)
        box_layout.addWidget(btn_forgot_password)

        layout.addStretch(1)
        layout.addWidget(box_widget, alignment=Qt.AlignCenter)
        layout.addStretch(1)

        self.central_widget.addWidget(login_widget)
    def initialize_database(self):
        """Ensure the database schema is up to date"""
        conn = sqlite3.connect("1.db")
        cur = conn.cursor()

        # Check the schema of the 'streaks' table
        cur.execute("PRAGMA table_info(streaks)")
        schema_info = cur.fetchall()
        print("Current schema of streaks table:")
        for column in schema_info:
            print(column)

        def column_exists(table, column):
            cur.execute(f"PRAGMA table_info({table})")
            return any(row[1] == column for row in cur.fetchall())

        # Ensure the 'streak_count' column exists
        if not column_exists('streaks', 'streak_count'):
            print("Adding column: streak_count")
            cur.execute("ALTER TABLE streaks ADD COLUMN streak_count INTEGER DEFAULT 0")

        # Ensure the 'current_streak' column exists
        if not column_exists('streaks', 'current_streak'):
            print("Adding column: current_streak")
            cur.execute("ALTER TABLE streaks ADD COLUMN current_streak INTEGER DEFAULT 0")

        # Ensure the 'longest_streak' column exists
        if not column_exists('streaks', 'longest_streak'):
            print("Adding column: longest_streak")
            cur.execute("ALTER TABLE streaks ADD COLUMN longest_streak INTEGER DEFAULT 0")

        conn.commit()
        conn.close()

    def init_signup_ui(self):
        # Signup UI
        signup_widget = QWidget()
        layout = QVBoxLayout(signup_widget)
        layout.setAlignment(Qt.AlignCenter)

        # Main Signup Box
        box_widget = QWidget()
        box_layout = QVBoxLayout(box_widget)
        box_widget.setStyleSheet("""
            QWidget {
                background-color: white;  /* Background color */
                border-radius: 20px;
                padding: 40px;
                max-width: 800px;  /* Increased width for better fitting elements */
                margin: 30px auto;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            }
        """)

        # Header
        header_label = QLabel("Create Your Account", self)
        header_label.setStyleSheet("font-size: 36px; color: #0057B7; font-weight: bold; margin-bottom: 20px;")
        header_label.setAlignment(Qt.AlignCenter)
        box_layout.addWidget(header_label)

        # User Name Box
        user_name_box = QWidget()
        user_name_layout = QVBoxLayout(user_name_box)
        user_name_box.setStyleSheet("""
            QWidget {
                background-color: #E0FFFF;  /* Very Light Blue */
                border-radius: 10px;
                padding: 10px;
                margin-bottom: 15px;  /* Spacing between boxes */
            }
        """)
        self.signup_name = self.create_labeled_input(user_name_layout, "User Name:", "Enter your name", "profile_6915911.png")

        box_layout.addWidget(user_name_box)

        # User Email Box
        user_email_box = QWidget()
        user_email_layout = QVBoxLayout(user_email_box)
        user_email_box.setStyleSheet("""
            QWidget {
                background-color: #E0FFFF;  /* Very Light Blue */
                border-radius: 10px;
                padding: 10px;
                margin-bottom: 15px;  /* Spacing between boxes */
            }
        """)
        self.signup_email = self.create_labeled_input(user_email_layout, "User Email:", "Enter your email", "email_552486.png")

        box_layout.addWidget(user_email_box)

        # Password Box
        password_box = QWidget()
        password_layout = QVBoxLayout(password_box)
        password_box.setStyleSheet("""
            QWidget {
                background-color: #E0FFFF;  /* Very Light Blue */
                border-radius: 10px;
                padding: 10px;
                margin-bottom: 15px;  /* Spacing between boxes */
            }
        """)
        self.signup_password = self.create_labeled_input(password_layout, "Password:", "Enter your password",
                                                         "lock_17777135.png", is_password=True)

        box_layout.addWidget(password_box)
        '''        # Confirm Password Box
        confirm_password_box = QWidget()
        confirm_password_layout = QVBoxLayout(confirm_password_box)
        confirm_password_box.setStyleSheet("""
            QWidget {
                background-color: #E0FFFF;  /* Very Light Blue */
                border-radius: 10px;
                padding: 10px;
                margin-bottom: 15px;  /* Spacing between boxes */
            }
        """)
        self.create_labeled_input(confirm_password_layout, "Confirm Password:", "Re-enter your password",
                                  "lock_17777135.png", is_password=True)
        box_layout.addWidget(confirm_password_box)
        '''

        # Feedback label
        self.signup_feedback = QLabel("", self)
        self.signup_feedback.setStyleSheet("font-size: 20px; color: #FF0000; margin-top: 15px;")  # Red for feedback
        self.signup_feedback.setAlignment(Qt.AlignCenter)
        box_layout.addWidget(self.signup_feedback)

        # Sign up button
        btn_signup = QPushButton("Signup", self)
        self.set_button_style(btn_signup)
        btn_signup.setStyleSheet(btn_signup.styleSheet() + """
            font-size: 25px; 
            margin-top: 20px; 
            font-weight: bold;
            min-width: 150px;  /* Minimum width */
            min-height: 40px;  /* Minimum height */
        """)
        btn_signup.clicked.connect(self.signup_database)
        box_layout.addWidget(btn_signup)

        # Footer with Terms and Conditions
        footer_label = QLabel("By signing up, you agree to our Terms and Conditions.", self)
        footer_label.setStyleSheet("font-size: 14px; color: #808080; margin-top: 20px;")
        footer_label.setAlignment(Qt.AlignCenter)
        box_layout.addWidget(footer_label)

        layout.addWidget(box_widget)
        self.central_widget.addWidget(signup_widget)

    def create_labeled_input(self, layout, label_text, placeholder_text, logo_path, is_password=False):
        """Helper method to create labeled input fields with logo placeholders."""
        container_widget = QWidget()
        container_layout = QHBoxLayout(container_widget)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(10)

        label = QLabel(label_text, self)
        label.setStyleSheet("font-size: 24px; color: #0057B7; font-weight: bold; margin-right: 10px;")
        container_layout.addWidget(label)

        input_field = QLineEdit(self)
        self.set_text_field_style(input_field)
        input_field.setPlaceholderText(placeholder_text)
        input_field.setFixedHeight(50)
        input_field.setStyleSheet("""
            QLineEdit {
                font-size: 18px;
                padding-left: 40px;
            }
            QLineEdit::placeholder {
                font-size: 18px;
                color: #999;
            }
        """)

        # Add logo
        icon_pixmap = QPixmap(logo_path).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        action = QAction(self)
        action.setIcon(QIcon(icon_pixmap))
        input_field.addAction(action, QLineEdit.LeadingPosition)

        if is_password:
            input_field.setEchoMode(QLineEdit.Password)

        container_layout.addWidget(input_field)
        layout.addWidget(container_widget)
        return input_field

    def signup_database(self):
        """Handle database actions for signup"""
        name = self.signup_name.text().strip()
        email = self.signup_email.text().strip()
        password = self.signup_password.text().strip()

        # Validate that all fields are filled
        if not name or not email or not password:
            self.signup_feedback.setText("Please fill in all fields.")
            return

        try:
            conn = sqlite3.connect("1.db")
            cur = conn.cursor()

            # Ensure the 'test' table exists for users (if not, it gets created)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS test (
                    id INTEGER PRIMARY KEY, 
                    name TEXT, 
                    email TEXT, 
                    password TEXT
                )
            """)

            # Check if the user already exists by email
            cur.execute("SELECT id FROM test WHERE email = ?", (email,))
            existing_user = cur.fetchone()
            if existing_user:
                self.signup_feedback.setText("Account already exists with this email.")
                return  # If user exists, stop further processing

            # Add the new user to the 'test' table
            cur.execute("INSERT INTO test (name, email, password) VALUES (?, ?, ?)", (name, email, password))

            # Get the user ID of the newly inserted user
            user_id = cur.lastrowid

            # Check if the 'streaks' table exists, and create it if it doesn't
            cur.execute("""
                CREATE TABLE IF NOT EXISTS streaks (
                    user_id INTEGER PRIMARY KEY,
                    last_active_date TEXT,
                    streak_count INTEGER,
                    current_streak INTEGER,
                    longest_streak INTEGER,
                    FOREIGN KEY(user_id) REFERENCES test(id)
                )
            """)

            # Function to check if a column exists in the streaks table
            def column_exists(table, column):
                cur.execute(f"PRAGMA table_info({table})")
                return any(row[1] == column for row in cur.fetchall())

            # Ensure the required columns exist in the 'streaks' table (add if missing)
            if not column_exists('streaks', 'last_active_date'):
                cur.execute("ALTER TABLE streaks ADD COLUMN last_active_date TEXT")
            if not column_exists('streaks', 'current_streak'):
                cur.execute("ALTER TABLE streaks ADD COLUMN current_streak INTEGER DEFAULT 0")
            if not column_exists('streaks', 'longest_streak'):
                cur.execute("ALTER TABLE streaks ADD COLUMN longest_streak INTEGER DEFAULT 0")

            # Initialize the streak for the new user
            cur.execute("""
                INSERT INTO streaks (user_id, last_active_date, streak_count, current_streak, longest_streak)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, datetime.datetime.today().date().isoformat(), 0, 0, 0))

            conn.commit()

            # Provide feedback that the account was created successfully
            self.signup_feedback.setText("Account created successfully!")
            self.signup_name.clear()
            self.signup_email.clear()
            self.signup_password.clear()
            self.central_widget.setCurrentIndex(0)  # Go back to the main UI
            self.add_to_history(0)  # Add main UI to history

        except sqlite3.Error as e:
            # In case of an error with the database, show the error message
            self.signup_feedback.setText(f"Database error: {e}")
        finally:
            conn.close()

    def init_welcome_ui(self):
        """Show a welcome frame after successful login"""
        welcome_widget = QWidget()
        layout = QVBoxLayout(welcome_widget)

        # Welcome message with custom style
        self.welcome_msg = QLabel("", self)
        self.welcome_msg.setStyleSheet("font-size: 40px; font-weight: bold; color: #333333;")
        self.welcome_msg.setAlignment(Qt.AlignCenter)  # Centering the label
        layout.addWidget(self.welcome_msg)

        # Logout button with modern style
        btn_logout = QPushButton("Logout", self)
        self.set_button_style(btn_logout)
        btn_logout.setStyleSheet(btn_logout.styleSheet() + "font-size: 25px; margin-top: 20px;")
        btn_logout.clicked.connect(self.logout)
        layout.addWidget(btn_logout)

        self.central_widget.addWidget(welcome_widget)

    def show_welcome_frame(self, user_name):
        """Show welcome message and initialize tabs after successful login"""
        self.central_widget.setCurrentIndex(5)  # Switch to a new index for tabs
        self.init_tabs(user_name)  # Initialize tabs
        self.add_to_history(5)  # Add tabs UI to history

    def init_tabs(self, user_name):
        """Initialize the tabbed interface after login"""
        tabs_widget = QWidget()
        tabs_layout = QVBoxLayout(tabs_widget)

        # Create QTabWidget
        self.tabs = QTabWidget()

        # Apply the updated style sheet for colorful and fitting tab buttons
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                background-color: #E1BEE7;  /* Light purple background */
                color: black;               /* Black text for contrast */
                font-size: 14px;            /* Font size */
                padding: 10px 25px;         /* Ensure proper padding for better visibility */
                border: 1px solid #ccc;     /* Border around tabs */
                border-bottom: none;        /* Smooth look */
                border-radius: 4px;         /* Rounded corners */
                min-width: 100px;           /* Minimum width to prevent truncation */
            }

            QTabBar::tab:selected {
                background-color: #D81B60;  /* Darker purple for selected tab */
                font-weight: bold;          /* Bold text for selected tab */
            }

            QTabBar::tab:hover {
                background-color: #D5006D;  /* Lighter purple on hover */
            }

            QTabWidget::pane {
                border: 1px solid #ccc;     /* Border around tab content */
                border-top: none;           /* Merge content with tabs */
            }
        """)

        # Allow tabs to expand with window size
        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Add the QTabWidget to the layout
        tabs_layout.addWidget(self.tabs)

        # Create tabs
        self.create_workout_planner_tab()
        self.create_streak_tab()
        self.create_bmi_visualization_tab()
        self.create_meal_planner_tab()
        self.create_interactive_assistant_tab()
        self.create_help_tab()

        # Set the tabs widget as the central widget
        self.central_widget.addWidget(tabs_widget)
        self.central_widget.setCurrentWidget(tabs_widget)  # Show the tabs widget

        # Use stretch to ensure resizing affects tab size properly
        tabs_layout.setStretch(0, 1)  # Allow the tab widget to stretch

    def create_workout_planner_tab(self):
        workout_tab = QWidget()
        layout = QVBoxLayout(workout_tab)

        # Title with updated label color closer to the theme
        label = QLabel("Workout Planner", self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
            color: #D81B60;  /* Soft pink for the label text */
            background-color: #F3E5F5;  /* Very light lavender for the background */
            padding: 10px;
        """)
        layout.addWidget(label)

        # Muscle Group Label
        muscle_group_label = QLabel("Muscle Group:", self)
        muscle_group_label.setStyleSheet("font-size: 16px; color: white;")
        layout.addWidget(muscle_group_label)

        # Muscle Group ComboBox
        self.muscle_group_combo = QComboBox(self)
        self.muscle_group_combo.addItems([
            "","Abdominals", "Abductors", "Adductors", "Biceps", "Calves",
            "Chest", "Forearms", "Glutes", "Hamstrings", "Lats", "Lower Back",
            "Middle Back", "Neck", "Quadriceps", "Traps", "Triceps"
        ])
        self.muscle_group_combo.setStyleSheet("""
            background-color: #f0f0f0;
            font-size: 16px;
            padding: 5px;
            border: 2px solid #E1BEE7;  /* Light purple border */
            border-radius: 5px;
        """)
        layout.addWidget(self.muscle_group_combo)

        # Exercise Name Label
        exercise_name_label = QLabel("Exercise Name:", self)
        exercise_name_label.setStyleSheet("font-size: 16px; color: white;")
        layout.addWidget(exercise_name_label)

        # Exercise Name Input
        self.exercise_name_input = QLineEdit(self)
        self.exercise_name_input.setPlaceholderText("Partial Exercise Name (e.g., press, squat)")
        self.exercise_name_input.setStyleSheet("""
            background-color: #f0f0f0;
            font-size: 16px;
            padding: 5px;
            border: 2px solid #E1BEE7;  /* Light purple border */
            border-radius: 5px;
        """)
        layout.addWidget(self.exercise_name_input)

        # Exercise Type Label
        exercise_type_label = QLabel("Exercise Type:", self)
        exercise_type_label.setStyleSheet("font-size: 16px; color: white;")
        layout.addWidget(exercise_type_label)

        # Exercise Type ComboBox
        self.exercise_type_combo = QComboBox(self)
        self.exercise_type_combo.addItems([
          "","Cardio", "Olympic Weightlifting", "Plyometrics", "Powerlifting",
            "Strength", "Stretching", "Strongman"
        ])
        self.exercise_type_combo.setStyleSheet("""
            background-color: #f0f0f0;
            font-size: 16px;
            padding: 5px;
            border: 2px solid #E1BEE7;  /* Light purple border */
            border-radius: 5px;
        """)
        layout.addWidget(self.exercise_type_combo)

        # Difficulty Label
        difficulty_label = QLabel("Difficulty Level:", self)
        difficulty_label.setStyleSheet("font-size: 16px; color: white;")
        layout.addWidget(difficulty_label)

        # Difficulty ComboBox
        self.difficulty_combo = QComboBox(self)
        self.difficulty_combo.addItems(["","Beginner", "Intermediate", "Expert"])
        self.difficulty_combo.setStyleSheet("""
            background-color: #f0f0f0;
            font-size: 16px;
            padding: 5px;
            border: 2px solid #E1BEE7;  /* Light purple border */
            border-radius: 5px;
        """)
        layout.addWidget(self.difficulty_combo)

        # Duration Label
        duration_label = QLabel("Workout Duration (minutes):", self)
        duration_label.setStyleSheet("font-size: 16px; color: white;")
        layout.addWidget(duration_label)

        # Duration Input
        self.workout_duration_input = QLineEdit(self)
        self.workout_duration_input.setPlaceholderText("Workout Duration (minutes, e.g., 45)")
        self.workout_duration_input.setStyleSheet("""
            background-color: #f0f0f0;
            font-size: 16px;
            padding: 5px;
            border: 2px solid #E1BEE7;  /* Light purple border */
            border-radius: 5px;
        """)
        layout.addWidget(self.workout_duration_input)

        # Generate Button
        generate_button = QPushButton("Generate Workout Plan", self)
        generate_button.setStyleSheet("""
            QPushButton {
                background-color: #E1BEE7;  /* Light purple background */
                color: black;               /* Black text for contrast */
                font-size: 18px;            /* Increased font size */
                padding: 10px 20px;         /* Padding for better visibility */
                border: 1px solid #ccc;     /* Border around buttons */
                border-radius: 4px;         /* Rounded corners */
                cursor: pointer;           /* Change cursor to pointer */
            }
            QPushButton:hover {
                background-color: #D5006D;  /* Darker purple on hover */
            }
        """)
        generate_button.clicked.connect(self.generate_workout_plan)
        layout.addWidget(generate_button)

        # Output Area
        self.workout_plan_output = QTextEdit(self)
        self.workout_plan_output.setReadOnly(True)
        self.workout_plan_output.setStyleSheet("""
            background-color: #f9f9f9;
            font-size: 16px;
            padding: 10px;
            border: 2px solid #E1BEE7;  /* Light purple border */
            border-radius: 5px;
            color: #333;
        """)
        layout.addWidget(self.workout_plan_output)

        # Add tab
        self.tabs.addTab(workout_tab, "Workouts")

    def generate_workout_plan(self):
        muscle_group = self.muscle_group_combo.currentText()
        exercise_name = self.exercise_name_input.text().strip()
        exercise_type = self.exercise_type_combo.currentText()
        difficulty = self.difficulty_combo.currentText()

        try:
            total_time = float(self.workout_duration_input.text().strip())
        except ValueError:
            self.workout_plan_output.setPlainText("Please enter a valid number for duration.")
            return

        if not muscle_group and not exercise_name and not exercise_type:
            self.workout_plan_output.setPlainText("Please specify at least one filter.")
            return

        # Fetch exercises using the API
        planner = WorkoutPlanner(api_key="1c55tgO/oZW1c40Dtz+PxQ==hGupNoi6khvXO6Xv")
        exercises = planner.get_exercises(muscle=muscle_group, name=exercise_name, exercise_type=exercise_type)

        if difficulty:
            exercises = planner.filter_exercises(exercises, 'difficulty', difficulty)

        # Format and display the workout plan
        formatted_plan = planner.format_exercise_details(exercises, total_time)
        self.workout_plan_output.setHtml(formatted_plan)

    def create_streak_tab(self):
        """Create the Streak Tab UI with enhanced visual design and functionality."""
        streak_tab = QWidget()
        layout = QVBoxLayout(streak_tab)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title label for Streak Tracker
        title_label = QLabel("Streak Tracker")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
            color: #D81B60;  /* Soft pink for the label text */
            background-color: #F3E5F5;  /* Very light lavender for the background */
            padding: 10px;
        """)
        layout.addWidget(title_label)

        # Sub-heading label for current streak status
        current_status_label = QLabel("Track your streaks and progress!")
        current_status_label.setAlignment(Qt.AlignCenter)
        current_status_label.setStyleSheet("""
            font-size: 20px;
            color: white;
            margin-bottom: 20px;
        """)
        layout.addWidget(current_status_label)

        # Display streak statistics
        stats_layout = QHBoxLayout()

        # Current Streak
        self.current_streak_label = QLabel("Current Streak: 0 Days")
        self.current_streak_label.setAlignment(Qt.AlignCenter)
        self.current_streak_label.setStyleSheet("""
            font-size: 18px;
            color: white;
            background-color: #4CAF50; /* Green */
            padding: 10px;
            border-radius: 5px;
        """)
        stats_layout.addWidget(self.current_streak_label)

        # Longest Streak
        self.longest_streak_label = QLabel("Longest Streak: 0 Days")
        self.longest_streak_label.setAlignment(Qt.AlignCenter)
        self.longest_streak_label.setStyleSheet("""
            font-size: 18px;
            color: white;
            background-color: #FF5733; /* Red */
            padding: 10px;
            border-radius: 5px;
        """)
        stats_layout.addWidget(self.longest_streak_label)

        layout.addLayout(stats_layout)

        # Streak Progress Bar
        self.streak_progress_bar = QProgressBar()
        self.streak_progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #FFFFFF;
                border-radius: 5px;
                background: #333333;
                text-align: center;
                font-size: 16px;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #FFD700; /* Golden color */
                width: 20px;
            }
        """)
        self.streak_progress_bar.setMaximum(7)  # Assuming streaks reset after 7 days
        self.streak_progress_bar.setValue(0)
        layout.addWidget(self.streak_progress_bar)

        # Display streak progress in detail
        self.streak_progress_label = QLabel("Your current streak progress: 0/7 days")
        self.streak_progress_label.setAlignment(Qt.AlignCenter)
        self.streak_progress_label.setStyleSheet("""
            font-size: 16px;
            color: white;
            margin-top: 10px;
        """)
        layout.addWidget(self.streak_progress_label)

        # Add the streak tab to the main tab widget
        self.tabs.addTab(streak_tab, "Streak")

        # Ensure the tab switch signal is connected only once
        if not hasattr(self, '_streak_signal_connected'):
            self.tabs.currentChanged.connect(self.update_streak_progress)
            self._streak_signal_connected = True  # Prevent re-connecting the signal

    def update_streak_progress(self):
        """Update the streak progress display in the Streak tab."""
        if self.tabs.tabText(self.tabs.currentIndex()) != "Streak":
            return  # Not the streak tab, ignore

        user_id = self.get_current_user_id()
        if not user_id:
            self.streak_progress_label.setText("No user logged in.")
            return

        try:
            conn = sqlite3.connect("1.db")
            cur = conn.cursor()

            # Ensure streaks table exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS streaks (
                    user_id TEXT PRIMARY KEY,
                    last_active_date TEXT,
                    streak_count INTEGER,
                    current_streak INTEGER,
                    longest_streak INTEGER
                )
            """)

            # Fetch streak data for the current user
            today = datetime.datetime.today().date().isoformat()
            cur.execute(
                "SELECT last_active_date, streak_count, current_streak, longest_streak FROM streaks WHERE user_id = ?",
                (user_id,))
            result = cur.fetchone()

            if result:
                _, streak_count, current_streak, longest_streak = result
                self.streak_progress_label.setText(
                    f"Total Streak: {streak_count} days\n"
                    f"Current Streak: {current_streak} days\n"
                    f"Longest Streak: {longest_streak} days"
                )
            else:
                # Handle first-time login for a user
                cur.execute("""
                    INSERT INTO streaks (user_id, last_active_date, streak_count, current_streak, longest_streak)
                    VALUES (?, ?, 1, 1, 1)
                """, (user_id, today))
                conn.commit()
                self.streak_progress_label.setText(
                    "Total Streak: 1 day\nCurrent Streak: 1 day\nLongest Streak: 1 day"
                )
        except sqlite3.Error as e:
            self.streak_progress_label.setText(f"Error fetching streak data: {e}")
        finally:
            conn.close()

    def update_streak(self, user_id):
        """Update the streak for the user."""
        conn = sqlite3.connect("1.db")
        cur = conn.cursor()

        today = datetime.datetime.today().date().isoformat()
        try:
            cur.execute(
                "SELECT last_active_date, streak_count, current_streak, longest_streak FROM streaks WHERE user_id = ?",
                (user_id,))
            result = cur.fetchone()

            if result:
                last_active_date, streak_count, current_streak, longest_streak = result
                if last_active_date == today:
                    return  # No update needed
                elif last_active_date == (datetime.datetime.today() - datetime.timedelta(days=1)).date().isoformat():
                    streak_count += 1
                    current_streak += 1
                else:
                    streak_count = 1
                    current_streak = 1

                if current_streak > longest_streak:
                    longest_streak = current_streak

                cur.execute("""
                    UPDATE streaks
                    SET last_active_date = ?, streak_count = ?, current_streak = ?, longest_streak = ?
                    WHERE user_id = ?
                """, (today, streak_count, current_streak, longest_streak, user_id))
            else:
                cur.execute("""
                    INSERT INTO streaks (user_id, last_active_date, streak_count, current_streak, longest_streak)
                    VALUES (?, ?, 1, 1, 1)
                """, (user_id, today))

            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error while updating streak: {e}")
        finally:
            conn.close()

    def get_current_user_id(self):
        user_id = getattr(self, 'current_user_id', None)
        print(f"get_current_user_id() returned: {user_id}")
        return user_id

    def create_bmi_visualization_tab(self):
        bmi_tab = QWidget()
        layout = QVBoxLayout(bmi_tab)

        label = QLabel("BMI Visualization", self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
            color: #D81B60;  /* Soft pink for the label text */
            background-color: #F3E5F5;  /* Very light lavender for the background */
            padding: 10px;
        """)
        layout.addWidget(label)

        self.weight_input = QLineEdit(self)
        self.weight_input.setPlaceholderText("Weight (kg)")
        self.weight_input.setStyleSheet("""
            font-size: 16px;           /* Smaller font size */
            padding: 5px;              /* Reduced padding */
            height: 25px;              /* Smaller height */
            border: 1px solid #ccc;    /* Border */
            border-radius: 5px;        /* Rounded corners */
            margin-bottom: 5px;        /* Reduced margin for spacing */
        """)
        layout.addWidget(self.weight_input)

        self.height_input = QLineEdit(self)
        self.height_input.setPlaceholderText("Height (cm)")
        self.height_input.setStyleSheet("""
            font-size: 16px;           /* Smaller font size */
            padding: 5px;              /* Reduced padding */
            height: 25px;              /* Smaller height */
            border: 1px solid #ccc;    /* Border */
            border-radius: 5px;        /* Rounded corners */
            margin-bottom: 5px;        /* Reduced margin for spacing */
        """)
        layout.addWidget(self.height_input)

        self.age_input = QLineEdit(self)
        self.age_input.setPlaceholderText("Age")
        self.age_input.setStyleSheet("""
            font-size: 16px;           /* Smaller font size */
            padding: 5px;              /* Reduced padding */
            height: 25px;              /* Smaller height */
            border: 1px solid #ccc;    /* Border */
            border-radius: 5px;        /* Rounded corners */
            margin-bottom: 5px;        /* Reduced margin for spacing */
        """)
        layout.addWidget(self.age_input)

        calculate_button = QPushButton("Calculate BMI", self)
        self.set_button_style(calculate_button)
        calculate_button.clicked.connect(self.calculate_bmi)
        layout.addWidget(calculate_button)

        # Create a text field to show the BMI result
        self.bmi_output = QLineEdit(self)
        self.bmi_output.setReadOnly(True)  # Make it read-only
        self.bmi_output.setStyleSheet("""
            background-color: #f0f0f0;
            font-size: 18px;           /* Reduced font size */
            font-weight: bold;         /* Bold text for emphasis */
            color: #8e24aa;            /* Matching the app theme */
            padding: 5px;              /* Reduced padding */
            border: 2px solid #E1BEE7; /* Light purple border */
            border-radius: 5px;
            height: 25px;              /* Reduced height */
            margin-top: 10px;          /* Added margin for spacing */
            margin-bottom: 10px;       /* Reduced margin for spacing */
        """)
        layout.addWidget(self.bmi_output)

        # Create a larger canvas for the plot
        self.canvas = FigureCanvas(Figure(figsize=(8, 8)))  # Larger canvas for better visibility
        self.canvas.setStyleSheet("border: 2px solid #E1BEE7; border-radius: 10px; background-color: #f3e5f5;")
        layout.addWidget(self.canvas)

        self.tabs.addTab(bmi_tab, "BMI")

    def calculate_bmi(self):
        try:
            weight = float(self.weight_input.text())
            height = float(self.height_input.text())
            age = int(self.age_input.text())

            bmi_metric = BMIMetric(weight, height, age)
            bmi_value = bmi_metric.calculate_bmi()
            bmi_category = bmi_metric.get_bmi_category(bmi_value)

            # Display the BMI value and category in the text field
            self.bmi_output.setText(f"BMI Value: {bmi_value:.2f}, Category: {bmi_category}")

            # Plot the BMI value
            self.plot_bmi(bmi_value, bmi_category)

        except ValueError:
            self.bmi_output.setText("Please enter valid numbers for weight, height, and age.")

    def plot_bmi(self, bmi_value, bmi_category):
        categories = ['Underweight', 'Normal weight', 'Overweight', 'Obesity']
        values = [18.5, 24.9, 29.9, 40]

        # Clear the canvas
        self.canvas.figure.clear()

        # Create the plot
        ax = self.canvas.figure.add_subplot(111)
        bars = ax.bar(categories, values, color=['#8e24aa', '#66bb6a', '#ffa726', '#ef5350'], edgecolor='white',
                      linewidth=2, alpha=0.9, zorder=3)

        # Highlight the user's BMI value
        user_bmi_bar = ax.axhline(bmi_value, color='#42a5f5', linestyle='--', linewidth=2)
        ax.text(3.5, bmi_value, f'Your BMI: {bmi_value:.2f}', color='#42a5f5', fontsize=12, ha='right', va='bottom',
                zorder=4)

        # Set background and grid style
        ax.set_facecolor('#f3e5f5')  # Light purple background for the plot
        ax.grid(color='white', linestyle='--', linewidth=0.7, zorder=0)

        # Add labels and title with modern fonts
        ax.set_title("BMI Categories", fontsize=20, fontweight='bold', color='#d81b60')
        ax.set_xlabel("Categories", fontsize=16, color='#333')
        ax.set_ylabel("BMI Values", fontsize=16, color='#333')
        ax.tick_params(axis='x', labelsize=12, colors='#333')
        ax.tick_params(axis='y', labelsize=12, colors='#333')

        # Add interactive tooltips
        cursor = mplcursors.cursor(bars, hover=True)
        cursor.connect("add", lambda sel: sel.annotation.set_text(
            f'BMI Category: {categories[sel.index]}\nBMI Value: {values[sel.index]}'))
        cursor.connect("add", lambda sel: sel.annotation.set_bbox(
            {"boxstyle": "round,pad=0.5", "fc": "#e1bee7", "ec": "#8e24aa"}))

        # Update canvas
        self.canvas.draw()

    def create_meal_planner_tab(self):
        meal_tab = QWidget()
        layout = QVBoxLayout(meal_tab)

        label = QLabel("Meal Planner", self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
            color: #D81B60;  /* Soft pink for the label text */
            background-color: #F3E5F5;  /* Very light lavender for the background */
            padding: 10px;
        """)
        layout.addWidget(label)

        self.calories_input = QLineEdit(self)
        self.calories_input.setPlaceholderText("Enter Target Calories")
        self.set_text_field_style(self.calories_input)
        self.calories_input.setStyleSheet(self.calories_input.styleSheet() + "margin-bottom: 15px;")
        layout.addWidget(self.calories_input)



        generate_meal_button = QPushButton("Generate Meal Plan", self)
        self.set_button_style(generate_meal_button)
        generate_meal_button.clicked.connect(self.generate_meal_plan)
        layout.addWidget(generate_meal_button)

        self.meal_plan_output = QTextEdit(self)
        self.meal_plan_output.setReadOnly(True)
        self.meal_plan_output.setStyleSheet("""
            background-color: #f9f9f9;
            border: 1px solid #cccccc;
            font-size: 14px;
            line-height: 1.5;
            padding: 10px;
        """)
        layout.addWidget(self.meal_plan_output)

        self.tabs.addTab(meal_tab, "Meal Planner")

    def generate_meal_plan(self):
        try:
            target_calories = int(self.calories_input.text())
            meal_plan = self.meal_planner.get_meal_plan(target_calories)

            if meal_plan and "meals" in meal_plan:
                meals = ""
                for meal in meal_plan["meals"]:
                    meals += f"<b>- {meal['title']}</b><br>"
                    meals += f"  Ready in: {meal['readyInMinutes']} minutes<br>"
                    meals += f"  Servings: {meal['servings']}<br>"
                    meals += f"  Recipe Link: {meal['sourceUrl']}<br><br>"  # Display URL directly

                self.meal_plan_output.setHtml(f"<h3>Recommended Meals:</h3>{meals}")
            else:
                self.meal_plan_output.setPlainText("Failed to generate meal plan.")
        except ValueError:
            self.meal_plan_output.setPlainText("Please enter a valid number for target calories.")
        except Exception as e:
            self.meal_plan_output.setPlainText(f"An error occurred: {e}")








    def activate_voice_assistant(self):
        """Activate the voice assistant with enhanced visual and audio feedback."""
        self.voice_assistant_active = True
        self.dynamic_button.setText("Stop Recording")  # Change button label
        self.assistant_status_label.setText("🎤 Listening...")
        self.assistant_status_label.setStyleSheet("font-size: 20px; color: green; font-weight: bold;")

        # Start animated visual feedback
        self.start_recording_visual_feedback()

        # Play a sound to indicate recording start
        threading.Thread(target=lambda: self.play_sound("start_sound.mp3"), daemon=True).start()

        def listen():
            try:
                while self.voice_assistant_active:
                    with self.microphone as source:
                        # Adjust for ambient noise and start listening
                        self.recognizer.adjust_for_ambient_noise(source)
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=2)

                    # Stop recording if the user presses "Stop"
                    if not self.voice_assistant_active:
                        break

                    # Play a sound to indicate recording stop
                    threading.Thread(target=lambda: self.play_sound("stop_sound.mp3"), daemon=True).start()

                    # Stop visual feedback
                    self.stop_recording_visual_feedback()

                    # Process the audio input
                    try:
                        command = self.recognizer.recognize_google(audio)
                        self.chat_output.append(
                            f"<b>You (Voice)</b> ({datetime.datetime.now().strftime('%H:%M')}): {command}")
                        self.process_voice_command(command)
                    except sr.UnknownValueError:
                        self.chat_output.append("<b>Assistant</b>: Sorry, I couldn't understand that.")
                    except sr.RequestError as e:
                        self.chat_output.append(f"<b>Assistant</b>: Error with voice recognition service: {e}")
            except sr.WaitTimeoutError:
                self.chat_output.append("<b>Assistant</b>: No input detected. Please try again.")
                self.stop_recording_visual_feedback()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Voice Assistant Error: {str(e)}")
                self.stop_recording_visual_feedback()
            finally:
                self.deactivate_voice_assistant()  # Ensure cleanup

        threading.Thread(target=listen, daemon=True).start()

    def start_recording_visual_feedback(self):
        """Start the visual feedback for recording."""
        self.mic_animation = QMovie("mic_listening.gif")  # Animated microphone icon
        self.mic_label.setMovie(self.mic_animation)
        self.mic_animation.start()

        self.recording_timer_start = time.time()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_recording_timer)
        self.timer.start(1000)

    def stop_recording_visual_feedback(self):
        """Stop the visual feedback for recording."""
        self.assistant_status_label.setText("🔴 Recording Stopped.")
        self.assistant_status_label.setStyleSheet("font-size: 20px; color: gray;")
        if hasattr(self, "mic_animation") and self.mic_animation:
            self.mic_animation.stop()
            self.mic_label.clear()
        if hasattr(self, "timer") and self.timer:
            self.timer.stop()

    def update_recording_timer(self):
        """Update the timer for how long the recording has been active."""
        elapsed_time = int(time.time() - self.recording_timer_start)
        minutes, seconds = divmod(elapsed_time, 60)
        self.assistant_status_label.setText(f"🎤 Listening... {minutes}:{seconds:02}")

    def play_sound(self, file_path):
        """Play a sound file."""
        try:
            playsound.playsound(file_path)
        except Exception as e:
            print(f"Error playing sound: {e}")

    def process_voice_command(self, command: str):
        """Process commands received from voice input with intent detection."""
        command = command.lower()
        if "login" in command:
            self.switch_to_login()
        elif "sign up" in command or "register" in command:
            self.switch_to_signup()
        elif "meal plan" in command:
            self.central_widget.setCurrentIndex(3)  # Navigate to meal planner
        elif "calculate bmi" in command or "bmi" in command:
            self.central_widget.setCurrentIndex(4)  # Navigate to BMI calculator
        elif "exit" in command or "logout" in command:
            self.logout()
        else:
            self.chat_output.append("<b>Assistant</b>: Let me think about that...")
            response = self.fitness_ai_assistant.send_query(command)
            formatted_response = self.format_response(response)
            self.chat_output.append(f"<b>Assistant</b>: {formatted_response}")

    def deactivate_voice_assistant(self):
        """Deactivate the voice assistant and reset UI state."""
        self.voice_assistant_active = False
        self.assistant_status_label.setText("🔴 Status: Inactive")
        self.assistant_status_label.setStyleSheet("font-size: 20px; color: gray;")
        self.dynamic_button.setText("Record")  # Reset button label
        self.stop_recording_visual_feedback()
        self.chat_output.append("<b>Assistant</b>: Voice assistant deactivated.")

    def toggle_button_mode(self):
        """Toggle the dynamic button mode based on chat input or recording state."""
        if self.dynamic_button.text() == "Deactivate":
            return  # If actively recording, the button stays as "Deactivate"
        elif self.chat_input.text().strip():  # If chat input is not empty
            self.dynamic_button.setText("Send")
        else:  # If the chat input is empty
            self.dynamic_button.setText("Record")

    def handle_dynamic_button_action(self):
        """Handle actions for the dynamic button based on its current state."""
        current_text = self.dynamic_button.text()
        if current_text == "Send":
            self.send_chat_message()
        elif current_text == "Record":
            self.activate_voice_assistant()
        elif current_text == "Stop Recording":
            self.deactivate_voice_assistant()

    def create_interactive_assistant_tab(self):
        """Create the interactive assistant tab with enhanced chat and voice features."""
        assistant_tab = QWidget()
        layout = QVBoxLayout(assistant_tab)
        # Microphone animation label


        # Tab title
        label = QLabel("AI Assistant", self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
            color: #D81B60;  /* Soft pink for the label text */
            background-color: #F3E5F5;  /* Very light lavender for the background */
            padding: 10px;
        """)
        layout.addWidget(label)

        # Chat output area
        self.chat_output = QTextEdit(self)
        self.chat_output.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                color: #333333;
                padding: 8px;
                line-height: 1.5;
            }
        """)
        self.chat_output.setReadOnly(True)
        layout.addWidget(self.chat_output)

        # Input area and dynamic button
        input_layout = QHBoxLayout()

        self.chat_input = QLineEdit(self)
        self.chat_input.setPlaceholderText("Type your message here or press record...")
        self.set_text_field_style(self.chat_input)
        self.chat_input.textChanged.connect(self.toggle_button_mode)
        input_layout.addWidget(self.chat_input)


        self.mic_label = QLabel(self)
        self.mic_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.mic_label)

        self.dynamic_button = QPushButton("Record", self)
        self.set_button_style(self.dynamic_button)
        self.dynamic_button.clicked.connect(self.handle_dynamic_button_action)
        input_layout.addWidget(self.dynamic_button)

        layout.addLayout(input_layout)

        # Status label for assistant state
        self.assistant_status_label = QLabel("Status: Inactive", self)
        self.assistant_status_label.setAlignment(Qt.AlignCenter)
        self.assistant_status_label.setStyleSheet("font-size: 20px; color: #cccccc;")
        layout.addWidget(self.assistant_status_label)

        # Add the tab to the QTabWidget
        self.tabs.addTab(assistant_tab, "AI Assistant")

    def send_chat_message(self):
        """Handle user input and communicate with Gemini AI."""
        message = self.chat_input.text().strip()
        if message:
            self.chat_output.append(f"<b>You</b> ({datetime.datetime.now().strftime('%H:%M')}): {message}")
            self.chat_input.clear()

            self.chat_output.append("<b>Assistant</b> is typing...")
            self.chat_output.repaint()

            def process_message():
                try:
                    response = self.fitness_ai_assistant.send_query(message)
                    formatted_response = self.format_response(response)
                    self.chat_output.append(
                        f"<b>Assistant</b> ({datetime.datetime.now().strftime('%H:%M')}): {formatted_response}")
                except Exception as e:
                    self.chat_output.append(f"<b>Assistant</b>: Sorry, I encountered an error: {e}")
                finally:
                    self.chat_output.append("")  # Remove the typing indicator

            threading.Thread(target=process_message, daemon=True).start()
        else:
            self.chat_output.append("<b>Assistant</b>: Please enter a message or use the voice assistant.")

    def format_response(self, response: str) -> str:
        """Format the assistant's response to ensure consistency and readability."""
        return response.strip().replace("*", "").replace("\n", " ")



    def create_help_tab(self):
        help_tab = QWidget()
        layout = QVBoxLayout(help_tab)

        # Title
        label = QLabel("Help & FAQs", self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
            color: #D81B60;  /* Soft pink for the label text */
            background-color: #F3E5F5;  /* Very light lavender for the background */
            padding: 10px;
        """)
        layout.addWidget(label)

        # FAQ Section Header
        faq_header = QLabel("Frequently Asked Questions", self)
        faq_header.setAlignment(Qt.AlignCenter)
        faq_header.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: white;
            margin-bottom: 20px;
        """)
        layout.addWidget(faq_header)

        # FAQs with collapsible sections
        faqs = [
            ("How do I reset my password?", "Click on 'Forgot Password?' on the login screen."),
            ("How can I contact support?", "Please use the contact form on our website."),
            ("What features does this app offer?",
             "The app provides posture tracking,meal planning,fitness tracking and workout planning ."),
            ("Is my data secure?", "Yes, we use encryption to protect your data."),
            ("Can I sync my progress with other devices?", "Yes, you can sync your data across multiple devices.")
        ]

        for question, answer in faqs:
            question_label = QPushButton(question, self)
            self.set_button_style(question_label)

            answer_label = QLabel(answer, self)
            answer_label.setWordWrap(True)
            answer_label.setStyleSheet("""
                font-size: 16px; 
                color: #cccccc; 
                padding: 10px; a
                background-color: #f0f0f0; 
                border: 1px solid #cccccc; 
                border-radius: 5px;
                margin-left: 20px;  /* Indent the answer */
            """)
            answer_label.setVisible(False)

            # Toggle answer visibility on question click
            def toggle_answer(checked, answer_label=answer_label):
                answer_label.setVisible(not answer_label.isVisible())
                if answer_label.isVisible():
                    answer_label.setStyleSheet("""
                        font-size: 16px; 
                        color: black; 
                        padding: 10px; 
                        background-color: #e0e0e0;  /* Slightly darker when visible */
                        border: 1px solid #aaaaaa; 
                        border-radius: 5px;
                        margin-left: 20px; 
                    """)
                else:
                    answer_label.setStyleSheet("""
                        font-size: 16px; 
                        color: #cccccc; 
                        padding: 10px; 
                        background-color: #f0f0f0; 
                        border: 1px solid #cccccc; 
                        border-radius: 5px;
                        margin-left: 20px; 
                    """)

            question_label.clicked.connect(toggle_answer)
            layout.addWidget(question_label)
            layout.addWidget(answer_label)

        # Add a feedback section at the bottom
        feedback_label = QLabel("Still have questions? Reach out to our support team!", self)
        feedback_label.setAlignment(Qt.AlignCenter)
        feedback_label.setStyleSheet("""
            font-size: 18px;
            color: #ffffff;
            margin-top: 30px;
        """)
        layout.addWidget(feedback_label)

        contact_button = QPushButton("Contact Support", self)
        self.set_button_style(contact_button)
        contact_button.clicked.connect(
            self.open_contact_form)  # Connect to a method that opens a contact form or support page
        layout.addWidget(contact_button)

        self.tabs.addTab(help_tab, "Help")


    def open_contact_form(self):
        """Open the contact form for user inquiries."""
        # This method should create and display a contact form dialog
        contact_dialog = QDialog(self)
        contact_dialog.setWindowTitle("Contact Support")
        contact_dialog.setFixedSize(400, 400)

        layout = QVBoxLayout(contact_dialog)

        label = QLabel("Contact Support", contact_dialog)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #8e24aa;  /* Matching the app theme */
            margin-bottom: 10px;
        """)
        layout.addWidget(label)

        name_input = QLineEdit(contact_dialog)
        name_input.setPlaceholderText("Name")
        name_input.setStyleSheet("""
            font-size: 16px;
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 5px;
            margin-bottom: 10px;
        """)
        layout.addWidget(name_input)

        email_input = QLineEdit(contact_dialog)
        email_input.setPlaceholderText("Email")
        email_input.setStyleSheet("""
            font-size: 16px;
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 5px;
            margin-bottom: 10px;
        """)
        layout.addWidget(email_input)

        message_input = QTextEdit(contact_dialog)
        message_input.setPlaceholderText("Message")
        message_input.setStyleSheet("""
            font-size: 16px;
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 5px;
            margin-bottom: 10px;
        """)
        layout.addWidget(message_input)

        submit_button = QPushButton("Submit", contact_dialog)
        self.set_button_style(submit_button)
        layout.addWidget(submit_button)

        success_label = QLabel("", contact_dialog)
        success_label.setAlignment(Qt.AlignCenter)
        success_label.setStyleSheet("""
            font-size: 16px;
            color: #42a5f5;  /* Light blue color for success message */
            margin-top: 10px;
            font-weight: bold;
        """)
        layout.addWidget(success_label)

        def submit_contact_form():
            """Handle the submission of the contact form."""
            name = name_input.text()
            email = email_input.text()
            message = message_input.toPlainText()

            if not name or not email or not message:
                success_label.setText("Please fill in all fields.")
                success_label.setStyleSheet("""
                    font-size: 16px;
                    color: red;  /* Red color for error message */
                    margin-top: 10px;
                    font-weight: bold;
                """)
                return

            '''# Show a confirmation message within the dialog
            success_label.setText("Message sent! We'll get back to you shortly.")
            success_label.setStyleSheet("""
                font-size: 16px;
                color: purple;  /* Light blue color for success message */
                margin-top: 10px;
                font-weight: bold;
            """)'''
            name_input.clear()
            email_input.clear()
            message_input.clear()

        submit_button.clicked.connect(submit_contact_form)

        contact_dialog.exec_()

    def show_message(self, message):
        """Display a message in a dialog."""
        msg_box = QMessageBox()
        msg_box.setText(message)
        msg_box.exec_()

    def logout(self):
        """Logout function - Close the welcome window and return to the main window"""
        self.central_widget.setCurrentIndex(0)  # Go back to main UI
        self.add_to_history(0)  # Add main UI to history


'''def set_background_image(self, image_path=None):
        """Set a gradient or image background."""
        if image_path:
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                print("Failed to load background image.")
                return
            palette = QPalette()
            palette.setBrush(QPalette.Window, QBrush(pixmap))
            self.setPalette(palette)
        else:
            self.setStyleSheet("""
                QWidget {
                    background: linear-gradient(to bottom, #3C3B3F, #605C3C);
                }
            """)

'''



if __name__ == "__main__":

    api_key = "e5968cb05a3b42a4845c016350e83f17"
    gemini_api_key = "AIzaSyA1RJISbzG7WJ0T_ZRQIEVj_WWkhiHKml4"

    app = QApplication(sys.argv)
    window = LoginSignupApp(api_key, gemini_api_key)
    window.show()
    sys.exit(app.exec_())