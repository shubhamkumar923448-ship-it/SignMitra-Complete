import os
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping

# 1. Path set karein
DATA_PATH = os.path.join('data', 'raw')
SEQUENCE_LENGTH = 20 # 
EXPECTED_FEATURES = 1560 # 

# 2. Automatically folders (words) detect karein
actions = np.array([name for name in os.listdir(DATA_PATH) if os.path.isdir(os.path.join(DATA_PATH, name))])
print(f"🧠 Found {len(actions)} words for training: {actions}")

label_map = {label:num for num, label in enumerate(actions)}
sequences, labels = [], []

print("📂 Loading data into memory... Please wait.")
corrupted_files = 0

for action in actions:
    for sequence in range(25): 
        try:
           
            res = np.load(os.path.join(DATA_PATH, action, f"{sequence}.npy"), allow_pickle=True)
            
            
            if type(res) is list:
                res = np.array(res)
                
            if res.shape != (SEQUENCE_LENGTH, EXPECTED_FEATURES):
                print(f"⚠️ Skipping corrupted/mismatched file: {action}/{sequence}.npy | Found Shape: {res.shape}")
                corrupted_files += 1
                continue
                
            sequences.append(res)
            labels.append(label_map[action])
            
        except Exception as e:
            pass 

print(f"✅ Filtered Out {corrupted_files} corrupted files.")


X = np.array(sequences)
y = to_categorical(labels).astype(int)

print(f"✅ Data loaded successfully! Shape: {X.shape}")


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)

print("🛠️ Building Neural Network (LSTM)...")
model = Sequential()
model.add(LSTM(64, return_sequences=True, activation='relu', input_shape=(X.shape[1], X.shape[2])))
model.add(LSTM(128, return_sequences=True, activation='relu'))
model.add(LSTM(64, return_sequences=False, activation='relu'))
model.add(Dense(64, activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dense(actions.shape[0], activation='softmax')) 

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['categorical_accuracy'])

# 5. Training Start 
print("🚀 Starting Training... (Grab a coffee ☕)")
early_stop = EarlyStopping(monitor='val_loss', patience=20, restore_best_weights=True)

model.fit(X_train, y_train, epochs=150, batch_size=16, validation_data=(X_test, y_test), callbacks=[early_stop])

# 6. Brain (Model) 
model.save('SignMitra_Model.h5')
np.save('classes.npy', actions)

print("🎉 TRAINING COMPLETE! 🧠")
print("Saved 'SignMitra_Model.h5' and 'classes.npy' in your current folder.")