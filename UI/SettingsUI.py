from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSlider, QSpinBox, QFrame
from Settings.Config import load_settings, save_settings
from PySide6.QtCore import Qt

class SettingsTabUI_New(QWidget):
    def __init__(self, settings=None):
        super().__init__()
        self.settings = settings or load_settings()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        group_manual = QFrame()
        group_manual.setStyleSheet("background-color: #404040; border-radius: 10px; padding: 10px;")
        manual_layout = QVBoxLayout()
        manual_layout.addWidget(QLabel("Manual Color Settings"))
        self.init_manual_color_controls(manual_layout)
        group_manual.setLayout(manual_layout)
        main_layout.addWidget(group_manual)
        self.setLayout(main_layout)

    def init_manual_color_controls(self, layout):
        side_layout = QHBoxLayout()
        self.side_label = QLabel("Side:")
        self.side_cb = QComboBox()
        self.side_cb.addItems(["Team", "Opponents"])
        self.side_cb.setCurrentIndex(0)
        self.side_cb.currentIndexChanged.connect(self.update_rgb_controls)
        side_layout.addWidget(self.side_label)
        side_layout.addWidget(self.side_cb)
        layout.addLayout(side_layout)

        category_layout = QHBoxLayout()
        self.category_label = QLabel("Category:")
        self.category_cb = QComboBox()
        self.category_cb.addItems(["Skeleton", "Head circle", "Nick", "GUN", "Lines", "Box", "Tracer"])
        self.category_cb.setCurrentIndex(0)
        self.category_cb.currentIndexChanged.connect(self.update_rgb_controls)
        category_layout.addWidget(self.category_label)
        category_layout.addWidget(self.category_cb)
        layout.addLayout(category_layout)

        self.rgb_layout = QHBoxLayout()
        self.r_label = QLabel("R")
        self.r_slider, self.r_spinbox = self.create_rgb_control(0)
        self.g_label = QLabel("G")
        self.g_slider, self.g_spinbox = self.create_rgb_control(1)
        self.b_label = QLabel("B")
        self.b_slider, self.b_spinbox = self.create_rgb_control(2)
        for lbl, slider in [(self.r_label, self.r_slider),
                            (self.g_label, self.g_slider),
                            (self.b_label, self.b_slider)]:
            lbl.setStyleSheet("color: white; font-size: 12px;")
            self.rgb_layout.addWidget(lbl)
            self.rgb_layout.addLayout(slider)
        self.color_preview = QFrame()
        self.color_preview.setFixedSize(30, 30)
        self.color_preview.setStyleSheet("background-color: rgb(255, 255, 255); border: 1px solid #606060;")
        self.rgb_layout.addWidget(self.color_preview)
        layout.addLayout(self.rgb_layout)
        self.update_rgb_controls()

    def create_rgb_control(self, color_index):
        slider = QSlider()
        slider.setOrientation(Qt.Horizontal)
        slider.setRange(0, 255)
        slider.setFixedWidth(80)
        spinbox = QSpinBox()
        spinbox.setRange(0, 255)
        spinbox.setFixedWidth(50)
        slider.valueChanged.connect(spinbox.setValue)
        spinbox.valueChanged.connect(slider.setValue)
        slider.valueChanged.connect(lambda: self.save_rgb_values())
        h_layout = QHBoxLayout()
        h_layout.setSpacing(3)
        h_layout.addWidget(slider)
        h_layout.addWidget(spinbox)
        return h_layout, spinbox

    def update_rgb_controls(self):
        category = self.category_cb.currentText()
        key = self.get_color_key(category)
        color = self.settings.get(key, [255, 255, 255])
        r, g, b = color
        self.r_slider.itemAt(0).widget().setValue(r)
        self.g_slider.itemAt(0).widget().setValue(g)
        self.b_slider.itemAt(0).widget().setValue(b)
        self.update_color_preview()

    def save_rgb_values(self):
        category = self.category_cb.currentText()
        key = self.get_color_key(category)
        r = self.r_slider.itemAt(0).widget().value()
        g = self.g_slider.itemAt(0).widget().value()
        b = self.b_slider.itemAt(0).widget().value()
        self.settings[key] = [r, g, b]
        save_settings(self.settings)
        self.update_color_preview()

    def update_color_preview(self):
        category = self.category_cb.currentText()
        key = self.get_color_key(category)
        r, g, b = self.settings.get(key, [255, 255, 255])
        self.color_preview.setStyleSheet(f"background-color: rgb({r}, {g}, {b}); border: 1px solid #606060;")

    def get_color_key(self, category):
        mapping = {
            "Skeleton": "bone_color",
            "Head circle": "head_circle_color",
            "Nick": "nick_color",
            "GUN": "gun_color",
            "Lines": "lines_color",
            "Box": "box_color",
            "Tracer": "tracer_color"
        }
        base = mapping.get(category, "bone_color")
        side = self.side_cb.currentText() if hasattr(self, 'side_cb') else "Global"
        if side == "Team":
            return f"{base}_team"
        elif side == "Opponents":
            return f"{base}_enemy"
        else:
            return base
