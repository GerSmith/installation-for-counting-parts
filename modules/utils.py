# modules/utils.py: Вспомогательные функции (чтение YAML, логирование)

import yaml
import logging

def load_config(config_path='config.yaml'):
    """Загружает конфигурацию из YAML-файла."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        # Простая валидация (расширь при необходимости)
        if 'camera' not in config or 'type' not in config['camera']:
            raise ValueError("Отсутствует раздел 'camera' или 'type'")
        return config
    except FileNotFoundError:
        logging.error(f"Файл конфигурации {config_path} не найден")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Ошибка парсинга YAML: {e}")
        raise

def setup_logging():
    """Настройка логирования с явной поддержкой UTF-8."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )   