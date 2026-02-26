# modules/uart_control.py
"""
Модуль управления платой RP2040 по UART для формирования ШИМ на вибробункер.
"""

import logging
import serial

logger = logging.getLogger(__name__)


class RP2040Controller:
    """Класс управления RP2040 через USB-UART."""

    def __init__(self, config):
        """Инициализация с конфигурацией UART и RP2040."""
        self.config = config.get("uart", {})
        self.rp_config = config.get("rp2040", {})
        self.ser = None
        self.connected = False
        self.is_on = False
        
        # Читаем значения из конфига, используем значения по умолчанию если не указаны
        self.default_freq = self.rp_config.get("default_freq", 15)
        self.default_duty = self.rp_config.get("default_duty", 50)
        
        # Команды из конфига (с поддержкой форматирования)
        self.commands = self.rp_config.get("commands", {})
        
        self.current_freq = self.default_freq
        self.current_duty = self.default_duty

    def connect(self):
        """Подключение по UART."""
        try:
            self.ser = serial.Serial(
                self.config["port"],
                self.config["baudrate"],
                timeout=self.config.get("timeout", 1)
            )
            logger.info(f"UART подключён: {self.config['port']} @ {self.config['baudrate']} baud")
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"Не удалось подключиться по UART: {e}")
            self.connected = False
            return False

    def send_command(self, on_off: bool, freq=0, duty=0):
        """Отправка команды: вкл/выкл, частота, заполнение."""
        if not self.connected:
            logger.warning("UART не подключён")
            return False

        try:
            if on_off:
                # Используем переданные значения или значения из конфига
                freq = freq or self.default_freq
                duty = duty or self.default_duty
                
                # Проверяем наличие команды в конфиге
                if "on" in self.commands:
                    command = self.commands["on"].format(freq=freq, duty=duty)
                else:
                    # Формат по умолчанию, если не указан в конфиге
                    command = f"1,{freq},{duty}\r\n"
                
                self.is_on = True
                self.current_freq = freq
                self.current_duty = duty
            else:
                # Команда выключения
                if "off" in self.commands:
                    command = self.commands["off"].format(freq=self.current_freq, duty=self.current_duty)
                else:
                    command = f"0,{freq},{duty}\r\n"
                
                self.is_on = False

            # Добавляем перевод строки, если его нет в команде из конфига
            if not command.endswith('\n') and not command.endswith('\r\n'):
                command += '\r\n'
                
            self.ser.write(command.encode())
            logger.info(f"Команда ШИМ отправлена: {command.strip()}")
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки команды ШИМ: {e}")
            return False

    def vib_on(self, freq=None, duty=None):
        """Включение вибрации с возможностью указать частоту и заполнение."""
        return self.send_command(True, freq, duty)

    def vib_off(self):
        """Выключение вибрации."""
        return self.send_command(False)

    def set_frequency(self, freq):
        """Установка частоты ШИМ (если вибрация включена)."""
        if self.is_on:
            return self.vib_on(freq, self.current_duty)
        else:
            self.default_freq = freq
            self.current_freq = freq
            return True

    def set_duty(self, duty):
        """Установка коэффициента заполнения (если вибрация включена)."""
        if self.is_on:
            return self.vib_on(self.current_freq, duty)
        else:
            self.default_duty = duty
            self.current_duty = duty
            return True

    def get_status(self):
        """Получение текущего статуса ШИМ (строка для отображения)."""
        if not self.connected:
            return "Нет связи с RP2040"
        if self.is_on:
            return f"Вкл: {self.current_freq} Гц, {self.current_duty}%"
        return f"Выкл: {self.default_freq} Гц, {self.default_duty}%"

    def get_config_values(self):
        """Получение значений из конфига для отображения."""
        return {
            'freq': self.default_freq,
            'duty': self.default_duty
        }

    def close(self):
        """Завершение работы: выключение и закрытие порта."""
        if self.connected:
            self.vib_off()
            self.ser.close()
            logger.info("UART отключён")
            self.connected = False
