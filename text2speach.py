import tkinter as tk
from tkinter import ttk
import pyttsx3
import threading
import queue

class TextToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text to Speech Converter")
        self.root.geometry("500x400")
        
        # Initialize the text-to-speech engine
        self.engine = pyttsx3.init()
        self.speaking = False
        self.stop_event = threading.Event()
        self.speech_queue = queue.Queue()
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Text input label
        self.label = ttk.Label(self.main_frame, text="Enter text to convert to speech:")
        self.label.grid(row=0, column=0, columnspan=3, pady=5)
        
        # Text input area
        self.text_input = tk.Text(self.main_frame, height=10, width=50)
        self.text_input.grid(row=1, column=0, columnspan=3, pady=5)
        
        # Voice selection
        self.voice_label = ttk.Label(self.main_frame, text="Select voice:")
        self.voice_label.grid(row=2, column=0, pady=5)
        
        self.voice_var = tk.StringVar()
        self.voice_dropdown = ttk.Combobox(self.main_frame, textvariable=self.voice_var)
        self.populate_voices()
        self.voice_dropdown.grid(row=2, column=1, pady=5, columnspan=2)
        
        # Speed control
        self.speed_label = ttk.Label(self.main_frame, text="Speech speed:")
        self.speed_label.grid(row=3, column=0, pady=5)
        
        self.speed_scale = ttk.Scale(self.main_frame, from_=50, to=300, orient=tk.HORIZONTAL)
        self.speed_scale.set(175)  # Default speed
        self.speed_scale.grid(row=3, column=1, pady=5, columnspan=2)
        
        # Buttons
        self.speak_button = ttk.Button(self.main_frame, text="Speak", command=self.start_speaking)
        self.speak_button.grid(row=4, column=0, pady=10)
        
        self.stop_button = ttk.Button(self.main_frame, text="Stop", command=self.stop_speaking, state='disabled')
        self.stop_button.grid(row=4, column=1, pady=10)
        
        self.clear_button = ttk.Button(self.main_frame, text="Clear", command=self.clear_text)
        self.clear_button.grid(row=4, column=2, pady=10)
        
        # Make the window resizable
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
        # Start the speech processing thread
        self.speech_thread = threading.Thread(target=self.speech_worker, daemon=True)
        self.speech_thread.start()

    def populate_voices(self):
        voices = self.engine.getProperty('voices')
        voice_names = [voice.name for voice in voices]
        self.voice_dropdown['values'] = voice_names
        if voice_names:
            self.voice_dropdown.set(voice_names[0])

    def speech_worker(self):
        while True:
            try:
                # Wait for text to speak
                text = self.speech_queue.get()
                if text is None:  # Exit signal
                    break
                    
                self.speaking = True
                self.root.after(0, self.update_buttons, True)
                
                # Set voice
                voices = self.engine.getProperty('voices')
                selected_voice = self.voice_var.get()
                for voice in voices:
                    if voice.name == selected_voice:
                        self.engine.setProperty('voice', voice.id)
                        break
                
                # Set speed
                speed = self.speed_scale.get()
                self.engine.setProperty('rate', speed)
                
                # Speak the text
                self.engine.say(text)
                self.engine.runAndWait()
                
                self.speaking = False
                self.root.after(0, self.update_buttons, False)
                self.speech_queue.task_done()
                
            except Exception as e:
                print(f"Error in speech worker: {e}")
                self.speaking = False
                self.root.after(0, self.update_buttons, False)

    def start_speaking(self):
        if not self.speaking:
            text = self.text_input.get("1.0", tk.END).strip()
            if text:
                self.stop_event.clear()
                self.speech_queue.put(text)

    def stop_speaking(self):
        if self.speaking:
            self.engine.stop()
            self.stop_event.set()
            self.speaking = False
            self.update_buttons(False)

    def update_buttons(self, speaking):
        if speaking:
            self.speak_button.configure(state='disabled')
            self.stop_button.configure(state='normal')
        else:
            self.speak_button.configure(state='normal')
            self.stop_button.configure(state='disabled')

    def clear_text(self):
        self.text_input.delete("1.0", tk.END)

    def on_closing(self):
        self.stop_speaking()
        self.speech_queue.put(None)  # Signal to exit the thread
        self.root.destroy()

def main():
    root = tk.Tk()
    app = TextToSpeechApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()