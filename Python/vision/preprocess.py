import numpy as np

def extract_keypoints(hand_result, face_result):
    """
    Extracts x, y, z coordinates from MediaPipe results and flattens them into a single 1D array.
    """
    # 1. FACE: 478 landmarks * 3 (x,y,z) = 1434 values
    if face_result and face_result.face_landmarks:
        face = np.array([[res.x, res.y, res.z] for res in face_result.face_landmarks[0]]).flatten()
    else:
        face = np.zeros(478 * 3)

    # 2. HANDS
    lh = np.zeros(21 * 3)
    rh = np.zeros(21 * 3)
    
    if hand_result and hand_result.hand_landmarks:
        for idx, hand_marks in enumerate(hand_result.hand_landmarks):
            handedness = hand_result.handedness[idx][0].category_name
            hand_array = np.array([[res.x, res.y, res.z] for res in hand_marks]).flatten()
            if handedness == 'Left':
                lh = hand_array
            elif handedness == 'Right':
                rh = hand_array

    # Total = 1560 values
    return np.concatenate([face, lh, rh])