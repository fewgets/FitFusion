import google.generativeai as genai
import requests
from typing import Optional, Dict, Any
import json
import requests


# BMI Calculation Classes
class BMI:
    def _init_(self):
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
    def _init_(self, weight_kg, height_cm, age):
        super()._init_()
        self.weight_kg = weight_kg
        self.height_m = height_cm / 100  # Convert height from cm to meters
        self.age = age

    def calculate_bmi(self):
        # BMI formula for Metric system
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
    def _init_(self, api_key: str):
        """Initialize the Fitness AI Assistant with Gemini API"""
        self.api_key = api_key
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)

        # Set up the model
        self.model = genai.GenerativeModel('gemini-pro')

        # Initialize chat with fitness context
        self.chat = self.model.start_chat(history=[])

        # Define the fitness trainer persona
        self.system_prompt = """
        You are FitFusion AI, an expert fitness and nutrition coach with years of experience in personal training 
        and dietary planning. Your role is to:

        1. Provide personalized fitness advice and workout recommendations
        2. Offer nutrition guidance and meal planning suggestions
        3. Help users understand their BMI and health metrics
        4. Motivate users to achieve their fitness goals
        5. Answer health and wellness-related questions
        6. Provide scientific, evidence-based information
        7. Maintain a supportive and encouraging tone

        Important Guidelines:
        - Always prioritize safety and proper form in exercise recommendations
        - Consider user's fitness level and any mentioned health conditions
        - Provide practical, actionable advice
        - Encourage sustainable healthy habits over quick fixes
        - Be supportive and motivational in your responses
        - If asked about medical conditions, remind users to consult healthcare professionals

        Begin by introducing yourself and asking about the user's fitness goals.
        """

        # Initialize the chat with the system prompt
        self.initialize_chat()

    def initialize_chat(self):
        """Initialize the chat with the system prompt"""
        try:
            self.chat = self.model.start_chat(history=[])
            response = self.chat.send_message(self.system_prompt)
            return response.text
        except Exception as e:
            return f"Error initializing chat: {str(e)}"

    def send_query(self, user_query: str) -> str:
        """Send a query to the AI and get response"""
        try:
            response = self.chat.send_message(user_query)
            return response.text
        except Exception as e:
            return f"Error communicating with AI: {str(e)}"


# Main Program
def main():
    # API Keys
    spoonacular_api_key = "e5968cb05a3b42a4845c016350e83f17"
    gemini_api_key = "AIzaSyA1RJISbzG7WJ0T_ZRQIEVj_WWkhiHKml4"

    # Initialize services
    meal_planner = MealPlanner(spoonacular_api_key)
    fitness_ai = FitnessAIAssistant(gemini_api_key)

    print("\n=== Welcome to FitFusion AI - Your Personal Fitness Coach! ===")
    print("I'm here to help you achieve your fitness goals and maintain a healthy lifestyle.")

    while True:
        print("\nMain Menu:")
        print("1. Calculate BMI and Get Meal Plan")
        print("2. Talk to Your Fitness Coach")
        print("3. Exit")

        choice = input("\nEnter your choice (1/2/3): ")

        if choice == "1":
            try:
                weight_kg = float(input("Enter your weight in kg: "))
                height_cm = float(input("Enter your height in cm: "))
                age = int(input("Enter your age: "))

                bmi_metric = BMIMetric(weight_kg, height_cm, age)
                bmi_value = bmi_metric.calculate_bmi()
                bmi_category = bmi_metric.get_bmi_category(bmi_value)

                print(f"\nYour BMI Results:")
                print(f"BMI Value: {bmi_value:.2f}")
                print(f"Category: {bmi_category}")

                # Get AI's interpretation of BMI results
                bmi_query = f"My BMI is {bmi_value:.2f} which falls in the {bmi_category} category. Can you provide some specific advice based on these results?"
                ai_advice = fitness_ai.send_query(bmi_query)
                print("\nAI Coach's Advice:")
                print(ai_advice)

                # Get meal plan
                print("\nGenerating personalized meal plan...")
                meal_plan = meal_planner.get_meal_plan(2000)  # Default 2000 calories
                if meal_plan:
                    print("\nRecommended Meals:")
                    for meal in meal_plan.get("meals", []):
                        print(f"- {meal.get('title', 'No title available')}")
                        print(f"  Recipe: {meal.get('sourceUrl', 'No URL available')}")

            except ValueError:
                print("Please enter valid numbers for weight, height, and age.")

        elif choice == "2":
            print("\nFitness Coach Chat Session")
            print("(Type 'exit' to return to main menu)")

            while True:
                user_input = input("\nYou: ")
                if user_input.lower() == 'exit':
                    break

                response = fitness_ai.send_query(user_input)
                print("\nFitness Coach:", response)

        elif choice == "3":
            print("\nThank you for using FitFusion AI! Stay healthy and keep moving!")
            break

        else:
            print("Invalid choice. Please select 1, 2, or 3.")


