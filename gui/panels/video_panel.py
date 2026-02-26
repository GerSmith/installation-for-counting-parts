# gui/panels/video_panel.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


class VideoPanel(QWidget):
    """Панель отображения видео."""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setStyleSheet("background-color: black; border: 1px solid #ccc;")

        layout.addWidget(self.image_label)

    def update_image(self, cv_img):
        """Обновление изображения."""
        try:
            if cv_img is None:
                return

            h, w, _ = cv_img.shape

            # Масштабирование с сохранением пропорций
            available_width = self.width()
            available_height = self.height()

            if available_width > 0 and available_height > 0:
                scale = min(available_width / w, available_height / h, 1.0)
                new_w, new_h = int(w * scale), int(h * scale)

                if scale < 1.0:
                    resized = cv2.resize(cv_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
                else:
                    resized = cv_img
                    new_w, new_h = w, h

                # Конвертация в QImage
                rgb_image = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
                bytes_per_line = 3 * new_w
                qt_img = QImage(rgb_image.data, new_w, new_h, bytes_per_line, QImage.Format_RGB888)

                self.image_label.setPixmap(QPixmap.fromImage(qt_img))

        except Exception as e:
            logger.error(f"Ошибка обновления изображения: {e}")
