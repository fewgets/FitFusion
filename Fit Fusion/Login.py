import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QStackedWidget, \
    QTabWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QBrush, QPalette


class LoginSignupApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('FitFusion: Fitness Tracker')
        self.setGeometry(100, 100, 800, 600)  # Set window size

        self.central_widget = QStackedWidget(self)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.central_widget)

        self.init_main_ui()
        self.init_login_ui()
        self.init_signup_ui()
        self.init_forgot_password_ui()
        self.init_welcome_ui()

        self.central_widget.setCurrentIndex(0)  # Start with the main UI

    def init_main_ui(self):
        """Initial window with Register Here options (Login/Signup)"""
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Background Image for Main Window
        self.set_background_image("th.jpg")  # Set your downloaded background image path here

        # Title label (adjusted font size)
        label = QLabel("Welcome to FitFusion!", self)
        label.setStyleSheet("font-size: 50px; font-weight: bold; color: white;")
        label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(label)

        # Buttons for Login and Signup with modern styles
        btn_login = QPushButton('Login', self)
        btn_login.setStyleSheet("""
            background-color: #4CAF50;
            font-size: 30px;
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        """)
        btn_login.clicked.connect(lambda: self.central_widget.setCurrentIndex(1))  # Switch to login
        main_layout.addWidget(btn_login)

        btn_signup = QPushButton('Signup', self)
        btn_signup.setStyleSheet("""
            background-color: #2196F3;
            font-size: 30px;
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        """)
        btn_signup.clicked.connect(lambda: self.central_widget.setCurrentIndex(2))  # Switch to signup
        main_layout.addWidget(btn_signup)

        self.central_widget.addWidget(main_widget)

    def init_login_ui(self):
        """Login UI with enhanced interaction"""
        login_widget = QWidget()
        layout = QVBoxLayout(login_widget)

        # Login Form UI with Custom Styling
        email_label = QLabel("Email: ", self)
        email_label.setStyleSheet("font-size: 30px; color: #444444; font-weight: bold;")
        layout.addWidget(email_label)

        self.login_email = QLineEdit(self)
        self.login_email.setStyleSheet("""
            font-size: 25px;
            padding: 15px;
            border: 2px solid #444444;
            border-radius: 5px;
            background-color: #f1f1f1;
        """)
        self.login_email.setPlaceholderText("Enter your email")
        layout.addWidget(self.login_email)

        password_label = QLabel("Password: ", self)
        password_label.setStyleSheet("font-size: 30px; color: #444444; font-weight: bold;")
        layout.addWidget(password_label)

        self.login_password = QLineEdit(self)
        self.login_password.setStyleSheet("""
            font-size: 25px;
            padding: 15px;
            border: 2px solid #444444;
            border-radius: 5px;
            background-color: #f1f1f1;
        """)
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setPlaceholderText("Enter your password")
        layout.addWidget(self.login_password)

        # Forgot Password Link
        forgot_password_link = QLabel('<a href="#">Forgot Password?</a>', self)
        forgot_password_link.setStyleSheet("font-size: 20px; color: #4CAF50; font-weight: bold;")
        forgot_password_link.setOpenExternalLinks(True)  # Make the link clickable
        forgot_password_link.mousePressEvent = self.open_forgot_password_window
        layout.addWidget(forgot_password_link)
        # Feedback label
        self.login_feedback = QLabel("", self)
        self.login_feedback.setStyleSheet("font-size: 25px; color: red;")
        layout.addWidget(self.login_feedback)

        # Login button with animation and feedback
        btn_login = QPushButton("Login", self)
        btn_login.setStyleSheet("""
                background-color: #2E3B4E;
                font-size: 25px;
                color: white;
                padding: 15px;
                border-radius: 8px;
                margin-top: 20px;
                font-weight: bold;
            """)
        btn_login.setCursor(Qt.PointingHandCursor)  # Change cursor on hover for better interaction
        btn_login.clicked.connect(self.on_login_button_click)
        layout.addWidget(btn_login)

        self.central_widget.addWidget(login_widget)

    def on_login_button_click(self):
        """Triggered when the login button is clicked."""
        # Validate fields
        email = self.login_email.text().strip()
        password = self.login_password.text().strip()

        if not email:
            self.login_feedback.setText("Please enter your email.")
            return
        if not password:
            self.login_feedback.setText("Please enter your password.")
            return

        # Proceed with checking credentials
        self.login_feedback.setText("")  # Clear previous feedback
        self.login_database()

    def login_database(self):
        """Check credentials in the database for login"""
        email = self.login_email.text().strip()
        password = self.login_password.text().strip()

        conn = sqlite3.connect("1.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM test WHERE email=? AND password=?", (email, password))
        row = cur.fetchall()
        conn.close()

        if row:
            user_name = row[0][1]
            self.login_feedback.setStyleSheet("font-size: 25px; color: green;")
            self.login_feedback.setText(f"Login successful. Welcome {user_name}!")
            self.show_welcome_frame(user_name)  # Show welcome frame upon successful login
        else:
            self.login_feedback.setStyleSheet("font-size: 25px; color: red;")
            self.login_feedback.setText("Incorrect email or password.")

    def open_forgot_password_window(self, event):
        """Open the forgot password dialog"""
        self.central_widget.setCurrentIndex(3)  # Switch to forgot password UI

    def init_forgot_password_ui(self):
        """Forgot Password UI"""
        forgot_widget = QWidget()
        layout = QVBoxLayout(forgot_widget)

        # Label and input for email
        email_label = QLabel("Enter your registered email:", self)
        email_label.setStyleSheet("font-size: 25px; color: #444444; font-weight: bold;")
        layout.addWidget(email_label)

        self.forgot_email = QLineEdit(self)
        self.forgot_email.setStyleSheet("""
                font-size: 25px;
                padding: 15px;
                border: 2px solid #444444;
                border-radius: 5px;
                background-color: #f1f1f1;
            """)
        self.forgot_email.setPlaceholderText("Enter your email")
        layout.addWidget(self.forgot_email)

        # Submit button for password reset
        btn_reset = QPushButton("Reset Password", self)
        btn_reset.setStyleSheet("""
                background-color: #2E3B4E;
                font-size: 25px;
                color: white;
                padding: 15px;
                border-radius: 8px;
                margin-top: 20px;
                font-weight: bold;
            """)
        btn_reset.clicked.connect(self.reset_password)
        layout.addWidget(btn_reset)

        # Feedback label
        self.forgot_password_feedback = QLabel("", self)
        self.forgot_password_feedback.setStyleSheet("font-size: 25px; color: green;")
        layout.addWidget(self.forgot_password_feedback)

        self.central_widget.addWidget(forgot_widget)

    def reset_password(self):
        """Simulate password reset process (for now just a placeholder)"""
        email = self.forgot_email.text().strip()

        if not email:
            self.forgot_password_feedback.setText("Please enter your email.")
            return

        # Here, you would typically connect to a password reset process, e.g. sending an email.
        self.forgot_password_feedback.setText("Password reset instructions sent to your email!")
        self.central_widget.setCurrentIndex(0)  # Go back to main UI after reset

    def init_signup_ui(self):
        # Signup UI
        signup_widget = QWidget()
        layout = QVBoxLayout(signup_widget)

        # Signup Form UI with Custom Styling
        name_label = QLabel("User  Name: ", self)
        name_label.setStyleSheet("font-size: 30px; color: #333333;")
        layout.addWidget(name_label)

        self.signup_name = QLineEdit(self)
        self.signup_name.setStyleSheet("font-size: 25px; padding: 10px; border-radius: 5px;")
        layout.addWidget(self.signup_name)

        email_label = QLabel("User  Email: ", self)
        email_label.setStyleSheet("font-size: 30px; color: #333333;")
        layout.addWidget(email_label)

        self.signup_email = QLineEdit(self)
        self.signup_email.setStyleSheet("font-size: 25px; padding: 10px; border-radius: 5px;")
        layout.addWidget(self.signup_email)

        password_label = QLabel("Password: ", self)
        password_label.setStyleSheet("font-size: 30px; color: #333333;")
        layout.addWidget(password_label)

        self.signup_password = QLineEdit(self)
        self.signup_password.setStyleSheet("font-size: 25px; padding: 10px; border-radius: 5px;")
        self.signup_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.signup_password)

        # Feedback label
        self.signup_feedback = QLabel("", self)
        self.signup_feedback.setStyleSheet("font-size: 25px; color: green;")
        layout.addWidget(self.signup_feedback)

        # Sign up button
        btn_signup = QPushButton("Signup", self)
        btn_signup.setStyleSheet("""
                background-color: #2196F3;
                font-size: 25px;
                color: white;
                padding: 15px;
                border-radius: 10px;
                margin-top: 20px;
            """)
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
        conn.close()

        self.signup_feedback.setText("Account created successfully!")
        # Automatically switch to login window after successful signup
        self.signup_name.clear()
        self.signup_email.clear()
        self.signup_password.clear()
        self.central_widget.setCurrentIndex(0)  # Go back to main UI

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
        btn_logout.setStyleSheet("""
                background-color: #FF5722;
                font-size: 25px;
                color: white;
                padding: 15px;
                border-radius: 10px;
                margin-top: 20px;
            """)
        btn_logout.clicked.connect(self.logout)
        layout.addWidget(btn_logout)

        self.central_widget.addWidget(welcome_widget)

    def show_welcome_frame(self, user_name):
        """Show welcome message and initialize tabs after successful login"""
        self.central_widget.setCurrentIndex(5)  # Switch to a new index for tabs
        self.init_tabs(user_name)  # Initialize tabs

    def init_tabs(self, user_name):
        """Initialize the tabbed interface after login"""
        tabs_widget = QWidget()
        tabs_layout = QVBoxLayout(tabs_widget)

        # Create QTabWidget
        self.tabs = QTabWidget()

        # Apply the updated style sheet for colorful and fitting tab buttons
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                background-color: #4CAF50;  /* Green background */
                color: white;               /* White text */
                font-size: 14px;            /* Font size */
                padding: 10px 25px;         /* Ensure proper padding for better visibility */
                border: 1px solid #ccc;     /* Border around tabs */
                border-bottom: none;        /* Smooth look */
                border-radius: 4px;         /* Rounded corners */
                min-width: 100px;           /* Minimum width to prevent truncation */
            }

            QTabBar::tab:selected {
                background-color: #45a049;  /* Darker green for selected tab */
                font-weight: bold;          /* Bold text for selected tab */
            }

            QTabBar::tab:hover {
                background-color: #66bb6a;  /* Lighter green on hover */
            }

            QTabWidget::pane {
                border: 1px solid #ccc;     /* Border around tab content */
                border-top: none;           /* Merge content with tabs */
            }
        """)

        self.tabs.setElideMode(Qt.ElideNone)  # Ensure full text visibility
        self.tabs.setTabPosition(QTabWidget.North)  # Adjust if needed
        self.tabs.setUsesScrollButtons(True)  # Enable scroll if tabs overflow

        tabs_layout.addWidget(self.tabs)

        # Create tabs
        self.create_workout_planner_tab()
        self.create_streak_tab()
        self.create_bmi_visualization_tab()
        self.create_meal_planner_tab()
        self.create_customer_service_tab()

        # Set the tabs widget as the central widget
        self.central_widget.addWidget(tabs_widget)
        self.central_widget.setCurrentWidget(tabs_widget)  # Show the tabs widget

    def create_workout_planner_tab(self):
        """Create the Workout Planner tab"""
        workout_tab = QWidget()
        layout = QVBoxLayout(workout_tab)

        label = QLabel("Workout Planner", self)
        label.setStyleSheet("font-size: 30px; font-weight: bold; color: white;")  # Set text color to white
        layout.addWidget(label)

        self.tabs.addTab(workout_tab, "Workouts")

    def create_streak_tab(self):
        """Create the Streak tab"""
        streak_tab = QWidget()
        layout = QVBoxLayout(streak_tab)

        label = QLabel("Streak Tracker", self)
        label.setStyleSheet("font-size: 30px; font-weight: bold; color: white;")  # Set text color to white
        layout.addWidget(label)

        self.tabs.addTab(streak_tab, "Streak")

    def create_bmi_visualization_tab(self):
        """Create the BMI Visualization tab"""
        bmi_tab = QWidget()
        layout = QVBoxLayout(bmi_tab)

        label = QLabel("BMI Visualization", self)
        label.setStyleSheet("font-size: 30px; font-weight: bold; color: white;")  # Set text color to white
        layout.addWidget(label)

        self.tabs.addTab(bmi_tab, "BMI")

    def create_meal_planner_tab(self):
        """Create the Meal Planner tab"""
        meal_tab = QWidget()
        layout = QVBoxLayout(meal_tab)

        label = QLabel("Meal Planner", self)
        label.setStyleSheet("font-size: 30px; font-weight: bold; color: white;")  # Set text color to white
        layout.addWidget(label)

        self.tabs.addTab(meal_tab, "Meal Planner")

    def create_customer_service_tab(self):
        """Create the Customer Service tab"""
        service_tab = QWidget()
        layout = QVBoxLayout(service_tab)

        label = QLabel("Customer Service", self)
        label.setStyleSheet("font-size: 30px; font-weight: bold; color: white;")  # Set text color to white
        layout.addWidget(label)

        self.tabs.addTab(service_tab, "Help")

    def logout(self):
        """Logout function - Close the welcome window and return to the main window"""
        self.central_widget.setCurrentIndex(0)  # Go back to main UI

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
    app = QApplication(sys.argv)
    window = LoginSignupApp()
    window.show()
    sys.exit(app.exec_())