if _name_ == "_main_":
main()











import requests


# Define the function to generate a workout plan
def generate_workout_plan():
    print("Welcome to the Workout Planner!")
    print("Please enter the following details to generate your workout plan:")

    # User inputs for the workout plan
    workout_duration = input("Enter workout duration in minutes: ")
    muscle_group = input("Enter the targeted muscle group (e.g., biceps, legs): ")
    workout_location = input("Enter workout location (e.g., gym, home): ")
    available_equipment = input("Enter the equipment available (e.g., dumbbells, pushups): ")

    # Set up the request headers
    myHeaders = {
        "x-apihub-key": "nwiydDeUHWDM0qoglsuUGYEwB43qNAea9yaJaRL-HKhk9SUyzO",
        "x-apihub-host": "AI-Workout-Planner.allthingsdev.co",
        "x-apihub-endpoint": "307137ae-fcd2-4781-bbf6-a9012349598c"
    }

    # Prepare the request URL with parameters
    url = f"https://AI-Workout-Planner.proxy-production.allthingsdev.co/?time={workout_duration}&muscle={muscle_group}&location={workout_location}&equipment={available_equipment}"

    # Send the request to the API
    response = requests.get(url, headers=myHeaders)

    if response.status_code == 200:
        workout_plan = response.json()

        # Display the workout plan details
        print("\nWorkout Plan:")

        # Display warm-up exercises
        if "Warm Up" in workout_plan:
            print("\nWarm Up:")
            for exercise in workout_plan["Warm Up"]:
                url = exercise.get("URL", "URL not provided")  # Get URL if available
                print(f"- {exercise['Exercise']} ({exercise['Time']})")
                print(f"  More info: {url}")

        # Display main exercises
        if "Exercises" in workout_plan:
            print("\nMain Exercises:")
            for exercise in workout_plan["Exercises"]:
                url = exercise.get("URL", "URL not provided")  # Get URL if available
                print(f"- {exercise['Exercise']}: {exercise['Sets']} sets of {exercise['Reps']} reps")
                print(f"  More info: {url}")

        # Display cool-down exercises
        if "Cool Down" in workout_plan:
            print("\nCool Down:")
            for exercise in workout_plan["Cool Down"]:
                url = exercise.get("URL", "URL not provided")  # Get URL if available
                print(f"- {exercise['Exercise']} ({exercise['Time']})")
                print(f"  More info: {url}")

    else:
        print(f"Failed to retrieve workout plan. Status Code: {response.status_code}")
        # Print response details for debugging
        print(f"Response: {response.text}")


# Main program loop
def main():
    while True:
        print("\nWorkout Planner Menu:")
        print("1. Generate Workout Plan")
        print("2. Exit")

        choice = input("Enter your choice (1/2): ")

        if choice == "1":
            generate_workout_plan()  # Generate and display the workout plan
        elif choice == "2":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if _name_ == "_main"
main()







import google.generativeai as genai
import speech_recognition as sr
import webbrowser
from sentence_transformers import SentenceTransformer, util
import re


