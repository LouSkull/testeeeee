from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import QEvent, QPoint
from PySide6.QtWidgets import QMainWindow, QPushButton, QDialog, QVBoxLayout, QLabel, QDialogButtonBox
from UI.ESPUI import ESPWindow
from UI.LegitUI import AimLockTabUI_New
from UI.TriggerUI import TriggerTabUI_New
from UI.MiscUI import MiscTabUI_New
from UI.SettingsUI import SettingsTabUI_New

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VacBanBETA")
        self.setGeometry(100, 100, 400, 300)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.addTab(ESPWindow({}), "ESP")
        self.tabs.addTab(AimLockTabUI_New(), "Legit")
        self.tabs.addTab(TriggerTabUI_New(), "Trigger")
        self.tabs.addTab(MiscTabUI_New(), "Misc")
        self.tabs.addTab(SettingsTabUI_New(), "Settings")
        self.setCentralWidget(self.tabs)
        self.set_dark_theme()
        self.dragging = False
        self.drag_position = QPoint()
        self.about_button = QPushButton("About", self)
        self.about_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #444, stop:1 #555);
                color: white;
                font-size: 16px;
                border: none;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #555, stop:1 #666);
            }
        """)
        self.about_button.adjustSize()
        self.about_button.clicked.connect(self.show_about_dialog)

    def set_dark_theme(self):
        dark_style = """
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-size: 14px;
            }
            QTabWidget::pane {
                border: 1px solid #444;
            }
            QTabBar::tab {
                background: #444;
                color: white;
                padding: 8px;
                border: 1px solid #555;
            }
            QTabBar::tab:selected {
                background: #555;
                border-bottom: 2px solid #ff9800;
            }
        """
        self.setStyleSheet(dark_style)

    def show_about_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("About VacBan")
        dialog.setModal(True)
        layout = QVBoxLayout()
        label = QLabel()
        label.setWordWrap(True)
        label.setStyleSheet("color: white; font-size: 14px;")
        about_text = (
            "About VacBan:\n\n"
            "VacBan — это кастомный инструмент для Counter-Strike 2, "
            "разработанный с использованием Python и PySide6. "
            "Он включает функции ESP, aimbot, trigger bot и многое другое.\n\n"
            "Используйте инструмент ответственно и на свой страх и риск.\n\n"
            "Приятной игры!"
        )
        label.setText(about_text)
        layout.addWidget(label)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)
        dialog.setLayout(layout)
        dialog.exec()

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self.setWindowOpacity(0.72)
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self.dragging and event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = False
            self.setWindowOpacity(1.0)
            event.accept()
