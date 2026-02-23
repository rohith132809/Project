import joblib
from feature_extraction import extract_mfcc

model = joblib.load("models/speaker_model.pkl")
feature = extract_mfcc("test.wav")

prediction = model.predict([feature])
print("Authenticated User:", prediction[0])
