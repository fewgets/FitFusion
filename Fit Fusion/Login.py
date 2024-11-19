import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QStackedWidget, \
    QTabWidget, QSizePolicy, QHBoxLayout, QMessageBox, QTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QBrush, QPalette
from google.auth.transport import requests


# BMI Calculation Classes
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

    def get_meal_plan(self, target_calories):
        params = {
            "apiKey": self.api_key,
            "timeFrame": "day",
            "targetCalories": target_calories,
        }
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching meal plan: {e}")
            return None

class LoginSignupApp(QWidget):
    def __init__(self, api_key):
        super().__init__()
        self.meal_planner = MealPlanner(api_key)  # Create an instance of MealPlanner
        self.setWindowTitle('FitFusion: Fitness Tracker')
        self.setGeometry(100, 100, 800, 600)  # Set window size

        self.central_widget = QStackedWidget(self)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.central_widget)

        # Add back and forward buttons
        self.back_button = QPushButton("Back")
        self.forward_button = QPushButton("Forward")

        # Set button styles
        self.set_button_style(self.back_button)
        self.set_button_style(self.forward_button)

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

        self.init_main_ui()
        self.init_login_ui()
        self.init_signup_ui()
        self.init_forgot_password_ui()
        self.init_welcome_ui()

        self.central_widget.setCurrentIndex(0)  # Start with the main UI
        self.add_to_history(0)  # Add main UI to history

    def set_button_style(self, button):
        button.setStyleSheet("""
            background-color: #E1BEE7;  /* Light purple background */
            color: black;                /* Black text for contrast */
            font-size: 18px;             /* Increased font size */
            padding: 10px 20px;          /* Padding for better visibility */
            border: 1px solid #ccc;      /* Border around buttons */
            border-radius: 4px;          /* Rounded corners */
            cursor: pointer;              /* Change cursor to pointer */
        """)
        button.setStyleSheet(button.styleSheet() + """
            QPushButton:hover {
                background-color: #D5006D;  /* Darker purple on hover */
            }
        """)

    def set_text_field_style(self, text_field):
        text_field.setStyleSheet("""
            font-size : 24px;  /* Increased font size */
            padding: 12px;    /* Increased padding */
            border: 2px solid #444444;
            border-radius: 5px;
            background-color: #f1f1f1;
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
        """Initial window with Register Here options (Login/Signup)"""
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        self.set_background_image("background_image_dark")
        label = QLabel("Welcome to FitFusion!", self)
        label.setStyleSheet("font-size: 50px; font-weight: bold; color: white;")
        label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(label)

        btn_login = QPushButton('Login', self)
        self.set_button_style(btn_login)
        btn_login.setStyleSheet(btn_login.styleSheet() + "font-size: 30px; margin-top: 20px;")
        btn_login.clicked.connect(lambda: self.switch_to_login())
        main_layout.addWidget(btn_login)

        btn_signup = QPushButton('Signup', self)
        self.set_button_style(btn_signup)
        btn_signup.setStyleSheet(btn_signup.styleSheet() + "font-size: 30px; margin-top: 20px;")
        btn_signup.clicked.connect(lambda: self.switch_to_signup())
        main_layout.addWidget(btn_signup)

        self.central_widget.addWidget(main_widget)

    def switch_to_login(self):
        self.central_widget.setCurrentIndex(1)
        self.add_to_history(1)

    def switch_to_signup(self):
        self.central_widget.setCurrentIndex(2)
        self.add_to_history(2)

    def init_login_ui(self):
        """Login UI with enhanced interaction"""
        login_widget = QWidget()
        layout = QVBoxLayout(login_widget)

        email_label = QLabel("Email: ", self)
        email_label.setStyleSheet("font-size: 30px; color: #444444; font-weight: bold;")
        layout.addWidget(email_label)

        self.login_email = QLineEdit(self)
        self.set_text_field_style(self.login_email)
        self.login_email.setPlaceholderText("Enter your email")
        layout.addWidget(self.login_email)

        password_label = QLabel("Password: ", self)
        password_label.setStyleSheet("font-size: 30px; color: #444444; font-weight: bold;")
        layout.addWidget(password_label)

        self.login_password = QLineEdit(self)
        self.set_text_field_style(self.login_password)
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setPlaceholderText("Enter your password")
        layout.addWidget(self.login_password)

        btn_forgot_password = QPushButton("Forgot Password?", self)
        self.set_button_style(btn_forgot_password)
        btn_forgot_password.clicked.connect(self.open_forgot_password_window)
        layout.addWidget(btn_forgot_password)

        self.login_feedback = QLabel("", self)
        self.login_feedback.setStyleSheet("font-size: 25px; color: red;")
        layout.addWidget(self.login_feedback)

        btn_login = QPushButton("Login", self)
        self.set_button_style(btn_login)
        btn_login.setStyleSheet(btn_login.styleSheet() + "font-size: 25px; margin-top: 20px; font-weight: bold;")
        btn_login.clicked.connect(self.on_login_button_click)
        layout.addWidget(btn_login)

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

        conn = sqlite3
        conn = sqlite3.connect("1.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM test WHERE email=? AND password=?", (email, password))
        row = cur.fetchall()
        conn.close()

        if row:
            user_name = row[0][1]
            self.login_feedback.setStyleSheet("font-size: 25px; color: green;")
            self.login_feedback.setText(f"Login successful. Welcome {user_name}!")
            self.show_welcome_frame(user_name)
        else:
            self.login_feedback.setStyleSheet("font-size: 25px; color: red;")
            self.login_feedback.setText("Incorrect email or password.")

    def open_forgot_password_window(self):
        """Open the forgot password dialog"""
        self.central_widget.setCurrentIndex(3)
        self.add_to_history(3)

    def init_forgot_password_ui(self):
        """Forgot Password UI"""
        forgot_widget = QWidget()
        layout = QVBoxLayout(forgot_widget)

        email_label = QLabel("Enter your registered email:", self)
        email_label.setStyleSheet("font-size: 25px; color: #444444; font-weight: bold;")
        layout.addWidget(email_label)

        self.forgot_email = QLineEdit(self)
        self.set_text_field_style(self.forgot_email)
        self.forgot_email.setPlaceholderText("Enter your email")
        layout.addWidget(self.forgot_email)

        btn_reset = QPushButton("Reset Password", self)
        self.set_button_style(btn_reset)
        btn_reset.setStyleSheet(btn_reset.styleSheet() + "font-size: 25px; margin-top: 20px; font-weight: bold;")
        btn_reset.clicked.connect(self.reset_password)
        layout.addWidget(btn_reset)

        self.forgot_password_feedback = QLabel("", self)
        self.forgot_password_feedback.setStyleSheet("font-size: 25px; color: green;")
        layout.addWidget(self.forgot_password_feedback)

        self.central_widget.addWidget(forgot_widget)

    def reset_password(self):
        """Simulate password reset process"""
        email = self.forgot_email.text().strip()

        if not email:
            self.forgot_password_feedback.setText("Please enter your email.")
            return

        self.forgot_password_feedback.setText("Password reset instructions sent to your email!")
        self.central_widget.setCurrentIndex(0)
        self.add_to_history(0)

    def init_signup_ui(self):
        """Signup UI"""
        signup_widget = QWidget()
        layout = QVBoxLayout(signup_widget)

        name_label = QLabel("User  Name: ", self)
        name_label.setStyleSheet("font-size: 30px; color: #333333;")
        layout.addWidget(name_label)

        self.signup_name = QLineEdit(self)
        self.set_text_field_style(self.signup_name)
        layout.addWidget(self.signup_name)

        email_label = QLabel("User  Email: ", self)
        email_label.setStyleSheet("font-size: 30px; color: #333333;")
        layout.addWidget(email_label)

        self.signup_email = QLineEdit(self)
        self.set_text_field_style(self.signup_email)
        layout.addWidget(self.signup_email)

        password_label = QLabel("Password: ", self)
        password_label.setStyleSheet("font-size: 30px; color: #333333;")
        layout.addWidget(password_label)

        self.signup_password = QLineEdit(self)
        self.set_text_field_style(self.signup_password)
        self.signup_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.signup_password)

        self.signup_feedback = QLabel("", self)
        self.signup_feedback.setStyleSheet("font-size: 25px; color: green;")
        layout.addWidget(self.signup_feedback)

        btn_signup = QPushButton("Signup", self)
        self.set_button_style(btn_signup)
        btn_signup.setStyleSheet(btn_signup.styleSheet() + "font-size: 25px; margin-top: 20px;")
        btn_signup.clicked.connect(self.signup_database)
        layout.addWidget(btn_signup)

        self.central_widget.addWidget(signup_widget)

    def signup_database(self):
        """Handle database actions for signup"""
        name = self.signup_name.text().strip()
        email = self.signup_email.text().strip()
        password = self.signup_password.text().strip()

        if not name or not email or not password:
            self.signup_feedback.setText("Please fill in all fields.")
            return

        conn = sqlite3.connect("1.db")
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS test(id INTEGER PRIMARY KEY, name TEXT, email TEXT, password TEXT)")
        cur.execute("INSERT INTO test (name, email, password) VALUES (?, ?, ?)", (name, email, password))

        conn.commit()
        conn.close
        self.signup_feedback.setText("Account created successfully!")
        self.signup_name.clear()
        self.signup_email.clear()
        self.signup_password.clear()
        self.central_widget.setCurrentIndex(0)  # Go back to main UI
        self.add_to_history(0)  # Add main UI to history

    def init_welcome_ui(self):
        """Show a welcome frame after successful login"""
        welcome_widget = QWidget()
        layout = QVBoxLayout(welcome_widget)

        self.welcome_msg = QLabel("", self)
        self.welcome_msg.setStyleSheet("font-size: 40px; font-weight: bold; color: #333333;")
        self.welcome_msg.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.welcome_msg)

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

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                background-color: #E1BEE7;  
                color: black;               
                font-size: 14px;            
                padding: 10px 25px;         
                border: 1px solid #ccc;     
                border-bottom: none;        
                border-radius: 4px;         
                min-width: 100px;           
            }

            QTabBar::tab:selected {
                background-color: #D81B60;  
                font-weight: bold;          
            }

            QTabBar::tab:hover {
                background-color: #D5006D;  
            }

            QTabWidget::pane {
                border: 1px solid #ccc;     
                border-top: none;           
            }
        """)

        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tabs_layout.addWidget(self.tabs)

        self.create_workout_planner_tab()
        self.create_streak_tab()
        self.create_bmi_visualization_tab()
        self.create_meal_planner_tab()
        self.create_voice_assistant_tab()
        self.create_textual_chat_tab()
        self.create_help_tab()

        self.central_widget.addWidget(tabs_widget)
        self.central_widget.setCurrentWidget(tabs_widget)
        tabs_layout.setStretch(0, 1)

    def create_workout_planner_tab(self):
        workout_tab = QWidget()
        layout = QVBoxLayout(workout_tab)

        label = QLabel("Workout Planner", self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 30px; font-weight: bold; color: white;")
        layout.addWidget(label)

        self.workout_duration_input = QLineEdit(self)
        self.workout_duration_input.setPlaceholderText("Duration (minutes)")
        self.set_text_field_style(self.workout_duration_input)
        layout.addWidget(self.workout_duration_input)

        self.muscle_group_input = QLineEdit(self)
        self.muscle_group_input.setPlaceholderText("Target Muscle Group")
        self.set_text_field_style(self.muscle_group_input)
        layout.addWidget(self.muscle_group_input)

        self.workout_location_input = QLineEdit(self)
        self.workout_location_input.setPlaceholderText("Workout Location")
        self.set_text_field_style(self.workout_location_input)
        layout.addWidget(self.workout_location_input)

        self.equipment_input = QLineEdit(self)
        self.equipment_input.setPlaceholderText("Available Equipment")
        self.set_text_field_style(self.equipment_input)
        layout.addWidget(self.equipment_input)

        generate_button = QPushButton("Generate Workout Plan", self)
        self.set_button_style(generate_button)
        generate_button.clicked.connect(self.generate_workout_plan)
        layout.addWidget(generate_button)

        self.workout_plan_output = QLabel("", self)
        layout.addWidget(self.workout_plan_output)

        self.tabs.addTab(workout_tab, "Workouts")

    def generate_workout_plan(self):
        duration = self.workout_duration_input.text()
        muscle_group = self.muscle_group_input.text()
        location = self.workout_location_input.text()
        equipment = self.equipment_input.text()

        # Placeholder for workout plan generation logic
        self.workout_plan_output.setText(f"Workout Plan for {duration} minutes targeting {muscle_group} at {location} with {equipment}.")

    def create_streak_tab(self):
        streak_tab = QWidget()
        layout = QVBoxLayout(streak_tab)

        label = QLabel("Streak Tracker", self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 30px; font-weight: bold; color: white;")
        layout.addWidget(label)

        button_reset = QPushButton("Reset Streak", self)
        button_view = QPushButton("View Progress", self)

        self.set_button_style(button_reset)
        self.set_button_style(button_view)

        button_layout = QHBoxLayout()
        button_layout.addWidget(button_reset)
        button_layout.addWidget(button_view)

        layout.addLayout(button_layout)
        self.tabs.addTab(streak_tab, "Streak")

    def create_bmi_visualization_tab(self):
        bmi_tab = QWidget()
        layout = QVBoxLayout(bmi_tab)

        label = QLabel("BMI Visualization", self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 30px; font-weight: bold; color: white;")
        layout.addWidget(label)

        self.weight_input = QLineEdit(self)
        self.weight_input.setPlaceholderText("Weight (kg)")
        self.set_text_field_style(self.weight_input)
        layout.addWidget(self.weight_input)

        self.height_input = QLineEdit(self)
        self.height_input.setPlaceholderText("Height (cm)")
        self.set_text_field_style(self.height_input)
        layout.addWidget(self.height_input)

        self.age_input = QLineEdit(self)
        self.age_input.setPlaceholderText("Age")
        self.set_text_field_style(self.age_input)
        layout.addWidget(self.age_input)

        calculate_button = QPushButton("Calculate BMI", self)
        self.set_button_style(calculate_button)
        calculate_button.clicked.connect(self.calculate_bmi)
        layout.addWidget(calculate_button)

        self.bmi_output = QLineEdit(self)
        self.bmi_output.setReadOnly(True)
        layout.addWidget(self.bmi_output)

        self.tabs.addTab(bmi_tab, "BMI")

    def calculate_bmi(self):
        try:
            weight = float(self.weight_input.text())
            height = float(self.height_input.text())
            age = int(self.age_input.text())

            bmi_metric = BMIMetric(weight, height, age)
            bmi_value = bmi_metric.calculate_bmi()
            bmi_category = bmi_metric.get_bmi_category(bmi_value)

            self.bmi_output.setText(f"BMI Value: {bmi_value:.2f}, Category: {bmi_category}")

        except ValueError:
            self.bmi_output.setText("Please enter valid numbers for weight, height, and age.")
    def create_meal_planner_tab(self):
        meal_tab = QWidget()
        layout = QVBoxLayout(meal_tab)

        label = QLabel("Meal Planner", self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 30px; font-weight: bold; color: black;")
        layout.addWidget(label)

        self.calories_input = QLineEdit(self)
        self.calories_input.setPlaceholderText("Target Calories")
        self.set_text_field_style(self.calories_input)
        layout.addWidget(self.calories_input)

        generate_meal_button = QPushButton("Generate Meal Plan", self)
        self.set_button_style(generate_meal_button)
        generate_meal_button.clicked.connect(self.generate_meal_plan)
        layout.addWidget(generate_meal_button)

        self.meal_plan_output = QTextEdit(self)
        self.meal_plan_output.setReadOnly(True)
        layout.addWidget(self.meal_plan_output)

        self.tabs.addTab(meal_tab, "Meals")


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

    def create_voice_assistant_tab(self):
        voice_tab = QWidget()
        layout = QVBoxLayout(voice_tab)

        label = QLabel("Voice Assistant", self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 30px; font-weight: bold; color: white;")
        layout.addWidget(label)

        activate_button = QPushButton("Activate Voice Assistant", self)
        self.set_button_style(activate_button)
        layout.addWidget(activate_button)

        # Placeholder for voice assistant functionality
        voice_instruction = QLabel("Voice assistant features will be implemented here.", self)
        voice_instruction.setAlignment(Qt.AlignCenter)
        voice_instruction.setStyleSheet("font-size: 20px; color: #cccccc;")
        layout.addWidget(voice_instruction)

        self.tabs.addTab(voice_tab, "Voice Assistant")

    def create_textual_chat_tab(self):
        chat_tab = QWidget()
        layout = QVBoxLayout(chat_tab)

        label = QLabel("Textual Chat", self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 30px; font-weight: bold; color: white;")
        layout.addWidget(label)

        self.chat_input = QLineEdit(self)
        self.chat_input.setPlaceholderText("Type your message here...")
        self.set_text_field_style(self.chat_input)
        layout.addWidget(self.chat_input)

        send_button = QPushButton("Send", self)
        self.set_button_style(send_button)
        send_button.clicked.connect(self.send_chat_message)
        layout.addWidget(send_button)

        self.chat_output = QTextEdit(self)
        self.chat_output.setReadOnly(True)
        layout.addWidget(self.chat_output)

        self.tabs.addTab(chat_tab, "Textual Chat")

    def send_chat_message(self):
        message = self.chat_input.text().strip()
        if message:
            self.chat_output.append(f"You: {message}")
            self.chat_input.clear()
            # Placeholder for response logic
            self.chat_output.append("Assistant: This feature is under development.")
        else:
            self.chat_output.append("Assistant: Please enter a message.")

    def create_help_tab(self):
        help_tab = QWidget()
        layout = QVBoxLayout(help_tab)

        label = QLabel("Help & FAQs", self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 30px; font-weight: bold; color: white;")
        layout.addWidget(label)

        faqs = [
            "Q: How do I reset my password?\nA: Click on 'Forgot Password?' on the login screen.",
            "Q: How can I contact support?\nA: Please use the contact form on our website.",
            "Q: What features does this app offer?\nA: The app provides workout planning, meal planning, and fitness tracking."
        ]

        for faq in faqs:
            faq_label = QLabel(faq, self)
            faq_label.setStyleSheet("font-size: 20px; color: #cccccc;")
            layout.addWidget(faq_label)

        self.tabs.addTab(help_tab, "Help")

    def logout(self):
        """Logout function - Close the welcome window and return to the main window"""
        self.central_widget.setCurrentIndex(0)  # Go back to main UI
        self.add_to_history(0)  # Add main UI to history

    def set_background_image(self, image_path):
        """Set a background image for the window."""
        pixmap = QPixmap(image_path)  # Load the image
        if pixmap.isNull():
            print("Failed to load background image.")
            return

        # Set the background image to the central widget
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(pixmap))
        self.setPalette(palette)



if __name__ == "__main__":
    api_key = "e5968cb05a3b42a4845c016350e83f17"
    app = QApplication(sys.argv)
    window = LoginSignupApp(api_key)

    window.show()
    sys.exit(app.exec_())