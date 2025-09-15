# 🏋️‍♂️ FitFusion: AI Fitness Tracker with Pose & Diet Intelligence

> An AI-powered desktop app to analyze workout posture, suggest custom meal plans, and track progress — all in one place.

---

## 📌 Project Summary

FitFusion is a desktop-based fitness assistant that combines:

1. **Pose Detection for Form Correction** using Mediapipe + OpenCV

   * 🎥 Tracks keypoints for exercises like push-ups, planks, squats, etc.
   * 🧠 Gives posture-based rep count & real-time correction feedback

2. **AI-Powered Meal Planning**

   * 🍽️ Uses Gemini AI + Spoonacular API
   * 📊 Generates meal plans based on calorie requirements and user preferences

3. **User Management + Progress Tracking**

   * 🔒 Signup/Login with Supabase auth
   * 🔥 Track workout streaks and visualize BMI changes over time

---

## 🧠 How it Works

### 🔍 Pose Detection

* Live camera stream analyzed via Mediapipe Pose model
* Calculates angles & form to verify posture
* Reps auto-counted if pose is correct

### 🧪 AI Meal Suggestions

* Users input preferences (veg/non-veg, allergies, calories)
* Gemini AI + Spoonacular API returns full-day meal plan

### 📈 Progress Features

* BMI calculator & visualizer (via matplotlib)
* Weekly streak history stored in Supabase DB

---

## 🧰 Tech Stack

| Category        | Tools / Frameworks         |
| --------------- | -------------------------- |
| Language        | Python 3.10+               |
| Interface       | PyQt5                      |
| Pose Estimation | OpenCV, Mediapipe          |
| AI Meal Plans   | Gemini AI, Spoonacular API |
| Data Storage    | Supabase (Auth + Database) |
| Charts          | Matplotlib                 |

---

---

## ⚙️ How to Run the Project

### 🔧 1. Clone the Repository

```bash
git clone https://github.com/your-username/FitFusion.git
cd FitFusion
```

### 🔧 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 🔧 3. Set API Keys

* In `Database.py`, enter Supabase credentials
* In `meal_planner.py`, set Gemini + Spoonacular API keys

### 🚀 4. Run the App

```bash
python Login.py
```

---

## ✨ Features

* ✅ Real-time form correction and rep counting
* ✅ Smart meal plans based on dietary needs
* ✅ Visual BMI progress graphs
* ✅ User login, streaks, and habit tracker

---

## 🔮 Future Plans

* 🗣️ Add voice-guided workouts and assistant
* 📱 Launch mobile version (Android/iOS)
* 🌍 Include regional/local meal options
* 🏆 Fitness leaderboard and community challenge system
* ☁️ Cloud sync and backup of progress data

---

## 📩 Contact

👤 **Usama Shahid**
📧 Email: [dev.usamashahid@gmail.com](mailto:dev.usamashahid@gmail.com)

Feel free to reach out for:

* 🤝 Collaboration or code queries
* 💬 Troubleshooting or improvement ideas
* 🎯 Customizations or contributions

---

## 📜 License

This project is for academic and research purposes only. Feel free to fork, reference, and learn - but give credit where due 🙏

---
