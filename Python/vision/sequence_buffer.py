import numpy as np
from collections import deque

class SignSequenceBuffer:
    def __init__(self, sequence_length=30):
        """
        sequence_length: Number of frames to hold before making a prediction.
        30 frames at 15FPS = ~2 seconds of motion.
        """
        self.sequence_length = sequence_length
        # deque automatically removes the oldest frame when a new one is added if maxlen is reached
        self.buffer = deque(maxlen=sequence_length)
        
    def add_frame(self, keypoints):
        """Adds a new extracted frame to the buffer."""
        self.buffer.append(keypoints)
        
    def is_ready(self):
        """Checks if we have collected enough frames to make a prediction."""
        return len(self.buffer) == self.sequence_length
        
    def get_sequence(self):
        """
        Returns the sequence as a NumPy array ready for the LSTM/AI model.
        Shape will be (1, 30, 1560) -> (Batch, Time Steps, Features)
        """
        if self.is_ready():
            return np.expand_dims(np.array(self.buffer), axis=0)
        return None
        
    def clear(self):
        """Clears the memory (e.g., after a successful translation or a long pause)."""
        self.buffer.clear()