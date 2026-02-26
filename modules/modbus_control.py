# modules/modbus_control.py
"""
Модуль управления сервоприводом Delta ASDA-AB по Modbus RTU (JOG-режим).
Поддерживает подключение, команды JOG и регулировку скорости с ограничениями.
"""

import logging
import minimalmodbus

logger = logging.getLogger(__name__)

JOG_STEP = 25  # Шаг изменения скорости (об/мин)


class ServoController:
    """Класс управления сервоприводом Delta ASDA-AB в режиме JOG."""

    REGISTERS = {
        "JOG": 1029,  # P4-05: регистр управления JOG
        "VERSION": 0,  # P0-00: версия ПО
        "ERROR": 1,  # P0-01: код ошибки
    }

    JOG_COMMANDS = {
        "FORWARD": 4998,  # Команда вперёд
        "REVERSE": 4999,  # Команда назад
        "STOP": 5000,  # Команда остановки
    }

    MIN_SPEED = 0  # Минимальная скорость
    MAX_SPEED = 400  # Максимальная скорость

    def __init__(self, config):
        """Инициализация с конфигурацией Modbus."""
        self.config = config.get("modbus", {})
        self.instrument = None
        self.current_speed = 75  # Начальная скорость
        self.current_direction = None  # None / "forward" / "reverse"
        self.connected = False

    def connect(self):
        """Подключение к сервоприводу через Modbus RTU."""
        try:
            self.instrument = minimalmodbus.Instrument(
                self.config["port"], self.config["slave_address"]
            )
            self.instrument.serial.baudrate = self.config["baudrate"]
            self.instrument.serial.bytesize = self.config["bytesize"]
            self.instrument.serial.parity = self.config["parity"]
            self.instrument.serial.stopbits = self.config["stopbits"]
            self.instrument.serial.timeout = self.config["timeout"]

            logger.info(f"Modbus подключён: {self.config['port']} @ {self.config['baudrate']} baud")
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"Не удалось подключиться: {e}")
            self.connected = False
            return False

    def read_version(self):
        """Чтение версии ПО привода (P0-00). Возвращает None при ошибке."""
        if not self.connected:
            return None
        try:
            return self.instrument.read_register(self.REGISTERS["VERSION"])
        except Exception as e:
            logger.warning(f"Не удалось прочитать версию ПО: {e}")
            return None

    def check_connection(self):
        """Проверка связи и ошибок. Возвращает True, если ошибок нет."""
        if not self.connected:
            return False
        try:
            version = self.instrument.read_register(self.REGISTERS["VERSION"])
            error = self.instrument.read_register(self.REGISTERS["ERROR"])
            logger.info(f"Версия ПО: {version}, код ошибки: {error}")
            return error == 0
        except Exception as e:
            logger.error(f"Ошибка проверки связи: {e}")
            return False

    def jog(self, direction: str):
        """Отправка команды JOG: forward / reverse / stop."""
        if not self.connected:
            logger.warning("Сервопривод не подключён")
            return False

        try:
            if direction in ("forward", "reverse"):
                cmd = self.JOG_COMMANDS[direction.upper()]
                self.current_direction = direction
            else:  # stop
                cmd = self.JOG_COMMANDS["STOP"]
                self.current_direction = None

            self.instrument.write_register(self.REGISTERS["JOG"], cmd)
            logger.info(f"JOG → {direction.upper()} | скорость {self.current_speed} об/мин")
            return True
        except Exception as e:
            logger.error(f"Ошибка команды JOG: {e}")
            return False

    def jog_forward(self):
        """Вращение вперёд (shortcut для jog)."""
        return self.jog("forward")

    def jog_reverse(self):
        """Вращение назад (shortcut для jog)."""
        return self.jog("reverse")

    def set_speed(self, speed: int):
        """Установка скорости JOG с проверкой границ."""
        if not self.connected:
            logger.warning("Сервопривод не подключён")
            return False

        clamped_speed = max(self.MIN_SPEED, min(self.MAX_SPEED, int(speed)))
        if clamped_speed != speed:
            logger.warning(
                f"Скорость {speed} вне диапазона [{self.MIN_SPEED}–{self.MAX_SPEED}]. Установлено {clamped_speed}"
            )

        try:
            self.instrument.write_register(self.REGISTERS["JOG"], clamped_speed)
            self.current_speed = clamped_speed
            logger.info(f"Скорость установлена: {clamped_speed} об/мин")

            # Перезапуск движения, если активен
            if self.current_direction:
                self.jog(self.current_direction)

            return True
        except Exception as e:
            logger.error(f"Ошибка установки скорости: {e}")
            return False

    def increase_speed(self):
        """Увеличение скорости на шаг."""
        return self.set_speed(self.current_speed + JOG_STEP)

    def decrease_speed(self):
        """Уменьшение скорости на шаг."""
        return self.set_speed(self.current_speed - JOG_STEP)

    def stop(self):
        """Остановка (shortcut для jog)."""
        return self.jog("stop")

    def close(self):
        """Завершение работы: остановка и сброс скорости."""
        if self.connected:
            self.stop()
            self.set_speed(20)
            logger.info("Сервопривод остановлен и сброшен")
            self.connected = False
