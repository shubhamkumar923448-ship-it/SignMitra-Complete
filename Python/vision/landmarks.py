import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
import urllib.request
from vision.preprocess import extract_keypoints

# ==========================================
# 1. AUTO-DOWNLOAD AI MODELS 
# ==========================================
def download_model(url, filename):
    model_dir = "vision/models"
    os.makedirs(model_dir, exist_ok=True)
    filepath = os.path.join(model_dir, filename)
    if not os.path.exists(filepath):
        print(f"⏳ Downloading {filename} (Please wait)...")
        urllib.request.urlretrieve(url, filepath)
        print(f"✅ {filename} downloaded!")
    return filepath

hand_model_path = download_model(
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task", 
    "hand_landmarker.task"
)
face_model_path = download_model(
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task", 
    "face_landmarker.task"
)

# ==========================================
# 2. INITIALIZE DETECTORS
# ==========================================
print("🚀 Initializing Premium Neural Detectors (MediaPipe)...")
hand_base_options = python.BaseOptions(model_asset_path=hand_model_path)
hand_options = vision.HandLandmarkerOptions(base_options=hand_base_options, num_hands=2)
hand_detector = vision.HandLandmarker.create_from_options(hand_options)

face_base_options = python.BaseOptions(model_asset_path=face_model_path)
face_options = vision.FaceLandmarkerOptions(base_options=face_base_options)
face_detector = vision.FaceLandmarker.create_from_options(face_options)

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8), 
    (5, 9), (9, 10), (10, 11), (11, 12), (9, 13), (13, 14), (14, 15), 
    (15, 16), (13, 17), (17, 18), (18, 19), (19, 20), (0, 17)
]

def get_hand_orientation(hand_marks, handedness):
    wrist = np.array([hand_marks[0].x, hand_marks[0].y, hand_marks[0].z])
    index_mcp = np.array([hand_marks[5].x, hand_marks[5].y, hand_marks[5].z])
    pinky_mcp = np.array([hand_marks[17].x, hand_marks[17].y, hand_marks[17].z])
    vector1 = index_mcp - wrist
    vector2 = pinky_mcp - wrist
    normal_vector = np.cross(vector1, vector2)
    z_direction = normal_vector[2]
    
    # Mirror me hand labels swap hote hain, logic adjust kiya gaya hai
    is_left_label = handedness[0].category_name == "Left"
    if is_left_label:
        return "BACK OF HAND" if z_direction < 0 else "PALM FRONT"
    else:
        return "BACK OF HAND" if z_direction > 0 else "PALM FRONT"

def draw_styled_landmarks(frame, hand_marks, handedness_info, w, h):
    x_min, y_min = w, h
    x_max, y_max = 0, 0
    orientation = get_hand_orientation(hand_marks, handedness_info)
    box_color = (0, 255, 0) if orientation == "PALM FRONT" else (0, 0, 255)

    for start_idx, end_idx in HAND_CONNECTIONS:
        start_point = (int(hand_marks[start_idx].x * w), int(hand_marks[start_idx].y * h))
        end_point = (int(hand_marks[end_idx].x * w), int(hand_marks[end_idx].y * h))
        cv2.line(frame, start_point, end_point, (150, 0, 150), 4, cv2.LINE_AA)
        cv2.line(frame, start_point, end_point, (255, 100, 255), 2, cv2.LINE_AA)

    for i, mark in enumerate(hand_marks):
        cx, cy = int(mark.x * w), int(mark.y * h)
        x_min, y_min = min(x_min, cx), min(y_min, cy)
        x_max, y_max = max(x_max, cx), max(y_max, cy)

        if i in [4, 8, 12, 16, 20]:
            cv2.circle(frame, (cx, cy), 6, (0, 255, 255), cv2.FILLED, cv2.LINE_AA)
            cv2.circle(frame, (cx, cy), 2, (255, 255, 255), cv2.FILLED, cv2.LINE_AA)
            
    padding = 20
    
    # Kyunki video mirrored hai, MediaPipe left ko right samajhta hai. Humein UI pe correct dikhana hai.
    category = handedness_info[0].category_name
    real_hand_type = "RIGHT" if category == "Left" else "LEFT"
    hud_text = f"{real_hand_type} HAND | {orientation}"
    
    cv2.rectangle(frame, (x_min - padding, y_min - padding - 25), (x_max + padding, y_min - padding), box_color, cv2.FILLED)
    cv2.putText(frame, hud_text, (x_min - padding + 5, y_min - padding - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)

def draw_styled_face(frame, face_marks, w, h):
    x_min, y_min = w, h
    x_max, y_max = 0, 0
    for i, mark in enumerate(face_marks):
        cx, cy = int(mark.x * w), int(mark.y * h)
        x_min, y_min = min(x_min, cx), min(y_min, cy)
        x_max, y_max = max(x_max, cx), max(y_max, cy)
        if i % 3 == 0:
            cv2.circle(frame, (cx, cy), 1, (255, 255, 0), cv2.FILLED, cv2.LINE_AA)

    padding = 15
    L, T, R, B = x_min - padding, y_min - padding, x_max + padding, y_max + padding
    line_len = 20
    color = (0, 200, 255)
    cv2.line(frame, (L, T), (L + line_len, T), color, 2)
    cv2.line(frame, (L, T), (L, T + line_len), color, 2)
    cv2.line(frame, (R, T), (R - line_len, T), color, 2)
    cv2.line(frame, (R, T), (R, T + line_len), color, 2)
    cv2.line(frame, (L, B), (L + line_len, B), color, 2)
    cv2.line(frame, (L, B), (L, B - line_len), color, 2)
    cv2.line(frame, (R, B), (R - line_len, B), color, 2)
    cv2.line(frame, (R, B), (R, B - line_len), color, 2)
    cv2.putText(frame, "FACE MESH: ACTIVE", (L, T - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, cv2.LINE_AA)

# ==========================================
# 3. MAIN EXPORT FUNCTION 
# ==========================================
def process_frame_with_mediapipe(frame):
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    # Run Inference
    hand_result = hand_detector.detect(mp_image)
    face_result = face_detector.detect(mp_image)

    # ✋ STRICT HAND-GATE LOGIC
    hands_visible = bool(hand_result.hand_landmarks)
    
    # Agar haath nahi hain, toh keypoints ko None bhej do taaki AI predict na kare
    if hands_visible:
        keypoints = extract_keypoints(hand_result, face_result)
    else:
        keypoints = None 

    # Dark overlay panel for text at the top
    cv2.rectangle(frame, (0, 0), (w, 50), (0, 0, 0), cv2.FILLED)
    
    # Draw Hands & Update Status
    if hands_visible:
        for idx, hand_marks in enumerate(hand_result.hand_landmarks):
            handedness_info = hand_result.handedness[idx]
            draw_styled_landmarks(frame, hand_marks, handedness_info, w, h)
        cv2.putText(frame, "[ STATUS: EXTRACTING ISL VECTORS ]", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
    else:
        # Agar sirf face hai aur haath nahi (Emotion Mode Ready)
        if face_result.face_landmarks:
            cv2.putText(frame, "[ STATUS: FACE DETECTED (EMOTION ONLY) ]", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
        else:
            cv2.putText(frame, "[ STATUS: SCANNING... ]", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1, cv2.LINE_AA)

    # Draw Face
    if face_result.face_landmarks:
        for face_marks in face_result.face_landmarks:
            draw_styled_face(frame, face_marks, w, h)

    return frame, keypoints