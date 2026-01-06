import numpy as np

class SignalBuffer:
    def __init__(self, window_size, overlap):
        self.window_size = window_size
        self.step = int(window_size * (1 - overlap))
        self.buffer = []

    def push(self, signal):
        self.buffer.extend(signal)
        windows = []

        while len(self.buffer) >= self.window_size:
            win = self.buffer[:self.window_size]
            windows.append(np.array(win))
            self.buffer = self.buffer[self.step:]

        return windows
