import time
import json
import threading
import requests
import pymem
import pymem.process
import win32api
import psutil
from pynput.mouse import Controller
from PySide6.QtCore import QCoreApplication
from Settings.Config import CONFIG_FILE

def triggerbot():
    offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json').json()
    client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json').json()
    # Здесь и далее – реализация trigger bot (считывание памяти, проверка команды, нажатие мышью и т.д.)
    pass

def trigger_program():
    app = QCoreApplication([])
    threading.Thread(target=triggerbot, daemon=True).start()
    app.exec()
