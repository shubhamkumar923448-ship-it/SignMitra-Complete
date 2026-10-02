import cv2
import numpy as np
import os
import time
from vision.landmarks import process_frame_with_mediapipe

DATA_PATH = os.path.join('data', 'raw')
# for words (overwriteable)
actions = np.array(['Math']) 

no_sequences = 25
sequence_length = 20

for action in actions:
    os.makedirs(os.path.join(DATA_PATH, action), exist_ok=True)

cap = cv2.VideoCapture(0)

for action in actions:
    # Word shuru hone se pehle lamba break
    print(f"\n👉 GET READY FOR: {action.upper()}")
    cv2.waitKey(2000) 

    for sequence in range(no_sequences):
    
        cv2.waitKey(2000) 

        sequence_data = []
        frame_num = 0  #

        # 
        while frame_num < sequence_length:
            ret, frame = cap.read()
            if not ret: break

            frame = cv2.flip(frame, 1)    # // Flip camera to real mirror
            processed_frame, keypoints = process_frame_with_mediapipe(frame)
            
            #
            if keypoints is None:
                cv2.putText(processed_frame, 'WAITING FOR HANDS...', (120,200), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3, cv2.LINE_AA)
                cv2.imshow('SignMitra Data Collector', processed_frame)
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
                continue 
            
            if frame_num == 0:
                cv2.putText(processed_frame, f'GET READY FOR VIDEO {sequence+1}/30...', (50,200), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3, cv2.LINE_AA)
                cv2.imshow('SignMitra Data Collector', processed_frame)
                cv2.waitKey(1500) 
                
                cv2.putText(processed_frame, 'START SIGNING NOW!', (120,200), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 4, cv2.LINE_AA)
                cv2.imshow('SignMitra Data Collector', processed_frame)
                cv2.waitKey(500)
            else: 
                cv2.putText(processed_frame, f'Recording: {action} | Video: {sequence+1}/{no_sequences}', (15,20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2, cv2.LINE_AA)
                cv2.imshow('SignMitra Data Collector', processed_frame)
            
            sequence_data.append(keypoints)
            frame_num += 1 # 
            
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
            
        npy_path = os.path.join(DATA_PATH, action, str(sequence))
        np.save(npy_path, sequence_data)

cap.release()
cv2.destroyAllWindows()