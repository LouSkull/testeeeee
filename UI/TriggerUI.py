from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QLineEdit, QLabel, QFormLayout, QSlider, QComboBox
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QKeySequence
from Settings.Config import load_settings, save_settings
import win32api

class TriggerTabUI_New(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.is_selecting_key = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.trigger_bot_active_cb = QCheckBox("Enable Trigger Bot")
        self.trigger_bot_active_cb.setStyleSheet("color: white;")
        self.trigger_bot_active_cb.setChecked(self.settings.get("trigger_bot_active", 0) == 1)
        self.trigger_bot_active_cb.stateChanged.connect(self.on_settings_changed)
        layout.addWidget(self.trigger_bot_active_cb)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignTop)

        self.trigger_key_input = QLineEdit()
        self.trigger_key_input.setText(self.settings.get("keyboards", "Mouse4"))
        self.trigger_key_input.setReadOnly(True)
        self.trigger_key_input.setStyleSheet("background-color: #404040; border-radius: 5px; color: white;")
        self.trigger_key_input.installEventFilter(self)

        label_trigger_key = QLabel("Trigger Key:")
        label_trigger_key.setStyleSheet("color: white;")
        form_layout.addRow(label_trigger_key, self.trigger_key_input)
        layout.addLayout(form_layout)

        self.trigger_time_label = QLabel(f"Reaction Time: {self.settings.get('trigger_time', 30)} ms")
        self.trigger_time_label.setStyleSheet("color: white; font-size: 12px;")
        layout.addWidget(self.trigger_time_label)

        self.trigger_time_slider = QSlider(Qt.Horizontal)
        self.trigger_time_slider.setMinimum(1)
        self.trigger_time_slider.setMaximum(500)
        self.trigger_time_slider.setValue(int(self.settings.get("trigger_time", 30)))
        self.trigger_time_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #606060;
            }
            QSlider::handle:horizontal {
                background: white;
                width: 12px;
                border-radius: 6px;
                margin: -4px 0;
            }
        """)
        self.trigger_time_slider.valueChanged.connect(self.update_trigger_time)
        layout.addWidget(self.trigger_time_slider)

        self.trigger_mode_cb = QComboBox()
        self.trigger_mode_cb.addItems(["Only Enemies", "All Players"])
        self.trigger_mode_cb.setCurrentIndex(self.settings.get("trigger_mode", 0))
        self.trigger_mode_cb.setStyleSheet("""
            QComboBox {
                background-color: #404040;
                color: white;
                border-radius: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #292929;
                color: white; 
                selection-background-color: #333;
                selection-color: white;
                border-radius: 5px;
            }
        """)
        self.trigger_mode_cb.currentIndexChanged.connect(self.on_settings_changed)
        layout.addWidget(QLabel("Trigger Mode:"))
        layout.addWidget(self.trigger_mode_cb)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #404040; border-radius: 10px; padding: 10px;")

    def update_trigger_time(self, value):
        if isinstance(value, (int, float)):
            self.settings["trigger_time"] = value
        else:
            self.settings["trigger_time"] = 30
        self.trigger_time_label.setText(f"Reaction Time: {self.settings['trigger_time']} ms")
        save_settings(self.settings)

    def on_settings_changed(self):
        self.settings["trigger_bot_active"] = 1 if self.trigger_bot_active_cb.isChecked() else 0
        self.settings["keyboards"] = self.trigger_key_input.text()
        self.settings["trigger_mode"] = self.trigger_mode_cb.currentIndex()
        save_settings(self.settings)

    def eventFilter(self, obj, event):
        if obj == self.trigger_key_input:
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self.is_selecting_key = True
                self.trigger_key_input.setText("Press a key...")
                return True
            if self.is_selecting_key:
                if event.type() == QEvent.KeyPress:
                    key_name = QKeySequence(event.key()).toString()
                    if key_name:
                        self.trigger_key_input.setText(key_name)
                        self.settings["keyboards"] = key_name
                        save_settings(self.settings)
                        self.is_selecting_key = False
                        return True
                elif event.type() == QEvent.MouseButtonPress:
                    mouse_buttons = {
                        Qt.LeftButton: "Mouse1",
                        Qt.RightButton: "Mouse2",
                        Qt.MiddleButton: "Mouse3",
                    }
                    if event.button() in mouse_buttons:
                        self.trigger_key_input.setText(mouse_buttons[event.button()])
                        self.settings["keyboards"] = mouse_buttons[event.button()]
                        save_settings(self.settings)
                        self.is_selecting_key = False
                        return True
            if self.is_selecting_key:
                if win32api.GetAsyncKeyState(0x05) < 0:
                    self.trigger_key_input.setText("Mouse4")
                    self.settings["keyboards"] = "Mouse4"
                    save_settings(self.settings)
                    self.is_selecting_key = False
                    return True
                elif win32api.GetAsyncKeyState(0x06) < 0:
                    self.trigger_key_input.setText("Mouse5")
                    self.settings["keyboards"] = "Mouse5"
                    save_settings(self.settings)
                    self.is_selecting_key = False
                    return True
        return super().eventFilter(obj, event)
