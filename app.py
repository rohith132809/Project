# ================= WINDOWS + HF FIX =================
import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

# ===================================================
from io import BytesIO
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from flask import Flask, render_template, request, session, redirect, url_for, abort, send_file
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet

import torch
import torchaudio
import webrtcvad
from speechbrain.pretrained import EncoderClassifier

# ================= APP CONFIG =================

app = Flask(__name__)
app.secret_key = "change_this_secret_key"

DATASET_DIR = "dataset"
EMB_DIR = "embeddings"
PROTECTED_DIR = "protected_media"

FS = 16000
SECONDS = 6
MIN_SAMPLES = 5

# ================= ENCRYPTION =================

def load_file_key():
    if not os.path.exists("filekey.key"):
        key = Fernet.generate_key()
        with open("filekey.key", "wb") as f:
            f.write(key)
    else:
        with open("filekey.key", "rb") as f:
            key = f.read()
    return Fernet(key)

fernet = load_file_key()

# ================= MODEL =================

print("Loading ECAPA-TDNN model...")
classifier = EncoderClassifier.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    run_opts={"device": "cpu"}
)

# ================= VAD =================

vad = webrtcvad.Vad(2)

def remove_silence(signal, sample_rate):
    signal = signal.squeeze().numpy()
    frame_ms = 30
    frame_size = int(sample_rate * frame_ms / 1000)

    voiced = []
    for i in range(0, len(signal) - frame_size, frame_size):
        frame = signal[i:i + frame_size]
        pcm16 = (frame * 32768).astype(np.int16).tobytes()
        if vad.is_speech(pcm16, sample_rate):
            voiced.append(frame)

    if not voiced:
        raise ValueError("No speech detected")

    return torch.tensor(np.concatenate(voiced)).unsqueeze(0)

# ================= AUDIO =================

def record_voice(filename):
    print("Recording... Speak clearly")

    audio = sd.rec(
        int(SECONDS * FS),
        samplerate=FS,
        channels=1,
        dtype="float32"
    )
    sd.wait()

    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val

    write(filename, FS, audio)

# ================= EMBEDDINGS =================

def l2_normalize(x):
    return x / np.linalg.norm(x)

def extract_embedding(wav_path):
    signal, fs = torchaudio.load(wav_path)

    if signal.shape[0] > 1:
        signal = torch.mean(signal, dim=0, keepdim=True)

    signal = remove_silence(signal, fs)

    if torch.mean(signal ** 2) < 1e-5:
        raise ValueError("Weak speech")

    with torch.no_grad():
        emb = classifier.encode_batch(signal)

    emb = emb.squeeze().cpu().numpy()
    return l2_normalize(emb)

def cosine_sim(a, b):
    return float(np.dot(a, b))

# ================= SCORE CALIBRATION =================

def calibrated_score(raw_score):
    if raw_score < 0.45:
        return raw_score * 0.5
    elif raw_score < 0.65:
        return 0.6 + (raw_score - 0.45) * 0.5
    else:
        return 0.85 + (raw_score - 0.65) * 0.5

# ================= ENROLL =================

def enroll_user(username, user_dir):
    wavs = [
        os.path.join(user_dir, f)
        for f in os.listdir(user_dir)
        if f.endswith(".wav")
    ]

    embeddings = []
    for w in wavs:
        try:
            embeddings.append(extract_embedding(w))
        except:
            pass

    if len(embeddings) < MIN_SAMPLES:
        raise ValueError("Need at least 5 clean voice samples")

    emb_stack = np.vstack(embeddings)
    mean_emb = l2_normalize(np.mean(emb_stack, axis=0))
    std_emb = np.std(emb_stack, axis=0)

    os.makedirs(EMB_DIR, exist_ok=True)
    np.save(os.path.join(EMB_DIR, f"{username}_mean.npy"), mean_emb)
    np.save(os.path.join(EMB_DIR, f"{username}_std.npy"), std_emb)

# ================= VERIFY =================

def verify_user(username, wav_file):
    try:
        test_emb = extract_embedding(wav_file)
    except:
        return False, 0.0

    mean_path = os.path.join(EMB_DIR, f"{username}_mean.npy")
    std_path = os.path.join(EMB_DIR, f"{username}_std.npy")

    if not os.path.exists(mean_path):
        return False, 0.0

    ref_mean = np.load(mean_path)
    ref_std = np.load(std_path)

    test_emb = test_emb - ref_std * 0.1
    test_emb = l2_normalize(test_emb)

    raw_score = cosine_sim(test_emb, ref_mean)
    confidence = calibrated_score(raw_score)

    if confidence >= 0.85:
        return True, confidence
    elif confidence >= 0.70:
        return True, confidence
    else:
        return False, confidence

# ================= ROUTES =================

@app.route("/", methods=["GET", "POST"])
def authenticate():
    status = None
    extra = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        action = request.form.get("action")

        if not username:
            return render_template("index.html", status="Invalid username")

        user_dir = os.path.join(DATASET_DIR, username)
        os.makedirs(user_dir, exist_ok=True)

        if action == "signup":
            count = len([f for f in os.listdir(user_dir) if f.endswith(".wav")])
            wav_path = os.path.join(user_dir, f"sample{count + 1}.wav")
            record_voice(wav_path)

            if count + 1 >= MIN_SAMPLES:
                try:
                    enroll_user(username, user_dir)
                    status = "Enrollment successful. You can sign in."
                except Exception as e:
                    status = str(e)
            else:
                status = "Sample recorded. Record 5 samples."

            extra = f"Samples recorded: {count + 1}"

        elif action == "signin":
            temp = "temp.wav"
            record_voice(temp)

            ok, score = verify_user(username, temp)

            if ok:
                session["user"] = username
                return redirect(url_for("hidden_area"))
            else:
                status = f"Authentication failed (Confidence: {score:.3f})"

    return render_template("index.html", status=status, extra=extra)

@app.route("/hidden")
def hidden_area():
    if "user" not in session:
        return redirect(url_for("authenticate"))

    username = session["user"]
    return render_template("hidden.html", username=username)

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user" not in session:
        return redirect(url_for("authenticate"))

    message = None
    user_dir = os.path.join(PROTECTED_DIR, session["user"])
    os.makedirs(user_dir, exist_ok=True)

    if request.method == "POST":
        file = request.files.get("file")
        if file:
            encrypted = fernet.encrypt(file.read())
            with open(os.path.join(user_dir, secure_filename(file.filename)), "wb") as f:
                f.write(encrypted)
            message = "File uploaded securely"

    return render_template(
        "upload.html",
        message=message,
        files=os.listdir(user_dir)
    )

@app.route("/media/<filename>")
def media(filename):
    if "user" not in session:
        abort(403)

    path = os.path.join(PROTECTED_DIR, session["user"], filename)
    with open(path, "rb") as f:
        decrypted = fernet.decrypt(f.read())

    return send_file(BytesIO(decrypted), download_name=filename)

@app.route("/delete/<filename>")
def delete_file(filename):
    if "user" not in session:
        abort(403)

    user_dir = os.path.join(PROTECTED_DIR, session["user"])
    path = os.path.join(user_dir, filename)

    if os.path.exists(path):
        os.remove(path)

    return redirect(url_for("upload"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("authenticate"))

# ================= MAIN =================

if __name__ == "__main__":
    os.makedirs(DATASET_DIR, exist_ok=True)
    os.makedirs(EMB_DIR, exist_ok=True)
    os.makedirs(PROTECTED_DIR, exist_ok=True)
    app.run(debug=True)
