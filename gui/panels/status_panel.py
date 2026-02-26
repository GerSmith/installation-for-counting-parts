# gui/panels/status_panel.py
from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer


class StatusPanel(QGroupBox):
    """Панель отображения статуса."""

    def __init__(self, servo, rp2040, parent=None):
        super().__init__("Текущее состояние", parent)
        self.servo = servo
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

        # Таймер обновления
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_all)
        self.timer.start(300)

    def _setup_ui(self):
        """Создание интерфейса панели."""
        layout = QVBoxLayout()
        layout.setSpacing(8)

        self.lbl_conveyor = QLabel("Конвейер: Остановлен")
        self.lbl_conveyor.setAlignment(Qt.AlignCenter)
        self.lbl_conveyor.setStyleSheet(
            """
            QLabel {
                font-size: 13px;
                color: #555;
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: white;
            }
        """
        )
        layout.addWidget(self.lbl_conveyor)

        self.lbl_vibro = QLabel("Вибробункер: Нет связи")
        self.lbl_vibro.setAlignment(Qt.AlignCenter)
        self.lbl_vibro.setStyleSheet(
            """
            QLabel {
                font-size: 13px;
                color: #555;
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: white;
            }
        """
        )
        layout.addWidget(self.lbl_vibro)

        self.setLayout(layout)

        self.update_all()

    def update_all(self):
        """Обновление всех статусов."""
        self.update_conveyor_status()
        self.update_vibro_status()

    def update_conveyor_status(self, servo=None):
        """Обновление статуса конвейера."""
        if servo:
            self.servo = servo

        if self.servo and self.servo.connected:
            direction = self.servo.current_direction or "Остановлен"
            speed = getattr(self.servo, "current_speed", 0)
            status_text = f"Конвейер: {direction.capitalize()}\n({speed} об/мин)"
            self.lbl_conveyor.setText(status_text)
        else:
            self.lbl_conveyor.setText("Конвейер: Нет связи")

    def update_vibro_status(self, rp2040=None):
        """Обновление статуса вибробункера."""
        if rp2040:
            self.rp2040 = rp2040

        if self.rp2040 and self.rp2040.connected:
            self.lbl_vibro.setText(f"Вибробункер:\n{self.rp2040.get_status()}")
        else:
            self.lbl_vibro.setText("Вибробункер: Нет связи")
