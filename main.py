# -*- coding: utf-8 -*-
import sys
import os
import json
import time
import datetime
import threading
import multiprocessing
import requests
import pymem
import pymem.process
import win32api
import win32con
import win32gui
import psutil
from include.utils import prints
from include import check_for_update
from include import default_settings
from include.console_control import change_title, clear_console
from colorama import Fore, Style, init

from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import QFileSystemWatcher, QCoreApplication, QEvent, Qt, QPoint
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QTabWidget, QLabel, QCheckBox, QComboBox, QLineEdit, QFormLayout,
                               QGraphicsView, QGraphicsScene, QPushButton, QDialog, QDialogButtonBox,
                               QSlider, QSpinBox, QFrame)
from PySide6.QtGui import QMouseEvent, QFont, QPen, QColor, QKeySequence
from pynput.mouse import Controller, Button

include_folder = "include"
init(autoreset=True)

change_title("VacBan-Loader")
os.system("color E")

# ===============================
# Settings and Helper Functions
# ===============================
CONFIG_DIR = os.path.join(os.environ['LOCALAPPDATA'], 'VAC Ban Cheat', 'configs')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

DEFAULT_SETTINGS = {
    "esp_rendering": 1,
    "esp_mode": 1,
    "line_rendering": 1,
    "hp_bar_rendering": 1,
    "head_hitbox_rendering": 1,
    "bons": 1,
    "nickname": 1,
    "keyboard": "C",
    "keyboards": "V",
    "weapon": 1,
    "bomb_esp": 1,
    "trigger_bot_active": 1,
    "anti_flash": 0,
    "esp_color_preset_global": "Default",
    
    "bone_color_enemy": [255, 0, 0],
    "Tracer_color_enemy": [255, 255, 255],
    "head_circle_color_enemy": [196, 30, 58],
    "nick_color_enemy": [196, 30, 58],
    "gun_color_enemy": [196, 30, 58],
    "Lines_color_enemy" : [255, 255, 255],
    "Box_color_enemy" : [255, 255, 255],
    
    "head_circle_color_team": [71, 167, 106],
    "nick_color_team": [71, 167, 106],
    "gun_color_team": [71, 167, 106],
    "bone_color_team": [0, 255, 0],
    "Lines_color_team" : [255, 255, 255],
    "Box_color_team" : [255, 255, 255],
    "Tracer_color_team": [255, 255, 255],
    
    "trigger_time": 100,
    "trigger_mode": 0,
    "aim_active": 1,
    "radius": 20,
    "aim_mode": 1,            # 0 - Body, 1 - Head
    "aim_mode_distance": 1    # 0 - Closest to Crosshair, 1 - Closest in 3D
}

def load_settings():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)
    try:
        with open(CONFIG_FILE, "r") as f:
            settings = json.load(f)
    except json.JSONDecodeError:
        # If the config file is empty, create a new one using default settings.
        if os.stat(CONFIG_FILE).st_size == 0:
            prints.println("config.json is empty, creating a new one...")
            with open(CONFIG_FILE, "w") as f:
                json.dump(DEFAULT_SETTINGS, f, indent=4)
        settings = DEFAULT_SETTINGS.copy()
    # Ensure all default keys exist in settings
    for key, value in DEFAULT_SETTINGS.items():
        if key not in settings:
            settings[key] = value
    return settings

def save_settings(settings):
    with open(CONFIG_FILE, "w") as f:
        json.dump(settings, f, indent=4)

def get_offsets_and_client_dll():
    offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json').json()
    client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json').json()
    return offsets, client_dll

def get_window_size(window_title="Counter-Strike 2"):
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd:
        rect = win32gui.GetClientRect(hwnd)
        return rect[2], rect[3]
    return None, None

def w2s(mtx, posx, posy, posz, width, height):
    # World-to-screen conversion
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
    # Returns weapon name based on its index
    weapon_names = {
        1: "Desert Eagle",
        2: "Dual Berettas",
        3: "Five-SeveN",
        4: "Glock-18",
        7: "AK-47",
        8: "AUG",
        9: "AWP",
        10: "FAMAS",
        11: "G3SG1",
        13: "Galil AR",
        14: "M249",
        16: "M4A4",
        17: "MAC-10",
        19: "P90",
        23: "MP5-SD",
        24: "UMP-45",
        25: "XM1014",
        26: "PP-Bizon",
        27: "MAG-7",
        28: "Negev",
        29: "Sawed-Off",
        30: "Tec-9",
        31: "Zeus x27",
        32: "P2000",
        33: "MP7",
        34: "MP9",
        35: "Nova",
        36: "P250",
        38: "SCAR-20",
        39: "SG 553",
        40: "SSG 08",
        41: "Knife (CT)",
        42: "Knife (T)",
        43: "Flashbang",
        44: "HE Grenade",
        45: "Smoke Grenade",
        46: "Molotov",
        47: "Decoy",
        48: "Incendiary Grenade",
        49: "C4 Explosive",
        59: "Knife",
        60: "M4A1-S",
        61: "USP-S",
        63: "CZ75-Auto",
        64: "R8 Revolver",
        500: "Bayonet",
        503: "Classic Knife",
        505: "Flip Knife",
        506: "Gut Knife",
        507: "Karambit",
        508: "M9 Bayonet",
        509: "Huntsman Knife",
        512: "Falchion Knife",
        514: "Bowie Knife",
        515: "Butterfly Knife",
        516: "Shadow Daggers",
        519: "Ursus Knife",
        520: "Navaja Knife",
        521: "Stiletto Knife",
        522: "Talon Knife",
        523: "Skeleton Knife"
    }
    return weapon_names.get(index, 'Unknown')

