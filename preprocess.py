import librosa
import numpy as np

def preprocess_audio(file):
    audio, sr = librosa.load(file, sr=16000)
    audio, _ = librosa.effects.trim(audio)
    audio = librosa.util.normalize(audio)
    return audio, sr
