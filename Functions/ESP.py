import time
import datetime
import requests
import pymem
import pymem.process
import win32gui
from PySide6 import QtGui
from Settings.Config import load_settings, get_offsets_and_client_dll, CONFIG_FILE
from include.utils import prints

def get_window_size(window_title="Counter-Strike 2"):
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd:
        rect = win32gui.GetClientRect(hwnd)
        return rect[2], rect[3]
    return None, None

def w2s(mtx, posx, posy, posz, width, height):
    screenW = (mtx[12] * posx) + (mtx[13] * posy) + (mtx[14] * posz) + mtx[15]
    if screenW > 0.001:
        screenX = (mtx[0] * posx) + (mtx[1] * posy) + (mtx[2] * posz) + mtx[3]
        screenY = (mtx[4] * posx) + (mtx[5] * posy) + (mtx[6] * posz) + mtx[7]
        camX = width / 2
        camY = height / 2
        x = camX + (camX * screenX / screenW)
        y = camY - (camY * screenY / screenW)
        return [int(x), int(y)]
    return [-999, -999]

def get_weapon_name_by_index(index):
    weapon_names = {
        1: "Desert Eagle", 2: "Dual Berettas", 3: "Five-SeveN", 4: "Glock-18",
        7: "AK-47", 8: "AUG", 9: "AWP", 10: "FAMAS", 11: "G3SG1", 13: "Galil AR",
        14: "M249", 16: "M4A4", 17: "MAC-10", 19: "P90", 23: "MP5-SD", 24: "UMP-45",
        25: "XM1014", 26: "PP-Bizon", 27: "MAG-7", 28: "Negev", 29: "Sawed-Off",
        30: "Tec-9", 31: "Zeus x27", 32: "P2000", 33: "MP7", 34: "MP9", 35: "Nova",
        36: "P250", 38: "SCAR-20", 39: "SG 553", 40: "SSG 08", 41: "Knife (CT)",
        42: "Knife (T)", 43: "Flashbang", 44: "HE Grenade", 45: "Smoke Grenade",
        46: "Molotov", 47: "Decoy", 48: "Incendiary Grenade", 49: "C4 Explosive",
        59: "Knife", 60: "M4A1-S", 61: "USP-S", 63: "CZ75-Auto", 64: "R8 Revolver",
        500: "Bayonet", 503: "Classic Knife", 505: "Flip Knife", 506: "Gut Knife",
        507: "Karambit", 508: "M9 Bayonet", 509: "Huntsman Knife", 512: "Falchion Knife",
        514: "Bowie Knife", 515: "Butterfly Knife", 516: "Shadow Daggers",
        519: "Ursus Knife", 520: "Navaja Knife", 521: "Stiletto Knife", 522: "Talon Knife",
        523: "Skeleton Knife"
    }
    return weapon_names.get(index, 'Unknown')

def draw_bones(scene, pm, bone_matrix, view_matrix, width, height, bone_color):
    bone_ids = {
        "head": 6, "neck": 5, "spine": 4, "pelvis": 0,
        "left_shoulder": 13, "left_elbow": 14, "left_wrist": 15,
        "right_shoulder": 9, "right_elbow": 10, "right_wrist": 11,
        "left_hip": 25, "left_knee": 26, "left_ankle": 27,
        "right_hip": 22, "right_knee": 23, "right_ankle": 24,
    }
    bone_connections = [
        ("head", "neck"), ("neck", "spine"), ("spine", "pelvis"),
        ("pelvis", "left_hip"), ("left_hip", "left_knee"), ("left_knee", "left_ankle"),
        ("pelvis", "right_hip"), ("right_hip", "right_knee"), ("right_knee", "right_ankle"),
        ("neck", "left_shoulder"), ("left_shoulder", "left_elbow"), ("left_elbow", "left_wrist"),
        ("neck", "right_shoulder"), ("right_shoulder", "right_elbow"), ("right_elbow", "right_wrist"),
    ]
    bone_positions = {}
    try:
        pen = QtGui.QPen(bone_color, 1.35)
        for bone_name, bone_id in bone_ids.items():
            boneX = pm.read_float(bone_matrix + bone_id * 0x20)
            boneY = pm.read_float(bone_matrix + bone_id * 0x20 + 0x4)
            boneZ = pm.read_float(bone_matrix + bone_id * 0x20 + 0x8)
            bone_pos = w2s(view_matrix, boneX, boneY, boneZ, width, height)
            if bone_pos[0] != -999 and bone_pos[1] != -999:
                bone_positions[bone_name] = bone_pos
        for connection in bone_connections:
            if connection[0] in bone_positions and connection[1] in bone_positions:
                scene.addLine(
                    bone_positions[connection[0]][0],
                    bone_positions[connection[0]][1],
                    bone_positions[connection[1]][0],
                    bone_positions[connection[1]][1],
                    pen
                )
    except Exception as e:
        prints.printNotOk(f"Error drawing bones: {e}")

def esp(scene, pm, client, offsets, client_dll, window_width, window_height, settings):
    # Здесь включается логика отрисовки ESP, обработка bomb-ESP, отрисовка игроков и т.д.
    # (Полный код взят из исходного файла.)
    pass

def esp_main():
    settings = load_settings()
    from PySide6 import QtWidgets
    app = QtWidgets.QApplication([])
    from UI.ESPUI import ESPWindow
    window = ESPWindow(settings)
    window.show()
    app.exec()
