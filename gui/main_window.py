# gui/main_window.py
from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QTimer

from gui.panels.conveyor_panel import ConveyorPanel
from gui.panels.vibro_panel import VibroPanel
from gui.panels.status_panel import StatusPanel
from gui.panels.video_panel import VideoPanel
from gui.threads.video_thread import VideoThread


class MainWindow(QMainWindow):
    """Главное окно - только компоновка и связывание компонентов."""

    def __init__(self, config, camera, servo, rp2040):
        super().__init__()
        self.config = config
        self.camera = camera
        self.servo = servo
        self.rp2040 = rp2040

        self.setWindowTitle("Конвейер: Подсчёт деталей")
        self.resize(1280, 720)

        # 1. Сначала создаем панели
        self._create_panels()

        # 2. Затем создаем потоки
        self._create_threads()

        # 3. Компоновка
        self._setup_layout()

        # 4. Подключение сигналов
        self._connect_signals()

        # 5. Запуск потоков
        self._start_threads()

        # 6. Установка фокуса
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def _create_panels(self):
        """Создание панелей интерфейса."""
        self.video_panel = VideoPanel()
        self.conveyor_panel = ConveyorPanel(self.servo)
        self.vibro_panel = VibroPanel(self.rp2040)
        self.status_panel = StatusPanel(self.servo, self.rp2040)

        # Отключаем фокус у всех панелей
        for panel in [self.conveyor_panel, self.vibro_panel, self.status_panel]:
            panel.setFocusPolicy(Qt.NoFocus)
            self._set_no_focus_recursive(panel)

        # Получаем горячие клавиши из конфига
        self.keys = self.config.get("control", {}).get("keys", {})

    def _set_no_focus_recursive(self, widget):
        """Рекурсивно отключает фокус у виджета и всех его детей."""
        widget.setFocusPolicy(Qt.NoFocus)
        for child in widget.findChildren(QWidget):
            child.setFocusPolicy(Qt.NoFocus)

    def _create_threads(self):
        """Создание потоков."""
        self.video_thread = VideoThread(self.camera)

    def _setup_layout(self):
        """Компоновка интерфейса."""
        # Главный горизонтальный layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Левая часть - видео
        main_layout.addWidget(self.video_panel, stretch=4)

        # Правая часть - панели управления
        control_container = QWidget()
        control_container.setFixedWidth(350)
        control_container.setStyleSheet(
            """
            QWidget {
                background-color: #f5f5f5;
                border-left: 2px solid #ccc;
            }
        """
        )

        control_layout = QVBoxLayout(control_container)
        control_layout.setContentsMargins(10, 10, 10, 10)
        control_layout.setSpacing(15)

        control_layout.addWidget(self.conveyor_panel)
        control_layout.addWidget(self.vibro_panel)
        control_layout.addWidget(self.status_panel)
        control_layout.addStretch()

        main_layout.addWidget(control_container, stretch=1)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def _connect_signals(self):
        """Подключение сигналов между компонентами."""
        # Сигналы от панелей
        self.conveyor_panel.forward_requested.connect(self._on_forward)
        self.conveyor_panel.reverse_requested.connect(self._on_reverse)
        self.conveyor_panel.stop_requested.connect(self._on_stop)
        self.conveyor_panel.speed_increase_requested.connect(self._on_increase_speed)
        self.conveyor_panel.speed_decrease_requested.connect(self._on_decrease_speed)

        self.vibro_panel.vibro_on_requested.connect(self._on_vib_on)
        self.vibro_panel.vibro_off_requested.connect(self._on_vib_off)

        # Сигналы от потока видео
        self.video_thread.change_pixmap_signal.connect(self.video_panel.update_image)

    def _start_threads(self):
        """Запуск потоков."""
        self.video_thread.start()

    def _on_forward(self):
        if self.servo:
            self.servo.jog_forward()
            self.status_panel.update_conveyor_status(self.servo)
            self.conveyor_panel.update_speed_display(self.servo.current_speed)
            self.setFocus()

    def _on_reverse(self):
        if self.servo:
            self.servo.jog_reverse()
            self.status_panel.update_conveyor_status(self.servo)
            self.conveyor_panel.update_speed_display(self.servo.current_speed)
            self.setFocus()

    def _on_stop(self):
        if self.servo:
            self.servo.stop()
            self.status_panel.update_conveyor_status(self.servo)
            self.conveyor_panel.update_speed_display(self.servo.current_speed)
            self.setFocus()

    def _on_increase_speed(self):
        if self.servo:
            self.servo.increase_speed()
            self.status_panel.update_conveyor_status(self.servo)
            self.conveyor_panel.update_speed_display(self.servo.current_speed)
            self.setFocus()

    def _on_decrease_speed(self):
        if self.servo:
            self.servo.decrease_speed()
            self.status_panel.update_conveyor_status(self.servo)
            self.conveyor_panel.update_speed_display(self.servo.current_speed)
            self.setFocus()

    def _on_vib_on(self):
        if self.rp2040:
            self.rp2040.vib_on()
            self.status_panel.update_vibro_status(self.rp2040)
            self.vibro_panel.update_status()
            self.setFocus()

    def _on_vib_off(self):
        if self.rp2040:
            self.rp2040.vib_off()
            self.status_panel.update_vibro_status(self.rp2040)
            self.vibro_panel.update_status()
            self.setFocus()

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return

        text = event.text().lower()
        key = event.key()

        if text == self.keys.get("start_conveyor", "w"):
            self._on_forward()
        elif text == self.keys.get("reverse_conveyor", "s"):
            self._on_reverse()
        elif key == Qt.Key.Key_Space or text == self.keys.get("stop_conveyor", " "):
            self._on_stop()
        elif text == self.keys.get("increase_speed", "d"):
            self._on_increase_speed()
        elif text == self.keys.get("decrease_speed", "a"):
            self._on_decrease_speed()
        elif text == self.keys.get("vib_on", "v"):
            self._on_vib_on()
        elif text == self.keys.get("vib_off", "b"):
            self._on_vib_off()
        elif text == self.keys.get("quit", "q"):
            self.close()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        self.setFocus()
        super().mousePressEvent(event)

    def closeEvent(self, event):
        if hasattr(self, "video_thread"):
            self.video_thread.stop()
        if self.servo:
            self.servo.close()
        if self.rp2040:
            self.rp2040.close()
        super().closeEvent(event)
