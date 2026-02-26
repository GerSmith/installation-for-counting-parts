# gui/threads/video_thread.py
from PySide6.QtCore import QThread, Signal
import numpy as np


class VideoThread(QThread):
    """Поток для захвата видео."""
    
    change_pixmap_signal = Signal(np.ndarray)
    
    def __init__(self, camera):
        super().__init__()
        self.camera = camera
        self.running = True
    
    def run(self):
        """Запуск потока."""
        self.camera.open()
        self.camera.start()
        
        while self.running:
            ret, frame = self.camera.read()
            if ret:
                self.change_pixmap_signal.emit(frame)
        
        self.camera.stop()
        self.camera.release()
    
    def stop(self):
        """Остановка потока."""
        self.running = False
        self.wait()