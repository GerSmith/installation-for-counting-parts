# gui/panels/conveyor_panel.py
from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QHBoxLayout, QLabel
from PySide6.QtCore import Signal, Qt


class ConveyorPanel(QGroupBox):
    """Панель управления конвейером."""

    forward_requested = Signal()
    reverse_requested = Signal()
    stop_requested = Signal()
    speed_increase_requested = Signal()
    speed_decrease_requested = Signal()

    def __init__(self, servo, parent=None):
        super().__init__("Конвейер (сервопривод)", parent)
        self.servo = servo
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

    def _setup_ui(self):
        """Создание интерфейса панели."""
        layout = QVBoxLayout()
        layout.setSpacing(8)

        # Кнопки управления
        self.btn_forward = QPushButton("Вперёд (W)")
        self.btn_forward.setFixedHeight(45)
        self.btn_forward.setFocusPolicy(Qt.NoFocus)  # Отключаем фокус
        layout.addWidget(self.btn_forward)

        self.btn_reverse = QPushButton("Назад (S)")
        self.btn_reverse.setFixedHeight(45)
        self.btn_reverse.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(self.btn_reverse)

        self.btn_stop = QPushButton("СТОП (Space)")
        self.btn_stop.setFixedHeight(45)
        self.btn_stop.setFocusPolicy(Qt.NoFocus)
        self.btn_stop.setStyleSheet(
            """
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
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """
        )
        layout.addWidget(self.btn_stop)

        # Управление скоростью
        speed_layout = QHBoxLayout()

        self.btn_decrease = QPushButton("−")
        self.btn_decrease.setFixedSize(45, 45)
        self.btn_decrease.setFocusPolicy(Qt.NoFocus)
        self.btn_decrease.setStyleSheet(
            """
            QPushButton {
                font-size: 20px;
                font-weight: bold;
            }
        """
        )
        speed_layout.addWidget(self.btn_decrease)

        self.lbl_speed = QLabel("0 об/мин")
        self.lbl_speed.setAlignment(Qt.AlignCenter)
        self.lbl_speed.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                font-weight: bold;
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
            }
        """
        )
        speed_layout.addWidget(self.lbl_speed, stretch=1)

        self.btn_increase = QPushButton("+")
        self.btn_increase.setFixedSize(45, 45)
        self.btn_increase.setFocusPolicy(Qt.NoFocus)
        self.btn_increase.setStyleSheet(
            """
            QPushButton {
                font-size: 20px;
                font-weight: bold;
            }
        """
        )
        speed_layout.addWidget(self.btn_increase)

        layout.addLayout(speed_layout)
        self.setLayout(layout)

        self._update_controls_enabled()

    def _connect_signals(self):
        """Подключение сигналов кнопок."""
        self.btn_forward.clicked.connect(self.forward_requested.emit)
        self.btn_reverse.clicked.connect(self.reverse_requested.emit)
        self.btn_stop.clicked.connect(self.stop_requested.emit)
        self.btn_increase.clicked.connect(self.speed_increase_requested.emit)
        self.btn_decrease.clicked.connect(self.speed_decrease_requested.emit)

    def _update_controls_enabled(self):
        """Обновление состояния кнопок."""
        enabled = bool(self.servo and self.servo.connected)
        for btn in [
            self.btn_forward,
            self.btn_reverse,
            self.btn_stop,
            self.btn_increase,
            self.btn_decrease,
        ]:
            btn.setEnabled(enabled)

    def update_speed_display(self, speed):
        """Обновление отображения скорости."""
        self.lbl_speed.setText(f"{speed} об/мин")