def draw_bones(scene, pm, bone_matrix, view_matrix, width, height, bone_color):
    # Define bone IDs for each body part
    bone_ids = {
        "head": 6,
        "neck": 5,
        "spine": 4,
        "pelvis": 0,
        "left_shoulder": 13,
        "left_elbow": 14,
        "left_wrist": 15,
        "right_shoulder": 9,
        "right_elbow": 10,
        "right_wrist": 11,
        "left_hip": 25,
        "left_knee": 26,
        "left_ankle": 27,
        "right_hip": 22,
        "right_knee": 23,
        "right_ankle": 24,
    }
    
    # Define bone connection pairs for drawing lines
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
                    bone_positions[connection[0]][0], bone_positions[connection[0]][1],
                    bone_positions[connection[1]][0], bone_positions[connection[1]][1], 
                    pen
                )

    except Exception as e:
        prints.printNotOk(f"Error drawing bones: {e}")

# ===============================
# ESP Function (with checks and Bomb Time)
# ===============================
BombPlantedTime = 0
BombDefusedTime = 0

def esp(scene, pm, client, offsets, client_dll, window_width, window_height, settings):
    global BombPlantedTime, BombDefusedTime

    if settings['esp_rendering'] == 0:
        return

    dwEntityList = offsets['client.dll']['dwEntityList']
    dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
    dwViewMatrix = offsets['client.dll']['dwViewMatrix']
    dwPlantedC4 = offsets['client.dll']['dwPlantedC4']
    m_iTeamNum = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iTeamNum']
    m_lifeState = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_lifeState']
    m_pGameSceneNode = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_pGameSceneNode']
    m_modelState = client_dll['client.dll']['classes']['CSkeletonInstance']['fields']['m_modelState']
    m_hPlayerPawn = client_dll['client.dll']['classes']['CCSPlayerController']['fields']['m_hPlayerPawn']
    m_iHealth = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iHealth']
    m_iszPlayerName = client_dll['client.dll']['classes']['CBasePlayerController']['fields']['m_iszPlayerName']
    m_pClippingWeapon = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_pClippingWeapon']
    m_AttributeManager = client_dll['client.dll']['classes']['C_EconEntity']['fields']['m_AttributeManager']
    m_Item = client_dll['client.dll']['classes']['C_AttributeContainer']['fields']['m_Item']
    m_iItemDefinitionIndex = client_dll['client.dll']['classes']['C_EconItemView']['fields']['m_iItemDefinitionIndex']
    m_ArmorValue = client_dll['client.dll']['classes']['C_CSPlayerPawn']['fields']['m_ArmorValue']
    m_vecAbsOrigin = client_dll['client.dll']['classes']['CGameSceneNode']['fields']['m_vecAbsOrigin']
    m_flTimerLength = client_dll['client.dll']['classes']['C_PlantedC4']['fields']['m_flTimerLength']
    m_flDefuseLength = client_dll['client.dll']['classes']['C_PlantedC4']['fields']['m_flDefuseLength']
    m_bBeingDefused = client_dll['client.dll']['classes']['C_PlantedC4']['fields']['m_bBeingDefused']

    view_matrix = [pm.read_float(client + dwViewMatrix + i * 4) for i in range(16)]
    local_player_pawn_addr = pm.read_longlong(client + dwLocalPlayerPawn)
    if not local_player_pawn_addr:
        return
    try:
        local_player_team = pm.read_int(local_player_pawn_addr + m_iTeamNum)
    except:
        return

    no_center_x = window_width / 2
    no_center_y = window_height * 0.9

    entity_list = pm.read_longlong(client + dwEntityList)
    if not entity_list:
        return
    entity_ptr = pm.read_longlong(entity_list + 0x10)
    if not entity_ptr:
        return

    # ===== Bomb Block =====
    def bombisplant():
        global BombPlantedTime
        planted = pm.read_bool(client + dwPlantedC4 - 0x8)
        if planted:
            if BombPlantedTime == 0:
                BombPlantedTime = time.time()
        else:
            BombPlantedTime = 0
        return planted

    def getC4BaseClass():
        plantedc4 = pm.read_longlong(client + dwPlantedC4)
        if not plantedc4:
            return 0
        return pm.read_longlong(plantedc4)

    def getPositionWTS():
        c4node = pm.read_longlong(getC4BaseClass() + m_pGameSceneNode)
        c4posX = pm.read_float(c4node + m_vecAbsOrigin)
        c4posY = pm.read_float(c4node + m_vecAbsOrigin + 0x4)
        c4posZ = pm.read_float(c4node + m_vecAbsOrigin + 0x8)
        return w2s(view_matrix, c4posX, c4posY, c4posZ, window_width, window_height)

    def getBombTime():
        global BombPlantedTime
        base = getC4BaseClass()
        if base == 0:
            return 0
        return pm.read_float(base + m_flTimerLength) - (time.time() - BombPlantedTime)

    def getDefuseTime():
        global BombDefusedTime
        base = getC4BaseClass()
        if base == 0:
            return 0
        return pm.read_float(base + m_flDefuseLength) - (time.time() - BombDefusedTime)

    if settings.get('bomb_esp', 0) == 1:
        if bombisplant():
            BombPosition = getPositionWTS()
            BombTime = getBombTime()
            DefuseTime = getDefuseTime()
            if BombPosition[0] > 0 and BombPosition[1] > 0:
                bfont = QtGui.QFont('DejaVu Sans', 10, QtGui.QFont.Bold)
                if BombTime <= 0:
                    text_str = "BOOM!"
                    time.sleep(2.5)
                else:
                    if DefuseTime > 0:
                        text_str = f'BOMB {round(BombTime, 2)} | DIF {round(DefuseTime, 2)}'
                    else:
                        text_str = f'BOMB {round(BombTime, 2)}'
                item = scene.addText(text_str, bfont)
                item.setPos(BombPosition[0], BombPosition[1])
                item.setDefaultTextColor(QtGui.QColor(255, 255, 255))
    # ===== End of Bomb Block =====

    # ===== Processing Players =====
    for i in range(1, 64):
        try:
            if entity_ptr == 0:
                break
            entity_controller = pm.read_longlong(entity_ptr + 0x78 * (i & 0x1FF))
            if entity_controller == 0:
                continue
            entity_controller_pawn = pm.read_longlong(entity_controller + m_hPlayerPawn)
            if entity_controller_pawn == 0:
                continue
            entity_list_pawn = pm.read_longlong(entity_list + 0x8 * ((entity_controller_pawn & 0x7FFF) >> 0x9) + 0x10)
            if entity_list_pawn == 0:
                continue
            entity_pawn_addr = pm.read_longlong(entity_list_pawn + 0x78 * (entity_controller_pawn & 0x1FF))
            if entity_pawn_addr == 0 or entity_pawn_addr == local_player_pawn_addr:
                continue
            entity_team = pm.read_int(entity_pawn_addr + m_iTeamNum)
            if entity_team == local_player_team and settings['esp_mode'] == 0:
                continue
            entity_hp = pm.read_int(entity_pawn_addr + m_iHealth)
            armor_hp = pm.read_int(entity_pawn_addr + m_ArmorValue)
            if entity_hp <= 0:
                continue
            entity_alive = pm.read_int(entity_pawn_addr + m_lifeState)
            if entity_alive != 256:
                continue
            weapon_pointer = pm.read_longlong(entity_pawn_addr + m_pClippingWeapon)
            weapon_index = pm.read_int(weapon_pointer + m_AttributeManager + m_Item + m_iItemDefinitionIndex)
            weapon_name = get_weapon_name_by_index(weapon_index)
            color = QtGui.QColor(*settings.get("bone_color", [255, 255, 255]))
            game_scene = pm.read_longlong(entity_pawn_addr + m_pGameSceneNode)
            bone_matrix = pm.read_longlong(game_scene + m_modelState + 0x80)
            try:
                headX = pm.read_float(bone_matrix + 6 * 0x20)
                headY = pm.read_float(bone_matrix + 6 * 0x20 + 0x4)
                headZ = pm.read_float(bone_matrix + 6 * 0x20 + 0x8) + 8
                head_pos = w2s(view_matrix, headX, headY, headZ, window_width, window_height)
                if head_pos[1] < 0:
                    continue
                if settings['line_rendering'] == 1:
                    legZ = pm.read_float(bone_matrix + 28 * 0x20 + 0x8)
                    leg_pos = w2s(view_matrix, headX, headY, legZ, window_width, window_height)
                    bottom_left_x = head_pos[0] - (head_pos[0] - leg_pos[0]) // 2
                    bottom_y = leg_pos[1]
                    line_color = settings.get("lines_color_team" if entity_team == local_player_team else "lines_color_enemy", [255, 255, 255])
                    scene.addLine(bottom_left_x, bottom_y, no_center_x, no_center_y, QtGui.QPen(QtGui.QColor(*line_color), 1))
                legZ = pm.read_float(bone_matrix + 28 * 0x20 + 0x8)
                leg_pos = w2s(view_matrix, headX, headY, legZ, window_width, window_height)
                deltaZ = abs(head_pos[1] - leg_pos[1])
                leftX = head_pos[0] - deltaZ // 4
                rightX = head_pos[0] + deltaZ // 4
                box_color = settings.get("box_color_team" if entity_team == local_player_team else "box_color_enemy", [255, 255, 255])
                scene.addRect(QtCore.QRectF(leftX, head_pos[1], rightX - leftX, leg_pos[1] - head_pos[1]),
                            QtGui.QPen(QtGui.QColor(*box_color), 1), QtCore.Qt.NoBrush)
                if settings['head_hitbox_rendering'] == 1:
                    head_hitbox_size = (rightX - leftX) / 5
                    head_hitbox_radius = head_hitbox_size * (2 ** 0.5) / 2
                    head_hitbox_x = leftX + 2.5 * head_hitbox_size
                    head_hitbox_y = head_pos[1] + deltaZ / 9
                    head_hitbox_radius *= 0.9
                    head_circle_color = settings.get("head_circle_color_team" if entity_team == local_player_team else "head_circle_color_enemy", [255, 255, 255])
                    scene.addEllipse(QtCore.QRectF(head_hitbox_x - head_hitbox_radius, head_hitbox_y - head_hitbox_radius,
                                                head_hitbox_radius * 2, head_hitbox_radius * 2),
                                    QtGui.QPen(QtGui.QColor(*head_circle_color), 1.35), QtCore.Qt.NoBrush)
                if settings['hp_bar_rendering'] == 1:
                    max_hp = 100
                    hp_percentage = min(1.0, max(0.0, entity_hp / max_hp))
                    hp_bar_width = 2
                    hp_bar_height = deltaZ
                    hp_bar_x_left = leftX - hp_bar_width - 2
                    hp_bar_y_top = head_pos[1]
                    scene.addRect(QtCore.QRectF(hp_bar_x_left, hp_bar_y_top, hp_bar_width, hp_bar_height),
                                  QtGui.QPen(QtCore.Qt.NoPen), QtGui.QColor(0, 0, 0))
                    current_hp_height = hp_bar_height * hp_percentage
                    hp_bar_y_bottom = hp_bar_y_top + hp_bar_height - current_hp_height
                    scene.addRect(QtCore.QRectF(hp_bar_x_left, hp_bar_y_bottom, hp_bar_width, current_hp_height),
                                  QtGui.QPen(QtCore.Qt.NoPen), QtGui.QColor(255, 0, 0))
                    max_armor_hp = 100
                    armor_hp_percentage = min(1.0, max(0.0, armor_hp / max_armor_hp))
                    armor_bar_width = 2
                    armor_bar_height = deltaZ
                    armor_bar_x_left = hp_bar_x_left - armor_bar_width - 2
                    armor_bar_y_top = head_pos[1]
                    scene.addRect(QtCore.QRectF(armor_bar_x_left, armor_bar_y_top, armor_bar_width, armor_bar_height),
                                  QtGui.QPen(QtCore.Qt.NoPen), QtGui.QColor(0, 0, 0))
                    current_armor_height = armor_bar_height * armor_hp_percentage
                    armor_bar_y_bottom = armor_bar_y_top + armor_bar_height - current_armor_height
                    scene.addRect(QtCore.QRectF(armor_bar_x_left, armor_bar_y_bottom, armor_bar_width, current_armor_height),
                                  QtGui.QPen(QtCore.Qt.NoPen), QtGui.QColor(62, 95, 138))
                if settings.get('bons', 0) == 1:
                    bone_color = (
                        settings.get("bone_color_team", [0, 255, 0])
                        if entity_team == local_player_team
                        else settings.get("bone_color_enemy", [255, 0, 0])
                    )
                    draw_bones(scene, pm, bone_matrix, view_matrix, window_width, window_height, QtGui.QColor(*bone_color))
                if settings.get('nickname', 0) == 1:
                    player_name = pm.read_string(entity_controller + m_iszPlayerName, 32)
                    font_size = max(6, min(18, deltaZ / 25))
                    font = QtGui.QFont('DejaVu Sans', font_size, QtGui.QFont.Bold)
                    nick_color_team = settings.get("nick_color_team", [0, 255, 0])
                    nick_color_enemy = settings.get("nick_color_enemy", [255, 0, 0])
                    nick_color = nick_color_team if entity_team == local_player_team else nick_color_enemy
                    name_text = scene.addText(player_name, font)
                    text_rect = name_text.boundingRect()
                    name_x = head_pos[0] - text_rect.width() / 2
                    name_y = head_pos[1] - text_rect.height()
                    name_text.setPos(name_x, name_y)
                    name_text.setDefaultTextColor(QtGui.QColor(*nick_color))
                if settings.get('weapon', 0) == 1:
                    weapon_name_text = scene.addText(weapon_name, font)
                    text_rect = weapon_name_text.boundingRect()
                    weapon_name_x = head_pos[0] - text_rect.width() / 2
                    weapon_name_y = head_pos[1] + deltaZ
                    weapon_name_text.setPos(weapon_name_x, weapon_name_y)
                    gun_color_team = settings.get("gun_color_team", [0, 255, 255])
                    gun_color_enemy = settings.get("gun_color_enemy", [255, 165, 0])
                    gun_color = gun_color_team if entity_team == local_player_team else gun_color_enemy
                    weapon_name_text.setDefaultTextColor(QtGui.QColor(*gun_color))
            except:
                return
        except:
            return

