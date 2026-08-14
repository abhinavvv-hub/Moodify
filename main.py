import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["TF_FORCE_GPU_ALLOW_GROWTH"] = "false"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import cv2
import customtkinter as ctk
from PIL import Image
from datetime import datetime
from deepface import DeepFace
import threading
import webbrowser as wb

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

mood_playlists = {
    "happy": "https://open.spotify.com/playlist/37i9dQZF1DWTwbZHrJRIgD",
    "sad": "https://open.spotify.com/playlist/37i9dQZF1DX7qK8ma5wgG1",
    "neutral": "https://open.spotify.com/playlist/37i9dQZF1DX4WYpdgoIcn6",
    "angry": "https://open.spotify.com/playlist/40HL5KI6iVgzwfnmjFDFfX",
    "fear": "https://open.spotify.com/playlist/37i9dQZF1DWTvNyxOwkztu",
    "surprise": "https://open.spotify.com/playlist/5yTCoKhdenIVoCmaoFAFZ2",
    "disgust": "https://open.spotify.com/playlist/37i9dQZF1DX3AQIJcCkXwU"
}


class Moodify(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Mood Music Player")
        self.geometry("700x650")
        self.resizable(False, False)

        self.cap = cv2.VideoCapture(0)
        self.current_frame = None
        self.analysis_running = False
        self.detected_mood = None
        self.analysis_error = None

        self.title_label = ctk.CTkLabel(self, text="Mood Music Player", font=("Helvetica", 24, "bold"))
        self.title_label.pack(pady=(20, 10))

        self.video_label = ctk.CTkLabel(self, text="")
        self.video_label.pack(pady=10)

        self.mood_label = ctk.CTkLabel(self, text="Detected Mood: Waiting...", font=("Helvetica", 16))
        self.mood_label.pack(pady=10)

        self.scan_button = ctk.CTkButton(self, text="Scan Mood & Play Music", font=("Helvetica", 14, "bold"), height=40, command=self.scan_mood)
        self.scan_button.pack(pady=15)

        self.update_frame()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_frame(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()

            if ret:
                frame = cv2.flip(frame, 1)
                self.current_frame = frame.copy()

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_frame)

                self.current_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(560, 420))
                self.video_label.configure(image=self.current_image)

        if self.detected_mood is not None:
            self.mood_label.configure(text=f"Detected Mood: {self.detected_mood.capitalize()}")
            self.detected_mood = None
            self.analysis_running = False
            self.scan_button.configure(state="normal", text="Scan Mood & Play Music")

        if self.analysis_error is not None:
            self.mood_label.configure(text="Detected Mood: Analysis Failed")
            self.analysis_error = None
            self.analysis_running = False
            self.scan_button.configure(state="normal", text="Scan Mood & Play Music")

        self.after(15, self.update_frame)

    def scan_mood(self):
        if self.current_frame is None:
            self.mood_label.configure(text="Detected Mood: Camera Not Ready")
            return

        if self.analysis_running:
            return

        self.analysis_running = True
        self.detected_mood = None
        self.analysis_error = None

        self.scan_button.configure(state="disabled", text="Analyzing...")
        self.mood_label.configure(text="Detected Mood: Analyzing...")

        print(f"Scan button clicked at {datetime.now().strftime('%H:%M:%S')}!")

        frame = self.current_frame.copy()

        analysis_thread = threading.Thread(target=self.analyze_mood, args=(frame,), daemon=True)
        analysis_thread.start()

    def analyze_mood(self, frame):
        try:
            print("Starting DeepFace analysis...")

            result = DeepFace.analyze(img_path=frame, actions=["emotion"], detector_backend="opencv", enforce_detection=False)

            print("DeepFace analysis completed")

            if isinstance(result, list):
                result = result[0]

            dominant = result["dominant_emotion"]

            print(f"Detected: {dominant}")

            self.detected_mood = dominant

            wb.open(mood_playlists[dominant])

        except Exception as e:
            print(f"Error During Analysis: {e}")
            self.analysis_error = str(e)

    def on_close(self):
        if self.cap.isOpened():
            self.cap.release()

        self.destroy()


if __name__ == "__main__":
    app = Moodify()
    app.mainloop()
