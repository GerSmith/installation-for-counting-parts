# main.py
import sys
import logging

from PySide6.QtWidgets import QApplication

from modules.utils import load_config, setup_logging
from modules.camera import get_camera
from modules.modbus_control import ServoController
from modules.uart_control import RP2040Controller
from gui.main_window import MainWindow


def main():
    """Главная функция приложения."""
    # Настройка логирования
    setup_logging()
    logger = logging.getLogger(__name__)

    # Загрузка конфигурации
    config = load_config()

    # Инициализация устройств
    camera = get_camera(config)
    servo = ServoController(config)
    rp2040 = RP2040Controller(config)

    # Подключение устройств
    if servo.connect():
        logger.info("Сервопривод подключён")
    else:
        logger.warning("Сервопривод не подключён")

    if rp2040.connect():
        logger.info(f"RP2040 подключён: {rp2040.default_freq} Гц, {rp2040.default_duty}%")
    else:
        logger.warning("RP2040 не подключён")

    # Запуск GUI
    app = QApplication(sys.argv)
    window = MainWindow(config, camera, servo, rp2040)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
