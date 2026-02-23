import os
import sounddevice as sd
from scipy.io.wavfile import write

fs = 16000
seconds = 5

# Ask user name
username = input("Enter your name: ").strip()

# Create user folder
user_dir = os.path.join("dataset", username)
os.makedirs(user_dir, exist_ok=True)

# Count existing samples
sample_count = len([f for f in os.listdir(user_dir) if f.endswith(".wav")])
file_path = os.path.join(user_dir, f"sample{sample_count + 1}.wav")

print(f"Speak now, {username}...")
audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
sd.wait()

write(file_path, fs, audio)

print(f"Audio saved at: {file_path}")
