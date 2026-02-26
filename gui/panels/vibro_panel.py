# gui/panels/vibro_panel.py
from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QHBoxLayout, QLabel
from PySide6.QtCore import Signal, Qt


class VibroPanel(QGroupBox):
    """Панель управления вибробункером."""

    vibro_on_requested = Signal()
    vibro_off_requested = Signal()

    def __init__(self, rp2040, parent=None):
        super().__init__("Вибробункер (RP2040)", parent)
        self.rp2040 = rp2040
        self.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """
        )

        self._setup_ui()
        self._connect_signals()
        self._update_controls_enabled()

    def _setup_ui(self):
        """Создание интерфейса панели."""
        layout = QVBoxLayout()
        layout.setSpacing(8)

        # Кнопки управления в одной строке
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        # Кнопка ВКЛ
        self.btn_on = QPushButton("Вкл (v)")
        self.btn_on.setFixedHeight(45)
        self.btn_on.setFocusPolicy(Qt.NoFocus)
        self.btn_on.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 3px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """
        )
        btn_layout.addWidget(self.btn_on)

        # Кнопка ВЫКЛ
        self.btn_off = QPushButton("Выкл (b)")
        self.btn_off.setFixedHeight(45)
        self.btn_off.setFocusPolicy(Qt.NoFocus)
        self.btn_off.setStyleSheet(
            """
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 3px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #707b7c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """
        )
        btn_layout.addWidget(self.btn_off)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _connect_signals(self):
        """Подключение сигналов кнопок."""
        self.btn_on.clicked.connect(self.vibro_on_requested.emit)
        self.btn_off.clicked.connect(self.vibro_off_requested.emit)

    def _update_controls_enabled(self):
        """Обновление состояния кнопок."""
        enabled = bool(self.rp2040 and self.rp2040.connected)
        self.btn_on.setEnabled(enabled)
        self.btn_off.setEnabled(enabled)

    def update_status(self):
        """Обновление статуса (теперь только состояние кнопок)."""
        self._update_controls_enabled()
