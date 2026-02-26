# modules/camera.py: Factory для выбора камеры по config

from .hik_camera import HikCamera
from .opencv_camera import OpenCVCamera

def get_camera(config):
    cam_type = config['camera']['type']
    if cam_type == 'hikrobot':
        return HikCamera(config)
    elif cam_type == 'opencv':
        return OpenCVCamera(config)
    else:
        raise ValueError(f"Неизвестный тип камеры: {cam_type}")