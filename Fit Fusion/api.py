import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import webbrowser
import re
import threading
import queue

class FitnessAIAssistant:
    def __init__(self, api_key: str):
        """Initialize the Fitness AI Assistant with Gemini API"""
        # Initialization code here

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

        # Initialize Text-to-Speech engine
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Adjust speech rate

        # Initialize speech task queue
        self.speech_queue = queue.Queue()

        # Start a thread to process the speech tasks (text-to-speech output)
        self.speech_thread = threading.Thread(target=self.process_speech, daemon=True)
        self.speech_thread.start()

        # Initialize the chat with the system prompt
        self.initialize_chat()

    def initialize_chat(self):
        """Initialize the chat with the system prompt"""
        try:
            self.chat = self.model.start_chat(history=[])
            response = self.chat.send_message(self.system_prompt)
            self.enqueue_speech(response.text)  # Add both text and speech
            print(response.text)  # Print response in console
        except Exception as e:
            self.enqueue_speech(f"Error initializing chat: {str(e)}")

    def send_query(self, user_query: str) -> str:
        """Send a query to the AI and get response"""
        try:
            response = self.chat.send_message(user_query)
            self.enqueue_speech(response.text)  # Add both text and speech
            print(response.text)  # Print response in console
            return response.text
        except Exception as e:
            self.enqueue_speech(f"Error communicating with AI: {str(e)}")

    def enqueue_speech(self, text: str):
        """Add speech text to the queue"""
        self.speech_queue.put(text)

    def process_speech(self):
        """Process speech tasks from the queue"""
        while True:
            text = self.speech_queue.get()
            if text:
                self.speak(text)
            self.speech_queue.task_done()

    def speak(self, text: str):
        """Speak the provided text"""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def listen(self) -> str:
        """Listen for audio input from the user and convert to text"""
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        with microphone as source:
            print("Listening for your question...")
            recognizer.adjust_for_ambient_noise(source)  # To handle background noise
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
        """Open websites based on user command"""
        if 'open youtube' in command.lower():
            webbrowser.open("https://www.youtube.com")
            self.enqueue_speech("Opening YouTube")
        elif 'open google' in command.lower():
            webbrowser.open("https://www.google.com")
            self.enqueue_speech("Opening Google")
        elif 'search' in command.lower():
            search_query = self.extract_search_query(command)
            if search_query:
                search_url = f"https://www.google.com/search?q={search_query}"
                webbrowser.open(search_url)
                self.enqueue_speech(f"Searching for {search_query} on Google")
            else:
                self.enqueue_speech("Sorry, I could not find a search query.")
        else:
            self.enqueue_speech("Sorry, I cannot recognize that command.")

    def extract_search_query(self, command: str) -> str:
        """Extract search query from the user's command"""
        search_pattern = r"search\s+(.+)"
        match = re.search(search_pattern, command.lower())
        if match:
            return match.group(1)
        return None

# Main Program: Example of interaction with voice input and output
def main():
    gemini_api_key = "AIzaSyA1RJISbzG7WJ0T_ZRQIEVj_WWkhiHKml4"

    # Initialize the Fitness AI assistant
    fitness_ai = FitnessAIAssistant(gemini_api_key)

    print("\n=== Welcome to FitFusion AI - Your Personal Fitness Coach! ===")
    print("I'm here to help you achieve your fitness goals and maintain a healthy lifestyle.")
    fitness_ai.enqueue_speech("Hello, I am your personal fitness assistant. How would you like to interact with me?")

    # Ask the user for their interaction choice (voice or text) only once
    if not hasattr(fitness_ai, 'interaction_choice'):
        print("\nWould you like to interact via:")
        print("1. Voice")
        print("2. Text")
        fitness_ai.interaction_choice = input("Enter 1 or 2: ").strip().lower()

    while True:
        # If user chooses voice, listen for commands
        if fitness_ai.interaction_choice == "1":
            user_input = fitness_ai.listen()

            if user_input.lower() == "exit":
                fitness_ai.enqueue_speech("Goodbye! Stay healthy and keep moving!")
                break

            # Check if the user command includes a website or search query
            if 'open' in user_input.lower() or 'search' in user_input.lower():
                fitness_ai.open_website(user_input)
            else:
                # Send the query to the AI and get the response
                ai_response = fitness_ai.send_query(user_input)
                print("AI Response: ", ai_response)

        # If user chooses text, handle text-based interaction
        elif fitness_ai.interaction_choice == "2":
            user_input = input("You can ask questions or give commands: ").strip().lower()

            if user_input == "exit":
                fitness_ai.enqueue_speech("Goodbye! Stay healthy and keep moving!")
                break

            # Check if the user command includes a website or search query
            if 'open' in user_input or 'search' in user_input:
                fitness_ai.open_website(user_input)
            else:
                # Send the query to the AI and get the response
                ai_response = fitness_ai.send_query(user_input)
                print("AI Response: ", ai_response)

            # Allow switching between text and voice modes
            if 'switch to voice' in user_input:
                fitness_ai.interaction_choice = "1"
                fitness_ai.enqueue_speech("Switching to voice mode.")
            elif 'switch to text' in user_input:
                fitness_ai.interaction_choice = "2"
                fitness_ai.enqueue_speech("Switching to text mode.")
if __name__ == "__main__":
    main()
