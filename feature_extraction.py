import librosa
import numpy as np
from preprocess import preprocess_audio

def extract_mfcc(file):
    audio, sr = preprocess_audio(file)
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
    return np.mean(mfcc.T, axis=0)