# ===============================
# ESPWindow Class (Overlay)
# ===============================
class ESPWindow(QtWidgets.QWidget):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.setWindowTitle('ESP Overlay')
        self.window_width, self.window_height = get_window_size("Counter-Strike 2")
        if self.window_width is None or self.window_height is None:
            prints.printNotOk("Error: game window not found.")
            sys.exit(1)
        self.setGeometry(0, 0, self.window_width, self.window_height)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        hwnd = self.winId()
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
        self.file_watcher = QFileSystemWatcher([CONFIG_FILE])
        self.file_watcher.fileChanged.connect(self.reload_settings)
        self.offsets, self.client_dll = get_offsets_and_client_dll()
        self.pm = pymem.Pymem("cs2.exe")
        self.client = pymem.process.module_from_name(self.pm.process_handle, "client.dll").lpBaseOfDll
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
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
            sys.exit(1)
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

            # === Настройки текста ===
            font = QtGui.QFont("Courier New", 9, QtGui.QFont.Bold)
            text_string = f"VacBan Beta | github.com/VacBanProject | {self.fps} | 64tick | {current_time}"
            metrics = QtGui.QFontMetrics(font)
            text_width = metrics.horizontalAdvance(text_string)
            text_height = metrics.height()

            # === Позиция — прижимаем к правому верхнему ===
            margin = 15
            x_pos = self.window_width - text_width - margin
            y_pos = margin

            # === Ещё ближе текст к полоске ===
            text_offset_y = -4  # ещё выше

            # === Урезаем фон снизу ещё сильнее ===
            background_rect = QtWidgets.QGraphicsRectItem(
                QtCore.QRectF(x_pos - 6, y_pos - 6, text_width + 12, text_height + 6)
            )
            background_rect.setBrush(QtGui.QColor(0, 0, 0))
            background_rect.setPen(QtGui.QPen(QtCore.Qt.NoPen))
            background_rect.setZValue(-1)
            self.scene.addItem(background_rect)

            # === Верхняя белая полоска ===
            top_line = QtWidgets.QGraphicsRectItem(
                QtCore.QRectF(x_pos - 6, y_pos - 8, text_width + 12, 2)
            )
            top_line.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
            top_line.setPen(QtGui.QPen(QtCore.Qt.NoPen))
            top_line.setZValue(0)
            self.scene.addItem(top_line)

            # === Сам текст ===
            status = self.scene.addText(text_string, font)
            status.setPos(x_pos, y_pos + text_offset_y)
            status.setDefaultTextColor(QtGui.QColor(255, 255, 255))
        except Exception as e:
            prints.printNotOk(f"Scene Update Error: {e}")
            QtWidgets.QApplication.quit()

    def is_game_window_active(self):
        hwnd = win32gui.FindWindow(None, "Counter-Strike 2")
        if hwnd:
            foreground_hwnd = win32gui.GetForegroundWindow()
            return hwnd == foreground_hwnd
        return False

