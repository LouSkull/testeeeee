from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox
from Settings.Config import load_settings, save_settings
import pymem
import pymem.process
import requests
from include.utils import prints

offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json').json()
client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json').json()
dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
m_flFlashMaxAlpha = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_flFlashMaxAlpha']

class MiscTabUI_New(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.init_ui()
    def init_ui(self):
        layout = QVBoxLayout()
        self.anti_flash_cb = QCheckBox("Anti Flash")
        self.anti_flash_cb.setStyleSheet("color: white;")
        self.anti_flash_cb.setChecked(self.settings.get("anti_flash", 0) == 1)
        self.anti_flash_cb.stateChanged.connect(self.on_anti_flash_changed)
        layout.addWidget(self.anti_flash_cb)
        self.unsafe_cb = QCheckBox("Enable Unsafe Mode (Risk of BAN!)")
        self.unsafe_cb.setStyleSheet("color: yellow;")
        self.unsafe_cb.setChecked(self.settings.get("unsafe", 0) == 1)
        self.unsafe_cb.stateChanged.connect(self.on_unsafe_changed)
        layout.addWidget(self.unsafe_cb)
        self.setLayout(layout)
        self.setStyleSheet("background-color: #404040; border-radius: 10px; padding: 10px;")
    def on_anti_flash_changed(self):
        self.settings["anti_flash"] = 1 if self.anti_flash_cb.isChecked() else 0
        save_settings(self.settings)
        try:
            pm = pymem.Pymem("cs2.exe")
            client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
            player = pm.read_longlong(client + dwLocalPlayerPawn)
            if self.settings["anti_flash"]:
                pm.write_int(player + m_flFlashMaxAlpha, 0)
            else:
                pm.write_int(player + m_flFlashMaxAlpha, 1132396544)
        except:
            prints.printNotOk("Failed to toggle anti-flash.")
    def on_unsafe_changed(self):
        self.settings["unsafe"] = 1 if self.unsafe_cb.isChecked() else 0
        save_settings(self.settings)
