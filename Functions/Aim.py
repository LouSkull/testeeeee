import time
import threading
import requests
import pymem
import pymem.process
import win32api
from PySide6.QtCore import QCoreApplication
from Settings.Config import CONFIG_FILE

def aim():
    # Здесь реализуется логика aimbot'а, аналогичная оригинальному коду
    pass

def aim_program():
    app = QCoreApplication([])
    threading.Thread(target=aim, daemon=True).start()
    app.exec()
