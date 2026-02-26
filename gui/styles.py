# gui/styles.py
"""Централизованное хранение стилей."""

BUTTON_STYLES = {
    'primary': """
        QPushButton {
            background-color: #3498db;
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:pressed {
            background-color: #216795;
        }
        QPushButton:disabled {
            background-color: #bdc3c7;
        }
    """,
    'danger': """
        QPushButton {
            background-color: #e74c3c;
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #c0392b;
        }
        QPushButton:pressed {
            background-color: #962d22;
        }
    """,
    'success': """
        QPushButton {
            background-color: #27ae60;
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #229954;
        }
    """
}

PANEL_STYLES = {
    'background': "#f0f0f0",
    'border': "1px solid #ccc",
    'status': """
        QLabel {
            font-size: 14px;
            color: #555;
            padding: 5px;
            border: 1px solid #ccc;
            border-radius: 3px;
            background-color: white;
        }
    """
}