def esp_main():
    settings = load_settings()
    app = QtWidgets.QApplication(sys.argv)
    window = ESPWindow(settings)
    window.show()
    sys.exit(app.exec())

# ===============================
# Trigger Bot Function
# ===============================
def triggerbot():
    offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json').json()
    client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json').json()
    
    dwEntityList = offsets['client.dll']['dwEntityList']
    dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
    m_iTeamNum = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iTeamNum']
    m_iIDEntIndex = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_iIDEntIndex']
    m_iHealth = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iHealth']

    mouse = Controller()

    default_settings_local = {
        "keyboards": "X",
        "trigger_bot_active": 1,
        "trigger_time": 100,  # Delay before shooting (in ms)
        "trigger_mode": 0,    # 0 - only enemies, 1 - for all
    }

    def load_settings_local():
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return default_settings_local

    def main_trigger(settings):
        pm = pymem.Pymem("cs2.exe")
        client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll

        while True:
            try:
                trigger_bot_active = settings.get("trigger_bot_active", 1)
                trigger_time = max(0.001, min(0.1, settings.get("trigger_time", 0.03)))  # Limit between 0.001 - 0.1 sec
                trigger_mode = settings.get("trigger_mode", 0)  # 0 - only enemies, 1 - for all
                keyboards = settings.get("keyboards", "X")

                if win32api.GetAsyncKeyState(ord(keyboards)):
                    if trigger_bot_active:
                        try:
                            player = pm.read_longlong(client + dwLocalPlayerPawn)
                            entityId = pm.read_int(player + m_iIDEntIndex)

                            if entityId > 0:
                                entList = pm.read_longlong(client + dwEntityList)
                                entEntry = pm.read_longlong(entList + 0x8 * (entityId >> 9) + 0x10)
                                entity = pm.read_longlong(entEntry + 120 * (entityId & 0x1FF))

                                entityTeam = pm.read_int(entity + m_iTeamNum)
                                playerTeam = pm.read_int(player + m_iTeamNum)

                                if (trigger_mode == 1) or (entityTeam != playerTeam):
                                    entityHp = pm.read_int(entity + m_iHealth)
                                    if entityHp > 0:
                                        mouse.press(Button.left)
                                        time.sleep(trigger_time)
                                        mouse.release(Button.left)
                        except Exception:
                            pass
                    time.sleep(0.01)
                else:
                    time.sleep(settings.get("trigger_time", 100) / 1000.0)
            except KeyboardInterrupt:
                break
            except Exception:
                time.sleep(1)

    def start_main_thread_trigger(settings):
        while True:
            main_trigger(settings)

    def setup_watcher_trigger(app, settings):
        watcher = QFileSystemWatcher()
        watcher.addPath(CONFIG_FILE)

        def reload_settings():
            new_settings = load_settings_local()
            settings.update(new_settings)

        watcher.fileChanged.connect(reload_settings)
        app.exec()

    def main_program_trigger():
        app = QCoreApplication(sys.argv)
        settings = load_settings_local()
        threading.Thread(target=start_main_thread_trigger, args=(settings,), daemon=True).start()
        setup_watcher_trigger(app, settings)

    main_program_trigger()

