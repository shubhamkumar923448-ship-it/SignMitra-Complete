import os
import numpy as np
from tensorflow.keras.models import load_model

class SignLanguageClassifier:
    def __init__(self):
        print("🧠 Loading Trained SignMitra AI Model...")
        
        try:
            # 🔴 FIX: Dynamically path nikalna taaki file hamesha mil jaye
            current_dir = os.path.dirname(os.path.abspath(__file__)) # Ye vision folder hai
            parent_dir = os.path.dirname(current_dir) # Ye main Python folder hai
            
            model_path = os.path.join(parent_dir, 'SignMitra_Model.h5')
            classes_path = os.path.join(parent_dir, 'classes.npy')
            
            print(f"🔍 Searching for model at: {model_path}")
            
            self.model = load_model(model_path)
            self.actions = np.load(classes_path)
            print(f"✅ Model Loaded Successfully! Recognized Words: {self.actions}")
            
        except Exception as e:
            print(f"❌ Model Load Error: {e}")
            self.model = None
            self.actions = []

    def predict_sign(self, sequence_data):
        if self.model is None or sequence_data is None:
            return "..."
            
        try:
            input_data = np.array(sequence_data)
            
            if len(input_data.shape) == 2:
                input_data = np.expand_dims(input_data, axis=0)
                
            predictions = self.model.predict(input_data, verbose=0)[0]
            best_match_index = np.argmax(predictions)
            confidence = predictions[best_match_index]
            
            predicted_word = self.actions[best_match_index]
            
            # 🔴 FIX: Terminal par AI ka dimaag print karo
            print(f"🤖 AI Guessed: '{predicted_word}' (Confidence: {confidence*100:.2f}%)")
            
            # 45% se upar ho toh LLM ke liye aage bhejo
            if confidence > 0.45:
                return predicted_word
            else:
                return "..."
                
        except Exception as e:
            print(f"Prediction Error: {e}")
            return "..."