# modules/hik_camera.py
"""
Класс для работы с промышленной камерой Hikrobot (USB3 Vision)
Поддерживаемые форматы: Mono8, BayerRG8
"""

import logging
import time
import ctypes
import numpy as np
import cv2

from .MvCameraControl_class import *
from .PixelType_header import PixelType_Gvsp_Mono8, PixelType_Gvsp_BayerRG8
from .MvErrorDefine_const import MV_OK, MV_E_GC_TIMEOUT

logger = logging.getLogger(__name__)


class HikCamera:
    """
    Класс управления камерой Hikrobot MV-CSxxx-10UC-PRO.

    Основные возможности:
    - открытие/закрытие камеры
    - настройка разрешения и формата пикселей
    - захват кадров в отдельном потоке
    - расчёт и отображение FPS на кадре
    """

    SUPPORTED_FORMATS = {
        "Mono8": PixelType_Gvsp_Mono8,
        "BayerRG8": PixelType_Gvsp_BayerRG8,
    }

    def __init__(self, config):
        """Инициализация параметров камеры из конфигурации."""
        self.cam = None
        self.width = config["hikrobot_cam"]["width"]
        self.height = config["hikrobot_cam"]["height"]
        self.pixel_format_name = config["hikrobot_cam"]["pixel_format"]

        self.running = False
        self.last_frame_time = 0.0
        self.frame_count = 0
        self.fps = 0.0

        # Проверка допустимости выбранного формата
        if self.pixel_format_name not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Неподдерживаемый формат: {self.pixel_format_name}. "
                f"Доступны: {list(self.SUPPORTED_FORMATS.keys())}"
            )
        self.pixel_format_value = self.SUPPORTED_FORMATS[self.pixel_format_name]

    def open(self):
        """Открытие камеры и применение базовых настроек."""
        try:
            self.cam = MvCamera()
            device_list = MV_CC_DEVICE_INFO_LIST()
            ret = MvCamera.MV_CC_EnumDevices(MV_USB_DEVICE, device_list)

            if ret != MV_OK or device_list.nDeviceNum == 0:
                raise RuntimeError(f"Не найдено USB3-камер Hikrobot (ret = {ret:#x})")

            # Используем первую найденную камеру
            dev_info = ctypes.cast(
                device_list.pDeviceInfo[0], ctypes.POINTER(MV_CC_DEVICE_INFO)
            ).contents
            ret = self.cam.MV_CC_CreateHandle(dev_info)
            if ret != MV_OK:
                raise RuntimeError(f"MV_CC_CreateHandle failed (ret = {ret:#x})")

            ret = self.cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
            if ret != MV_OK:
                raise RuntimeError(f"MV_CC_OpenDevice failed (ret = {ret:#x})")

            self._set_resolution()
            self._set_pixel_format()

            logger.info(
                f"Камера открыта: {self.width}x{self.height}, формат {self.pixel_format_name}"
            )

        except Exception as e:
            self.release()
            logger.exception("Ошибка при открытии камеры")
            raise

    def _set_resolution(self):
        """Установка ширины и высоты кадра (с предупреждением при неудаче)."""
        ret_w = self.cam.MV_CC_SetIntValue("Width", self.width)
        ret_h = self.cam.MV_CC_SetIntValue("Height", self.height)
        if ret_w != MV_OK:
            logger.warning(f"Не удалось установить Width = {self.width} (ret = {ret_w:#x})")
        if ret_h != MV_OK:
            logger.warning(f"Не удалось установить Height = {self.height} (ret = {ret_h:#x})")

    def _set_pixel_format(self):
        """Установка формата пикселей (критическая настройка)."""
        ret = self.cam.MV_CC_SetEnumValue("PixelFormat", self.pixel_format_value)
        if ret != MV_OK:
            logger.error(
                f"Не удалось установить PixelFormat {self.pixel_format_name} (ret = {ret:#x})"
            )
            raise RuntimeError(f"Установка PixelFormat провалилась (ret = {ret:#x})")

    def start(self):
        """Запуск непрерывного захвата кадров."""
        ret = self.cam.MV_CC_StartGrabbing()
        if ret != MV_OK:
            raise RuntimeError(f"MV_CC_StartGrabbing failed (ret = {ret:#x})")
        self.running = True
        self.frame_count = 0
        self.last_frame_time = time.time()
        logger.info("Захват кадров запущен")

    def read(self):
        """
        Получение одного кадра.
        Возвращает (success: bool, frame: np.ndarray или None)
        """
        if not self.running:
            return False, None

        stFrameInfo = MV_FRAME_OUT_INFO_EX()
        MAX_BUFFER_SIZE = 3072 * 2048 * 3  # безопасный максимум
        pData = (ctypes.c_ubyte * MAX_BUFFER_SIZE)()

        ret = self.cam.MV_CC_GetOneFrameTimeout(byref(pData), MAX_BUFFER_SIZE, stFrameInfo, 1000)

        if ret != MV_OK:
            if ret == MV_E_GC_TIMEOUT:
                logger.debug("Таймаут получения кадра")
            else:
                logger.warning(f"Ошибка получения кадра (ret = {ret:#x})")
            return False, None

        # Реальные параметры кадра из структуры (самый надёжный источник)
        w = stFrameInfo.nWidth
        h = stFrameInfo.nHeight
        pixel_type = stFrameInfo.enPixelType
        data_len = stFrameInfo.nFrameLen

        logger.debug(f"Получен кадр: {w}x{h}, pixel_type={pixel_type:#x}, len={data_len}")

        try:
            # Берём только реальное количество байт
            raw_data = np.frombuffer(pData, dtype=np.uint8, count=data_len)

            if pixel_type == PixelType_Gvsp_Mono8:
                raw = raw_data.reshape((h, w))
                frame = cv2.cvtColor(raw, cv2.COLOR_GRAY2BGR)

            elif pixel_type == PixelType_Gvsp_BayerRG8:
                raw = raw_data.reshape((h, w))
                frame = cv2.cvtColor(
                    raw, cv2.COLOR_BayerBG2BGR
                )  # или BayerRG2BGR — зависит от камеры

            else:
                logger.error(f"Неожиданный тип пикселей: {pixel_type:#x}")
                return False, None

            # Расчёт FPS
            self.frame_count += 1
            now = time.time()
            elapsed = now - self.last_frame_time
            if elapsed >= 1.0:
                self.fps = self.frame_count / elapsed
                self.frame_count = 0
                self.last_frame_time = now

            # Отрисовка FPS прямо на кадре
            cv2.putText(
                frame,
                f"FPS: {self.fps:.1f}",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0, 255, 0),
                3,
                cv2.LINE_AA,
            )

            return True, frame

        except ValueError as e:
            logger.error(
                f"Ошибка reshape кадра: {e} " f"(ожидаемый размер: {h*w}, получено: {len(raw_data)})"
            )
            return False, None
        except Exception as e:
            logger.exception("Неожиданная ошибка обработки кадра")
            return False, None

    def stop(self):
        """Остановка захвата кадров."""
        if self.running and self.cam:
            self.cam.MV_CC_StopGrabbing()
            self.running = False
            logger.info("Захват остановлен")

    def release(self):
        """Полное освобождение ресурсов камеры."""
        self.stop()
        if self.cam:
            self.cam.MV_CC_CloseDevice()
            self.cam.MV_CC_DestroyHandle()
            self.cam = None
        logger.debug("Ресурсы камеры освобождены")

    def get_fps(self):
        """Возвращает текущее значение FPS."""
        return self.fps


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Этот файл — модуль, запуск напрямую не предусмотрен")