# ===============================
# Aim Bot Function
# ===============================
def aim():
    default_settings = {
        'esp_rendering': 1,
        'esp_mode': 1,
        'keyboard': "C",
        'aim_active': 1,
        'aim_mode': 1,
        'radius': 20,
        'aim_mode_distance': 1
    }

    def get_window_size(window_name="Counter-Strike 2"):
        hwnd = win32gui.FindWindow(None, window_name)
        if hwnd:
            rect = win32gui.GetClientRect(hwnd)
            return rect[2] - rect[0], rect[3] - rect[1]
        return 1920, 1080

    def load_settings_aim():
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return default_settings

    def get_offsets_and_client_dll_aim():
        offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json').json()
        client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json').json()
        return offsets, client_dll

    def esp_for_aim(pm, client, offsets, client_dll, settings, target_list, window_size):
        width, height = window_size
        if settings['aim_active'] == 0:
            return
        dwEntityList = offsets['client.dll']['dwEntityList']
        dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
        dwViewMatrix = offsets['client.dll']['dwViewMatrix']
        m_iTeamNum = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iTeamNum']
        m_lifeState = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_lifeState']
        m_pGameSceneNode = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_pGameSceneNode']
        m_modelState = client_dll['client.dll']['classes']['CSkeletonInstance']['fields']['m_modelState']
        m_hPlayerPawn = client_dll['client.dll']['classes']['CCSPlayerController']['fields']['m_hPlayerPawn']
        view_matrix = [pm.read_float(client + dwViewMatrix + i * 4) for i in range(16)]
        local_player_pawn_addr = pm.read_longlong(client + dwLocalPlayerPawn)
        try:
            local_player_team = pm.read_int(local_player_pawn_addr + m_iTeamNum)
        except:
            return
        entity_list = pm.read_longlong(client + dwEntityList)
        entity_ptr = pm.read_longlong(entity_list + 0x10)
    
        for i in range(1, 64):
            try:
                if entity_ptr == 0:
                    break
                entity_controller = pm.read_longlong(entity_ptr + 0x78 * (i & 0x1FF))
                if entity_controller == 0:
                    continue
                entity_controller_pawn = pm.read_longlong(entity_controller + m_hPlayerPawn)
                if entity_controller_pawn == 0:
                    continue
                entity_list_pawn = pm.read_longlong(entity_list + 0x8 * ((entity_controller_pawn & 0x7FFF) >> 0x9) + 0x10)
                if entity_list_pawn == 0:
                    continue
                entity_pawn_addr = pm.read_longlong(entity_list_pawn + 0x78 * (entity_controller_pawn & 0x1FF))
                if entity_pawn_addr == 0 or entity_pawn_addr == local_player_pawn_addr:
                    continue
                entity_team = pm.read_int(entity_pawn_addr + m_iTeamNum)
                if entity_team == local_player_team and settings['esp_mode'] == 0:
                    continue
                entity_alive = pm.read_int(entity_pawn_addr + m_lifeState)
                if entity_alive != 256:
                    continue
                game_scene = pm.read_longlong(entity_pawn_addr + m_pGameSceneNode)
                bone_matrix = pm.read_longlong(game_scene + m_modelState + 0x80)
                try:
                    bone_id = 6 if settings['aim_mode'] == 1 else 4
                    headX = pm.read_float(bone_matrix + bone_id * 0x20)
                    headY = pm.read_float(bone_matrix + bone_id * 0x20 + 0x4)
                    headZ = pm.read_float(bone_matrix + bone_id * 0x20 + 0x8)
                    head_pos = w2s(view_matrix, headX, headY, headZ, width, height)
                    legZ = pm.read_float(bone_matrix + 28 * 0x20 + 0x8)
                    leg_pos = w2s(view_matrix, headX, headY, legZ, width, height)
                    deltaZ = abs(head_pos[1] - leg_pos[1])
                    if head_pos[0] != -999 and head_pos[1] != -999:
                        if settings['aim_mode_distance'] == 1:
                            target_list.append({
                                'pos': head_pos,
                                'deltaZ': deltaZ
                            })
                        else:
                            target_list.append({
                                'pos': head_pos,
                                'deltaZ': None
                            })
                except Exception as e:
                    pass
            except:
                return
        return target_list

    def aimbot(target_list, radius, aim_mode_distance):
        if not target_list:
            return
        center_x = win32api.GetSystemMetrics(0) // 2
        center_y = win32api.GetSystemMetrics(1) // 2
        if radius == 0:
            closest_target = None
            closest_dist = float('inf')
            for target in target_list:
                dist = ((target['pos'][0] - center_x) ** 2 + (target['pos'][1] - center_y) ** 2) ** 0.5
                if dist < closest_dist:
                    closest_target = target['pos']
                    closest_dist = dist
        else:
            screen_radius = radius / 100.0 * min(center_x, center_y)
            closest_target = None
            closest_dist = float('inf')
            if aim_mode_distance == 1:
                target_with_max_deltaZ = None
                max_deltaZ = -float('inf')
                for target in target_list:
                    dist = ((target['pos'][0] - center_x) ** 2 + (target['pos'][1] - center_y) ** 2) ** 0.5
                    if dist < screen_radius and target['deltaZ'] > max_deltaZ:
                        max_deltaZ = target['deltaZ']
                        target_with_max_deltaZ = target
                closest_target = target_with_max_deltaZ['pos'] if target_with_max_deltaZ else None
            else:
                for target in target_list:
                    dist = ((target['pos'][0] - center_x) ** 2 + (target['pos'][1] - center_y) ** 2) ** 0.5
                    if dist < screen_radius and dist < closest_dist:
                        closest_target = target['pos']
                        closest_dist = dist
        if closest_target:
            target_x, target_y = closest_target
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(target_x - center_x), int(target_y - center_y), 0, 0)

    def main_aim(settings):
        offsets, client_dll = get_offsets_and_client_dll_aim()
        window_size = get_window_size()
        pm = pymem.Pymem("cs2.exe")
        client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
        while True:
            target_list = []
            target_list = esp_for_aim(pm, client, offsets, client_dll, settings, target_list, window_size)
            if win32api.GetAsyncKeyState(ord(settings['keyboard'])):
                aimbot(target_list, settings['radius'], settings['aim_mode_distance'])
            time.sleep(0.001)

    def start_main_thread_aim(settings):
        while True:
            main_aim(settings)

    def setup_watcher_aim(app, settings):
        watcher = QFileSystemWatcher()
        watcher.addPath(CONFIG_FILE)
        def reload_settings():
            new_settings = load_settings_aim()
            settings.update(new_settings)
        watcher.fileChanged.connect(reload_settings)
        app.exec()

    def main_program_aim():
        app = QCoreApplication(sys.argv)
        settings = load_settings_aim()
        threading.Thread(target=start_main_thread_aim, args=(settings,), daemon=True).start()
        setup_watcher_aim(app, settings)

    main_program_aim()

