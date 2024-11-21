import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QBrush, QPalette

class LoginSignupApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('FitFusion: Fitness Tracker')
        self.setGeometry(100, 100, 1920, 1080)  # Set window size to 1920x1080

        self.init_main_ui()

    def init_main_ui(self):
        """Initial window with Register Here options (Login/Signup)"""
        self.main_layout = QVBoxLayout()

        # Background Image for Main Window
        self.set_background_image("th.jpg")  # Set your downloaded background image path here

        # Title label (adjusted font size)
        label = QLabel("Welcome to FitFusion!", self)
        label.setStyleSheet("font-size: 50px; font-weight: bold; color: #F0F0F0;")  # Light gray color
        label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(label)

        # Buttons for Login and Signup with modern masculine styles
        btn_login = QPushButton('Login', self)
        btn_login.setStyleSheet("""
            background-color: #2A3D57;  # Cool dark blue background
            font-size: 30px;
            color: #FFFFFF;  # White text
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
            font-weight: bold;
        """)
        btn_login.clicked.connect(self.show_login_window)
        self.main_layout.addWidget(btn_login)

        btn_signup = QPushButton('Signup', self)
        btn_signup.setStyleSheet("""
            background-color: #34495E;  # Slightly lighter dark background
            font-size: 30px;
            color: #FFFFFF;  # White text
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
            font-weight: bold;
        """)
        btn_signup.clicked.connect(self.show_signup_window)
        self.main_layout.addWidget(btn_signup)

        # Set the main layout
        self.setLayout(self.main_layout)

    def set_background_image(self, image_path):
        """Set a background image for the window."""
        pixmap = QPixmap(image_path)  # Load the image
        if pixmap.isNull():
            print("Error: Image could not be loaded!")
            return

        # Scale the image to fit the window size
        pixmap = pixmap.scaled(self.size(), aspectRatioMode=1)  # Scaling the image to match window size

        # Set the image as background using QPalette
        brush = QBrush(pixmap)
        palette = self.palette()
        palette.setBrush(QPalette.Background, brush)
        self.setPalette(palette)

    def resizeEvent(self, event):
        """Handle window resizing to rescale the background image."""
        # Resize background image when the window is resized
        self.set_background_image("th.jpg")
        super().resizeEvent(event)




    def show_login_window(self):
        """Show login window with enhanced interaction and masculine styling"""
        self.login_window = QWidget()
        self.login_window.setWindowTitle("Login")
        self.login_window.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # Background Image for Login Window
        self.set_background_image("th.jpg")  # Use the same background

        # Login Form UI with Custom Styling (Masculine Touch)
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

        # Forgot Password Link (opens a dialog for password recovery)
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

        self.login_window.setLayout(layout)
        self.login_window.show()

    def on_login_button_click(self):
        """Triggered when the login button is clicked."""
        # Disable the login button while checking credentials
        self.login_window.setCursor(Qt.WaitCursor)

        # Validate fields
        email = self.login_email.text().strip()
        password = self.login_password.text().strip()

        if not email:
            self.login_feedback.setText("Please enter your email.")
            self.login_window.setCursor(Qt.ArrowCursor)
            return
        if not password:
            self.login_feedback.setText("Please enter your password.")
            self.login_window.setCursor(Qt.ArrowCursor)
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

        if row != []:
            user_name = row[0][1]
            self.login_feedback.setStyleSheet("font-size: 25px; color: green;")
            self.login_feedback.setText(f"Login successful. Welcome {user_name}!")
            self.show_welcome_frame(user_name)  # Show new frame upon successful login
        else:
            self.login_feedback.setStyleSheet("font-size: 25px; color: red;")
            self.login_feedback.setText("Incorrect email or password.")
            self.login_window.setCursor(Qt.ArrowCursor)  # Restore cursor once done

    def open_forgot_password_window(self, event):
        """Open the forgot password dialog"""
        self.forgot_password_window = QWidget()
        self.forgot_password_window.setWindowTitle("Forgot Password")
        self.forgot_password_window.setGeometry(100, 100, 800, 400)

        layout = QVBoxLayout()

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

        self.forgot_password_window.setLayout(layout)
        self.forgot_password_window.show()

    def reset_password(self):
        """Simulate password reset process (for now just a placeholder)"""
        email = self.forgot_email.text().strip()

        if not email:
            self.forgot_password_window.setWindowTitle("Error")
            self.login_feedback.setText("Please enter your email.")
            return

        # Here, you would typically connect to a password reset process, e.g. sending an email.

        self.forgot_password_window.close()
        self.login_feedback.setStyleSheet("font-size: 25px; color: green;")
        self.login_feedback.setText("Password reset instructions sent to your email!")

    def show_signup_window(self):
        """Show signup window"""
        self.signup_window = QWidget()
        self.signup_window.setWindowTitle("Sign Up")
        self.signup_window.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # Background Image for Signup Window
        self.set_background_image("th.jpg")  # Use the same background

        # Signup Form UI with Custom Styling
        name_label = QLabel("User Name: ", self)
        name_label.setStyleSheet("font-size: 30px; color: #333333;")
        layout.addWidget(name_label)

        self.signup_name = QLineEdit(self)
        self.signup_name.setStyleSheet("font-size: 25px; padding: 10px; border-radius: 5px;")
        layout.addWidget(self.signup_name)

        email_label = QLabel("User Email: ", self)
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

        self.signup_window.setLayout(layout)
        self.signup_window.show()

    def signup_database(self):
        """Handle database actions for signup"""
        name = self.signup_name.text()
        email = self.signup_email.text()
        password = self.signup_password.text()

        conn = sqlite3.connect("1.db")
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS test(id INTEGER PRIMARY KEY, name TEXT, email TEXT, password TEXT)")
        cur.execute("INSERT INTO test (name, email, password) VALUES (?, ?, ?)", (name, email, password))

        conn.commit()
        conn.close()

        self.signup_feedback.setText("Account created successfully!")
        # Automatically switch to login window after successful signup
        self.signup_window.close()  # Close the signup window
        self.show_login_window()  # Show the login window

    def show_welcome_frame(self, user_name):
        """Show a welcome frame after successful login"""
        self.welcome_window = QWidget()
        self.welcome_window.setWindowTitle("Welcome")
        self.welcome_window.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # Welcome message with custom style
        welcome_msg = QLabel(f"Welcome, {user_name}!", self)
        welcome_msg.setStyleSheet("font-size: 40px; font-weight: bold; color: #333333;")
        welcome_msg.setAlignment(Qt.AlignCenter)  # Centering the label
        layout.addWidget(welcome_msg)

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

        self.welcome_window.setLayout(layout)
        self.welcome_window.show()

    def logout(self):
        """Logout function - Close the welcome window and return to the main window"""
        self.welcome_window.close()
        self.init_main_ui()  # Reinitialize the main UI with login/signup buttons

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Create the main application window
    window = LoginSignupApp()
    window.show()
    sys.exit(app.exec_())
