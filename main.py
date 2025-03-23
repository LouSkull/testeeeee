import sys
import time
import multiprocessing
from PySide6.QtWidgets import QApplication
import pymem
import pymem.process
import win32api
import psutil
from Settings.Config import load_settings
from Functions.ESP import esp_main
from Functions.Trigger import triggerbot
from Functions.Aim import aim
from UI.mainUI import MainWindow
from include import check_for_update
from include.utils import prints

if __name__ == "__main__":
    prints.println("Checking version...")
    time.sleep(0.35)
    if_ok = check_for_update.check(version=0.1)
    if if_ok:
        prints.println("You have the latest version!")
        time.sleep(1)
        print("Github - https://github.com/VacBanProject/VacBan-Cheat")
        prints.println("Trying to find Counter-Strike process...")
        while True:
            time.sleep(1)
            try:
                pm = pymem.Pymem("cs2.exe")
                client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
                break
            except Exception as e:
                prints.printNotOk(f"Error: {e}")
            except psutil.NoSuchProcess:
                prints.printNotOk("Error: Process not found.")
            except psutil.AccessDenied:
                prints.printNotOk("Error: Access denied. Try running as administrator.")
            except psutil.ZombieProcess:
                prints.printNotOk("Error: Process is a zombie.")
        prints.println("Successfully found cs2, please wait a moment...")
        time.sleep(1)
        prints.println("Loading VacBan BETA...")
        time.sleep(1)
        process_esp = multiprocessing.Process(target=esp_main)
        process_trigger = multiprocessing.Process(target=triggerbot)
        process_aim = multiprocessing.Process(target=aim)
        process_esp.start()
        process_trigger.start()
        process_aim.start()
        prints.println("Done! Press Insert to toggle the menu.")
        gui_app = QApplication(sys.argv)
        main_window = MainWindow()
        main_window.hide()
        insert_pressed = False  # Глобальная переменная
        from PySide6 import QtCore
        insert_timer = QtCore.QTimer()
        def check_insert():
            global insert_pressed  # Используем global, а не nonlocal
            is_pressed = (win32api.GetAsyncKeyState(0x2D) & 0x8000) != 0
            if is_pressed and not insert_pressed:
                insert_pressed = True
                if main_window.isVisible():
                    main_window.hide()
                    QApplication.setOverrideCursor(QtCore.Qt.BlankCursor)
                else:
                    main_window.show()
                    QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)
            elif not is_pressed and insert_pressed:
                insert_pressed = False
        insert_timer.timeout.connect(check_insert)
        insert_timer.start(100)
        gui_app.exec()
        process_esp.join()
        process_trigger.join()
        process_aim.join()
        sys.exit(0)
    else:
        prints.println("You have the wrong version!")
        time.sleep(1)
        prints.println("Install the latest version here: https://github.com/VacBanProject/VacBan-Cheat")
        input("Press enter to exit...")