# ===============================
# ESP Tab
# ===============================
class ESPTabUI_New(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.init_ui()
    def init_ui(self):
        layout = QVBoxLayout()
        self.esp_rendering_cb = QCheckBox("Enable ESP")
        self.esp_rendering_cb.setStyleSheet("color: white;")
        self.esp_rendering_cb.setChecked(self.settings.get("esp_rendering", 0) == 1)
        self.esp_rendering_cb.stateChanged.connect(self.on_settings_changed)
        layout.addWidget(self.esp_rendering_cb)
        self.esp_mode_cb = QComboBox()
        self.esp_mode_cb.addItems(["Only Enemies", "All Players"])
        self.esp_mode_cb.setCurrentIndex(self.settings.get("esp_mode", 0))
        self.esp_mode_cb.setStyleSheet("""
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
        self.esp_mode_cb.currentIndexChanged.connect(self.on_settings_changed)
        layout.addWidget(self.esp_mode_cb)
        self.line_rendering_cb = QCheckBox("Draw Lines")
        self.line_rendering_cb.setStyleSheet("color: white;")
        self.line_rendering_cb.setChecked(self.settings.get("line_rendering", 0) == 1)
        self.line_rendering_cb.stateChanged.connect(self.on_settings_changed)
        layout.addWidget(self.line_rendering_cb)
        self.hp_bar_rendering_cb = QCheckBox("Draw HP Bars")
        self.hp_bar_rendering_cb.setStyleSheet("color: white;")
        self.hp_bar_rendering_cb.setChecked(self.settings.get("hp_bar_rendering", 0) == 1)
        self.hp_bar_rendering_cb.stateChanged.connect(self.on_settings_changed)
        layout.addWidget(self.hp_bar_rendering_cb)
        self.head_hitbox_rendering_cb = QCheckBox("Draw Head Hitbox")
        self.head_hitbox_rendering_cb.setStyleSheet("color: white;")
        self.head_hitbox_rendering_cb.setChecked(self.settings.get("head_hitbox_rendering", 0) == 1)
        self.head_hitbox_rendering_cb.stateChanged.connect(self.on_settings_changed)
        layout.addWidget(self.head_hitbox_rendering_cb)
        self.bons_cb = QCheckBox("Draw Bones")
        self.bons_cb.setStyleSheet("color: white;")
        self.bons_cb.setChecked(self.settings.get("bons", 0) == 1)
        self.bons_cb.stateChanged.connect(self.on_settings_changed)
        layout.addWidget(self.bons_cb)
        self.nickname_cb = QCheckBox("Show Nickname")
        self.nickname_cb.setStyleSheet("color: white;")
        self.nickname_cb.setChecked(self.settings.get("nickname", 0) == 1)
        self.nickname_cb.stateChanged.connect(self.on_settings_changed)
        layout.addWidget(self.nickname_cb)
        self.weapon_cb = QCheckBox("Show Weapon")
        self.weapon_cb.setStyleSheet("color: white;")
        self.weapon_cb.setChecked(self.settings.get("weapon", 0) == 1)
        self.weapon_cb.stateChanged.connect(self.on_settings_changed)
        layout.addWidget(self.weapon_cb)
        self.bomb_esp_cb = QCheckBox("Bomb ESP")
        self.bomb_esp_cb.setStyleSheet("color: white;")
        self.bomb_esp_cb.setChecked(self.settings.get("bomb_esp", 0) == 1)
        self.bomb_esp_cb.stateChanged.connect(self.on_settings_changed)
        layout.addWidget(self.bomb_esp_cb)
        self.setLayout(layout)
        self.setStyleSheet("background-color: #404040; border-radius: 10px; padding: 10px;")
    def on_settings_changed(self):
        self.settings["esp_rendering"] = 1 if self.esp_rendering_cb.isChecked() else 0
        self.settings["esp_mode"] = self.esp_mode_cb.currentIndex()
        self.settings["line_rendering"] = 1 if self.line_rendering_cb.isChecked() else 0
        self.settings["hp_bar_rendering"] = 1 if self.hp_bar_rendering_cb.isChecked() else 0
        self.settings["head_hitbox_rendering"] = 1 if self.head_hitbox_rendering_cb.isChecked() else 0
        self.settings["bons"] = 1 if self.bons_cb.isChecked() else 0
        self.settings["nickname"] = 1 if self.nickname_cb.isChecked() else 0
        self.settings["weapon"] = 1 if self.weapon_cb.isChecked() else 0
        self.settings["bomb_esp"] = 1 if self.bomb_esp_cb.isChecked() else 0
        save_settings(self.settings)

# ===============================
# Legit (Aim) Tab
# ===============================
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

# ===============================
# Trigger Tab
# ===============================
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

# ===============================
# Settings Tab
# ===============================
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
        slider = QSlider(Qt.Horizontal)
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
            "bone": "bone_color",
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

# ===============================
# Misc Tab
# ===============================
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
        if self.settings["anti_flash"]:
            try:
                pm = pymem.Pymem("cs2.exe")
                client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
                player = pm.read_longlong(client + offsets['client.dll']['dwLocalPlayerPawn'])
                pm.write_int(player + m_flFlashMaxAlpha, 0)
            except:
                prints.printNotOk("Failed to enable anti-flash.")
        else:
            try:
                pm = pymem.Pymem("cs2.exe")
                client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
                player = pm.read_longlong(client + offsets['client.dll']['dwLocalPlayerPawn'])
                pm.write_int(player + m_flFlashMaxAlpha, 1132396544)
            except:
                prints.printNotOk("Failed to disable anti-flash.")
    def on_unsafe_changed(self):
        self.settings["unsafe"] = 1 if self.unsafe_cb.isChecked() else 0
        save_settings(self.settings)

offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json').json()
client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json').json()
dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
m_flFlashMaxAlpha = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_flFlashMaxAlpha']

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VacBanBETA")
        self.setGeometry(100, 100, 400, 300)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.addTab(ESPTabUI_New(), "ESP")
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
            "VacBan is a custom tool for Counter-Strike 2 developed by a passionate coder. "
            "It integrates advanced features such as an ESP overlay, aim lock, and a trigger bot "
            "to enhance your gaming experience.\n\n"
            "Built with Python and PySide6, this tool is provided for educational purposes only. "
            "Use it responsibly and at your own risk.\n\n"
            "Enjoy and have fun!"
        )
        label.setText(about_text)
        layout.addWidget(label)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)
        dialog.setLayout(layout)
        dialog.exec()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.setWindowOpacity(0.72)
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.setWindowOpacity(1.0)
            event.accept()

    def resizeEvent(self, event: QtGui.QResizeEvent):
        super().resizeEvent(event)
        self.about_button.move(self.width() - self.about_button.width() - 10, 5)

# =============
# Main Launch
# =============
if __name__ == "__main__":
    prints.println("Checking version...")
    time.sleep(0.35)
    if_ok = check_for_update.check(version=0.1)
    if if_ok:
        prints.println("You have the latest version!")
        time.sleep(1)
        clear_console()
        print(rf"""{Fore.LIGHTYELLOW_EX}Github - https://github.com/VacBanProject/VacBan-Cheat
Discord - ggroltonuser and qqgtr_r34
Telegram - t.me/ggroltonshop
        """)
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
        # Start separate processes for ESP, Trigger Bot, and Aim Bot
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
        global insert_pressed
        insert_pressed = False
        def check_insert():
            """
            Checks if the Insert key is pressed to toggle the GUI menu visibility.
            """
            global insert_pressed
            is_pressed = (win32api.GetAsyncKeyState(0x2D) & 0x8000) != 0
            if is_pressed and not insert_pressed:
                insert_pressed = True
                if main_window.isVisible():
                    main_window.hide()
                    QApplication.setOverrideCursor(Qt.BlankCursor)
                else:
                    main_window.show()
                    QApplication.setOverrideCursor(Qt.ArrowCursor)
            elif not is_pressed and insert_pressed:
                insert_pressed = False
        insert_timer = QtCore.QTimer()
        insert_timer.timeout.connect(check_insert)
        insert_timer.start(100)
        gui_result = gui_app.exec()
        process_esp.join()
        process_trigger.join()
        process_aim.join()
        sys.exit(gui_result)

    else:
      prints.println("You have the wrong version!")
      time.sleep(1)
      prints.println("Install the latest version here: https://github.com/VacBanProject/VacBan-Cheat")
      time.sleep(0.4)
      prints.inputln("Press enter to exit...")
