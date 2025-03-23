# Main.py для Settings
from .Config import load_settings, save_settings

if __name__ == "__main__":
    settings = load_settings()
    print("Current settings:")
    print(settings)
