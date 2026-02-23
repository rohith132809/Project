import os
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping

from feature_extraction import extract_mfcc

DATASET_DIR = "dataset"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "speaker_model_dl.h5")
LABEL_ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoder.pkl")


def load_dataset():
    if not os.path.exists(DATASET_DIR):
        raise ValueError("Dataset directory not found. Please record some samples first.")

    X, y = [], []

    users = [
        u for u in os.listdir(DATASET_DIR)
        if os.path.isdir(os.path.join(DATASET_DIR, u))
    ]

    if len(users) < 1:
        raise ValueError("Need at least one user to train the model.")

    for user in users:
        user_dir = os.path.join(DATASET_DIR, user)
        for file in os.listdir(user_dir):
            if file.endswith(".wav"):
                file_path = os.path.join(user_dir, file)
                mfcc = extract_mfcc(file_path).astype("float32")  # 1D MFCC vector
                X.append(mfcc)
                y.append(user)

    if not X:
        raise ValueError("No audio samples found to train the model.")

    X = np.array(X, dtype="float32")
    y = np.array(y)

    return X, y


def build_model(input_dim, num_classes):
    model = Sequential()
    model.add(Dense(128, activation="relu", input_shape=(input_dim,)))
    model.add(Dropout(0.3))
    model.add(Dense(64, activation="relu"))
    model.add(Dropout(0.3))
    model.add(Dense(num_classes, activation="softmax"))
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def train_speaker_model_dl():
    X, y = load_dataset()

    # Encode labels
    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    num_classes = len(le.classes_)
    y_onehot = to_categorical(y_enc, num_classes=num_classes)

    print("Training data shape:", X.shape)
    print("Number of users:", num_classes)
    print("Users:", list(le.classes_))

    model = build_model(input_dim=X.shape[1], num_classes=num_classes)

    es = EarlyStopping(
        monitor="val_loss",
        patience=5,
        restore_best_weights=True,
        verbose=1,
    )

    val_split = 0.2 if X.shape[0] > 1 else 0.0

    model.fit(
        X,
        y_onehot,
        validation_split=val_split,
        epochs=100,
        batch_size=4,
        callbacks=[es],
        verbose=1,
    )

    os.makedirs(MODEL_DIR, exist_ok=True)
    model.save(MODEL_PATH)
    joblib.dump(le, LABEL_ENCODER_PATH)

    print("DL model trained successfully ✅")
    return True


if __name__ == "__main__":
    train_speaker_model_dl()