class FitnessAIAssistant:
    def _init_(self, api_key: str):
        """Initialize the Fitness AI Assistant with Gemini API and semantic filtering."""
        self.api_key = api_key

        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = self.model.start_chat(history=[])

        # Define the fitness trainer persona
        self.system_prompt = """
        You are FitFusion AI, an expert health, fitness, and nutrition assistant. 
        Your role is to only respond to questions or provide suggestions directly related to:

        - Wellness, lifestyle, mental and physical health
        - Nutrition, foods, meal planning, and diets
        - Fitness routines, workouts, and health metrics

        If a query is outside your expertise (e.g., not related to health, fitness, or nutrition), politely respond: 
        "I'm sorry, I can only help with health, fitness, and nutrition-related questions."

        Do not provide responses outside this scope. Ensure all answers are evidence-based, concise, and tailored to the user’s health goals.
        """
        self.initialize_chat()

        # Initialize Semantic Filter
        self.semantic_filter = SemanticFilter()

    def initialize_chat(self):
        """Initialize the chat with the system prompt."""
        try:
            self.chat = self.model.start_chat(history=[])
            response = self.chat.send_message(self.system_prompt)
            print(response.text)
        except Exception as e:
            print(f"Error initializing chat: {str(e)}")

    def send_query(self, user_query: str) -> str:
        """Send a query to the AI if it passes semantic filtering."""
        if self.semantic_filter.is_relevant(user_query):
            try:
                response = self.chat.send_message(user_query)
                print(response.text)
                return response.text
            except Exception as e:
                print(f"Error communicating with AI: {str(e)}")
        else:
            print("I'm sorry, I can only assist with health, fitness, and nutrition-related questions.")
            return "I'm sorry, I can only assist with health, fitness, and nutrition-related questions."

    def listen(self) -> str:
        """Listen for audio input from the user and convert to text."""
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        with microphone as source:
            print("Listening for your question...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            print("You said: ", end="")
            query = recognizer.recognize_google(audio)
            print(query)
            return query
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return "Sorry, I did not understand that."
        except sr.RequestError:
            print("Sorry, I'm having trouble connecting to the speech recognition service.")
            return "Sorry, I'm having trouble connecting to the speech recognition service."

    def open_website(self, command: str):
        """Open websites based on user command."""
        if 'open youtube' in command.lower():
            webbrowser.open("https://www.youtube.com")
            print("Opening YouTube")
        elif 'open google' in command.lower():
            webbrowser.open("https://www.google.com")
            print("Opening Google")
        elif 'search' in command.lower():
            search_query = self.extract_search_query(command)
            if search_query:
                search_url = f"https://www.google.com/search?q={search_query}"
                webbrowser.open(search_url)
                print(f"Searching for {search_query} on Google")
            else:
                print("Sorry, I could not find a search query.")
        else:
            print("Sorry, I cannot recognize that command.")

    def extract_search_query(self, command: str) -> str:
        """Extract search query from the user's command."""
        search_pattern = r"search\s+(.+)"
        match = re.search(search_pattern, command.lower())
        if match:
            return match.group(1)
        return None


class SemanticFilter:
    def _init_(self):
        """Initialize the semantic filter with relevant topics."""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.topics = [
            "health", "fitness", "nutrition", "diet plans", "meal planning",
            "workouts", "stress management", "hydration", "BMI", "body fat percentage",
            "yoga", "HIIT", "cardio", "strength training"
        ]
        self.topic_embeddings = self.model.encode(self.topics, convert_to_tensor=True)

    def is_relevant(self, query: str) -> bool:
        """Check if a query is relevant to health, fitness, or nutrition."""
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        similarity_scores = util.cos_sim(query_embedding, self.topic_embeddings)
        max_similarity = similarity_scores.max().item()
        return max_similarity > 0.6  # Threshold for relevance


# Main Program
def main():
    gemini_api_key = "AIzaSyA1RJISbzG7WJ0T_ZRQIEVj_WWkhiHKml4"  # Replace with your actual API key

    fitness_ai = FitnessAIAssistant(gemini_api_key)

    print("\n=== Welcome to FitFusion AI - Your Personal Fitness Coach! ===")
    print("I'm here to help you achieve your fitness goals and maintain a healthy lifestyle.")

    # Prompt for interaction type only once
    interaction_choice = input("\nWould you like to interact via:\n1. Voice\n2. Text\nEnter 1 or 2: ").strip().lower()

    while True:
        if interaction_choice == "1":
            # If Voice is chosen, listen to user input
            user_input = fitness_ai.listen()

            if user_input.lower() == "exit":
                print("Goodbye! Stay healthy and keep moving!")
                break

            if 'open' in user_input.lower() or 'search' in user_input.lower():
                fitness_ai.open_website(user_input)
            else:
                ai_response = fitness_ai.send_query(user_input)
                print("AI Response: ", ai_response)

        elif interaction_choice == "2":
            # If Text is chosen, take text input
            user_input = input("You can ask questions or give commands: ").strip().lower()

            if user_input == "exit":
                print("Goodbye! Stay healthy and keep moving!")
                break

            if 'open' in user_input or 'search' in user_input:
                fitness_ai.open_website(user_input)
            else:
                ai_response = fitness_ai.send_query(user_input)
                print("AI Response: ", ai_response)

        else:
            print("Invalid choice. Please enter 1 for Voice or 2 for Text.")
            interaction_choice = input("Enter 1 or 2: ").strip().lower()  # Re-prompt for correct choice


if __name__ == "_main_":
    main()