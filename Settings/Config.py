import os
import json
import requests

# Пути для конфига
CONFIG_DIR = os.path.join(os.environ['LOCALAPPDATA'], 'VAC Ban Cheat', 'configs')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

# Значения по умолчанию
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
    "Lines_color_enemy": [255, 255, 255],
    "Box_color_enemy": [255, 255, 255],
    "head_circle_color_team": [71, 167, 106],
    "nick_color_team": [71, 167, 106],
    "gun_color_team": [71, 167, 106],
    "bone_color_team": [0, 255, 0],
    "Lines_color_team": [255, 255, 255],
    "Box_color_team": [255, 255, 255],
    "Tracer_color_team": [255, 255, 255],
    "trigger_time": 100,
    "trigger_mode": 0,
    "aim_active": 1,
    "radius": 20,
    "aim_mode": 1,
    "aim_mode_distance": 1
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
        if os.stat(CONFIG_FILE).st_size == 0:
            with open(CONFIG_FILE, "w") as f:
                json.dump(DEFAULT_SETTINGS, f, indent=4)
        settings = DEFAULT_SETTINGS.copy()
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
