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
            fps_text = self.scene.addText(
                f"VacBan Beta | FPS: {self.fps} | Time: {current_time}",
                QtGui.QFont('DejaVu Sans', 12, QtGui.QFont.Bold)
            )
            fps_text.setPos(-3, -5)
            fps_text.setDefaultTextColor(QtGui.QColor(255, 255, 255))
        except Exception as e:
            prints.printNotOk(f"Scene Update Error: {e}")
            QtWidgets.QApplication.quit()

    def is_game_window_active(self):
        hwnd = win32gui.FindWindow(None, "Counter-Strike 2")
        if hwnd:
            foreground_hwnd = win32gui.GetForegroundWindow()
            return hwnd == foreground_hwnd
        return False
