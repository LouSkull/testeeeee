from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QSlider, QLineEdit, QLabel, QComboBox
from PySide6.QtCore import Qt
from Settings.Config import load_settings, save_settings

class AimLockTabUI_New(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.init_ui()
    def init_ui(self):
        layout = QVBoxLayout()
        self.aim_active_cb = QCheckBox("Enable Aim")
        self.aim_active_cb.setStyleSheet("color: white;")
        self.aim_active_cb.setChecked(self.settings.get("aim_active", 0) == 1)
        self.aim_active_cb.stateChanged.connect(self.on_settings_changed)
        layout.addWidget(self.aim_active_cb)
        
        self.radius_slider = QSlider(Qt.Horizontal)
        self.radius_slider.setMinimum(0)
        self.radius_slider.setMaximum(100)
        self.radius_slider.setValue(self.settings.get("radius", 20))
        self.radius_slider.valueChanged.connect(self.on_settings_changed)
        layout.addWidget(QLabel("Aim Radius:"))
        layout.addWidget(self.radius_slider)
        
        self.keyboard_input = QLineEdit()
        self.keyboard_input.setText(self.settings.get("keyboard", "C"))
        self.keyboard_input.textChanged.connect(self.on_settings_changed)
        layout.addWidget(QLabel("Aim Key:"))
        layout.addWidget(self.keyboard_input)
        
        self.aim_mode_cb = QComboBox()
        self.aim_mode_cb.addItems(["Body", "Head"])
        self.aim_mode_cb.setCurrentIndex(self.settings.get("aim_mode", 1))
        self.aim_mode_cb.currentIndexChanged.connect(self.on_settings_changed)
        layout.addWidget(QLabel("Aim Mode:"))
        layout.addWidget(self.aim_mode_cb)
        
        self.aim_distance_cb = QComboBox()
        self.aim_distance_cb.addItems(["Closest to Crosshair", "Closest in 3D"])
        self.aim_distance_cb.setCurrentIndex(self.settings.get("aim_mode_distance", 1))
        self.aim_distance_cb.currentIndexChanged.connect(self.on_settings_changed)
        layout.addWidget(QLabel("Aim Distance Mode:"))
        layout.addWidget(self.aim_distance_cb)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: #404040; border-radius: 10px; padding: 10px;")
    def on_settings_changed(self):
        self.settings["aim_active"] = 1 if self.aim_active_cb.isChecked() else 0
        self.settings["radius"] = self.radius_slider.value()
        self.settings["keyboard"] = self.keyboard_input.text()
        self.settings["aim_mode"] = self.aim_mode_cb.currentIndex()
        self.settings["aim_mode_distance"] = self.aim_distance_cb.currentIndex()
        save_settings(self.settings)
