FitFusion: Fitness Tracker and Assistant
FitFusion is an advanced fitness tracker application that combines AI-powered features with user-friendly interfaces to help users achieve their health and fitness goals. It provides functionalities for logging in, signing up, tracking workouts, managing BMI, and receiving AI-assisted meal and workout plans.

Features
1. User Management
Sign-Up: Register users with email verification and initialize BMI and streak data.
Login: Secure authentication using Supabase integration.
2. Fitness Tools
Pose Tracker: Real-time feedback on exercises like biceps curls, squats, push-ups, and planks using Mediapipe and OpenCV.
Workout Planner: Suggests exercises based on muscle groups and goals using external APIs.
BMI Management: Calculate and update BMI with personalized insights.
3. AI Assistance
Meal Planning: AI-generated meal plans based on dietary preferences and calorie goals.
Fitness Assistant: Chat-based fitness and health guidance using Gemini AI.
4. Progress Tracking
Streak Management: Tracks daily streaks to encourage consistency.
Visual Feedback: Displays workout progress and BMI history graphically.
Installation
Prerequisites
Python 3.8+
Pip
Setup Steps
Clone this repository:

bash
Copy code
git clone https://github.com/your-username/fitfusion.git
cd fitfusion
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Configure API Keys:

Update Database.py with your Supabase credentials.
Update Login.py with your Gemini AI and Spoonacular API keys.
Run the application:

bash
Copy code
python Login.py
Technologies Used
Frontend: PyQt5
Backend: Python, Supabase, Mediapipe
AI Models: Gemini AI, Spoonacular API
Visualization: Matplotlib
Camera Integration: OpenCV
How It Works
Pose Tracker
Utilizes Mediapipe's Pose solution to analyze body movements and provide real-time feedback on exercise form. Supports:

Biceps Curls: Counts reps and analyzes arm angles.
Squats: Evaluates knee angles and depth.
Push-Ups: Tracks repetitions and posture.
Planks: Measures body alignment.
BMI Tracking
Captures user data such as height, weight, and age to calculate BMI. Stores historical data for progress visualization.

AI-Powered Assistance
Meal and workout plans are tailored to user preferences and goals.
AI chatbot answers fitness-related questions and provides guidance.
Contributing
We welcome contributions! Feel free to submit issues or pull requests to improve the application.

Steps to Contribute
Fork the repository.
Create a new feature branch:
bash
Copy code
git checkout -b feature-name
Commit changes and push to your fork:
bash
Copy code
git push origin feature-name
Submit a pull request.
License
This project is licensed under the MIT License.

Acknowledgments
Mediapipe and OpenCV for pose tracking.
Supabase for user authentication and database management.
Gemini AI and Spoonacular API for intelligent suggestions.
