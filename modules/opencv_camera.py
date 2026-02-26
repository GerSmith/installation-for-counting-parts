# modules/opencv_camera.py: Класс для OpenCV-совместимой камеры (веб или файл)

import cv2

class OpenCVCamera:
    def __init__(self, config):
        self.cap = None
        self.source = config['opencv_cam']['source']
        if self.source == 'device':
            self.device_id = config['opencv_cam']['device_id']
        elif self.source == 'file':
            self.file_path = config['opencv_cam']['file_path']
        self.running = False

    def open(self):
        if self.source == 'device':
            self.cap = cv2.VideoCapture(self.device_id)
        elif self.source == 'file':
            self.cap = cv2.VideoCapture(self.file_path)
        if not self.cap.isOpened():
            raise RuntimeError("Не удалось открыть OpenCV-источник")

    def start(self):
        self.running = True

    def read(self):
        if self.cap:
            ret, frame = self.cap.read()
            return ret, frame
        return False, None

    def stop(self):
        self.running = False

    def release(self):
        if self.cap:
            self.cap.release()