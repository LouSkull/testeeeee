import time
import datetime
import win32gui, win32con
import pymem, pymem.process
from PySide6 import QtWidgets, QtCore, QtGui
from Functions.ESP import esp, get_window_size, get_offsets_and_client_dll
from Settings.Config import load_settings, CONFIG_FILE
from include.utils import prints

class ESPWindow(QtWidgets.QWidget):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.setWindowTitle('ESP Overlay')
        self.window_width, self.window_height = get_window_size("Counter-Strike 2")
        if self.window_width is None or self.window_height is None:
            prints.printNotOk("Error: game window not found.")
            exit(1)
        self.setGeometry(0, 0, self.window_width, self.window_height)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        hwnd = self.winId()
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
        self.file_watcher = QtCore.QFileSystemWatcher([CONFIG_FILE])
        self.file_watcher.fileChanged.connect(self.reload_settings)
        self.offsets, self.client_dll = get_offsets_and_client_dll()
        self.pm = pymem.Pymem("cs2.exe")
        self.client = pymem.process.module_from_name(self.pm.process_handle, "client.dll").lpBaseOfDll
        self.scene = QtWidgets.QGraphicsScene(self)
        self.view = QtWidgets.QGraphicsView(self.scene, self)
        self.view.setGeometry(0, 0, self.window_width, self.window_height)
        self.view.setRenderHint(QtGui.QPainter.Antialiasing)
        self.view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.view.setStyleSheet("background: transparent;")
        self.view.setSceneRect(0, 0, self.window_width, self.window_height)
        self.view.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_scene)
        self.timer.start(0)
        self.last_time = time.time()
        self.frame_count = 0
        self.fps = 0

    def reload_settings(self):
        self.settings = load_settings()
        self.window_width, self.window_height = get_window_size("Counter-Strike 2")
        if self.window_width is None or self.window_height is None:
            prints.printNotOk("Error: incorrect screen resolution.")
            exit(1)
        self.setGeometry(0, 0, self.window_width, self.window_height)
        self.update_scene()

    def update_scene(self):
        if not self.is_game_window_active():
            self.scene.clear()
            return
        self.scene.clear()
        try:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            esp(self.scene, self.pm, self.client, self.offsets, self.client_dll,
                self.window_width, self.window_height, self.settings)
            self.frame_count += 1

            if time.time() - self.last_time >= 1.0:
                self.fps = self.frame_count
                self.frame_count = 0
                self.last_time = time.time()

            # === Настройки текста ===
            font = QtGui.QFont("Courier New", 9, QtGui.QFont.Bold)
            text_string = f"VacBan Beta | github.com/VacBanProject | {self.fps} | 64tick | {current_time}"
            metrics = QtGui.QFontMetrics(font)
            text_width = metrics.horizontalAdvance(text_string)
            text_height = metrics.height()

            # === Позиция — прижимаем к правому верхнему ===
            margin = 15
            x_pos = self.window_width - text_width - margin
            y_pos = margin

            # === Ещё ближе текст к полоске ===
            text_offset_y = -4  # ещё выше

            # === Урезаем фон снизу ещё сильнее ===
            background_rect = QtWidgets.QGraphicsRectItem(
                QtCore.QRectF(x_pos - 6, y_pos - 6, text_width + 12, text_height + 6)
            )
            background_rect.setBrush(QtGui.QColor(0, 0, 0))
            background_rect.setPen(QtGui.QPen(QtCore.Qt.NoPen))
            background_rect.setZValue(-1)
            self.scene.addItem(background_rect)

            # === Верхняя белая полоска ===
            top_line = QtWidgets.QGraphicsRectItem(
                QtCore.QRectF(x_pos - 6, y_pos - 8, text_width + 12, 2)
            )
            top_line.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
            top_line.setPen(QtGui.QPen(QtCore.Qt.NoPen))
            top_line.setZValue(0)
            self.scene.addItem(top_line)

            # === Сам текст ===
            status = self.scene.addText(text_string, font)
            status.setPos(x_pos, y_pos + text_offset_y)
            status.setDefaultTextColor(QtGui.QColor(255, 255, 255))

        except Exception as e:
            prints.printNotOk(f"Scene Update Error: {e}")
            QtWidgets.QApplication.quit()

    def is_game_window_active(self):
        hwnd = win32gui.FindWindow(None, "Counter-Strike 2")
        if hwnd:
            foreground_hwnd = win32gui.GetForegroundWindow()
            return hwnd == foreground_hwnd
        return False
