import tkinter as tk
from tkinter import ttk

class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Chat")
        self.geometry("600x600")
        self.configure(bg="#282C34")  # Theme background color

        # Chat history container
        self.chat_frame = ttk.Frame(self, padding="10")
        self.chat_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollable text widget for chat history
        self.chat_canvas = tk.Canvas(self.chat_frame, bg="#282C34", bd=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.chat_frame, orient="vertical", command=self.chat_canvas.yview)
        self.chat_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.chat_container = ttk.Frame(self.chat_canvas)
        self.chat_canvas.create_window((0, 0), window=self.chat_container, anchor="nw")

        self.chat_container.bind("<Configure>", self._on_frame_configure)

        # Input field and send button
        self.input_frame = ttk.Frame(self, padding="5")
        self.input_frame.pack(fill=tk.X)

        self.input_field = ttk.Entry(self.input_frame, width=80, font=("Arial", 12))
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.send_button = ttk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)

        # Initialize a placeholder for messages
        self.messages = []

    def send_message(self):
        user_message = self.input_field.get()
        if user_message.strip():
            self.add_message(user_message, user=True)
            self.input_field.delete(0, tk.END)

            # Simulate AI response
            self.after(1000, lambda: self.add_message(f"AI response to: {user_message}", user=False))

    def add_message(self, message, user=True):
        # Create a bubble frame
        bubble_frame = ttk.Frame(self.chat_container, padding="10", style="UserBubble.TFrame" if user else "AIBubble.TFrame")
        bubble_frame.pack(anchor="e" if user else "w", pady=(5, 10), padx=(10, 30) if user else (30, 10))

        # Bubble label
        label = ttk.Label(bubble_frame, text=message, wraplength=400, justify="left",
                          style="UserBubble.TLabel" if user else "AIBubble.TLabel")
        label.pack()

        # Scroll down to the latest message
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1)

    def _on_frame_configure(self, event=None):
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))

# Styling
def setup_styles():
    style = ttk.Style()
    style.theme_use("clam")

    # User bubble styling
    style.configure("UserBubble.TFrame", background="#4CAF50", relief="solid", borderwidth=1)
    style.configure("UserBubble.TLabel", background="#4CAF50", foreground="white", font=("Arial", 12), padding=5)

    # AI bubble styling
    style.configure("AIBubble.TFrame", background="#333333", relief="solid", borderwidth=1)
    style.configure("AIBubble.TLabel", background="#333333", foreground="white", font=("Arial", 12), padding=5)

if __name__ == "__main__":
    setup_styles()
    app = ChatApp()
    app.mainloop()
