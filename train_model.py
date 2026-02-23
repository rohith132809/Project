import os
import joblib
import numpy as np
from sklearn.svm import SVC

from feature_extraction import extract_mfcc

DATASET_DIR = "dataset"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "speaker_model.pkl")


def train_speaker_model():
    if not os.path.exists(DATASET_DIR):
        raise ValueError("Dataset directory not found. Please record some samples first.")

    X, y = [], []

    # Collect user folders
    users = [
        u for u in os.listdir(DATASET_DIR)
        if os.path.isdir(os.path.join(DATASET_DIR, u))
    ]

    # Allow training even with a single user
    if len(users) < 1:
        raise ValueError("Need at least one user to train the model.")

    for user in users:
        user_dir = os.path.join(DATASET_DIR, user)
        for file in os.listdir(user_dir):
            if file.endswith(".wav"):
                file_path = os.path.join(user_dir, file)
                mfcc = extract_mfcc(file_path)  # 1D MFCC feature vector
                X.append(mfcc)
                y.append(user)

    if not X:
        raise ValueError("No audio samples found to train the model.")

    X = np.array(X)
    y = np.array(y)

    print("Training data shape:", X.shape)
    print("Number of users:", len(set(y)))
    print("Users:", list(set(y)))

    model = SVC(kernel="linear", probability=True)
    model.fit(X, y)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print("Model trained successfully ✅")
    return True


if __name__ == "__main__":
    train_speaker_model()
