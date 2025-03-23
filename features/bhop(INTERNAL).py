import pymem
import pymem.process
import time
import os
import ctypes
import logging
import sys
import requests
from colorama import init, Fore

init(autoreset=True)

KEY_SPACE = 0x20
KEY_TOGGLE = 0x75  # F6
FORCE_JUMP_ACTIVE = 65537
FORCE_JUMP_INACTIVE = 256

class Logger:
    LOG_DIRECTORY = os.path.join(os.environ['LOCALAPPDATA'], 'temp', 'VacBan', 'xjfhskdowlqp')
    LOG_FILE = os.path.join(LOG_DIRECTORY, 'unsafeFunctions.log')

    @staticmethod
    def setup_logging():
        os.makedirs(Logger.LOG_DIRECTORY, exist_ok=True)
        with open(Logger.LOG_FILE, 'w'):
            pass

        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s: %(message)s',
            handlers=[logging.FileHandler(Logger.LOG_FILE), logging.StreamHandler()]
        )

class Utility:
    @staticmethod
    def fetch_offsets():
        url = "https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/buttons.hpp"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            offsets = response.text
            for line in offsets.splitlines():
                if "jump" in line:
                    offset_str = line.split('=')[-1].strip().rstrip(';')
                    try:
                        offset = int(offset_str, 16)
                        return offset
                    except ValueError as ve:
                        logging.error(f"{Fore.RED}[ VAC ] Could not convert '{offset_str}' into an integer: {ve}")
                        return None
            logging.error(f"{Fore.RED}[ VAC ] No jump offset found in retrieved data.")
        except requests.RequestException as re:
            logging.error(f"{Fore.RED}[ VAC ] Could not retrieve offsets from {url}: {re}")
        except Exception as e:
            logging.error(f"{Fore.RED}[ VAC ] An unexpected error occurred while getting offsets: {e}")
        return None

class Bhop:
    def __init__(self):
        self.pm = None
        self.dwForceJump = Utility.fetch_offsets()
        if self.dwForceJump is None:
            logging.error(f"{Fore.RED}[ VAC ] Offset retrieval failed. Exiting...")
            sys.exit(1)
        self.client_base = None
        self.force_jump_address = None
        self.bhop_enabled = True

    def initialize_pymem(self):
        try:
            self.pm = pymem.Pymem("cs2.exe")
            logging.info(f"{Fore.GREEN}[ VAC ] Successfully connected to cs2.exe.")
            return True
        except pymem.exception.ProcessNotFound:
            logging.error(f"{Fore.RED}[ VAC ] cs2.exe is not running. Please start the game.")
        except pymem.exception.PymemError as pe:
            logging.error(f"{Fore.RED}[ VAC ] Pymem encountered an issue: {pe}")
        except Exception as e:
            logging.error(f"{Fore.RED}[ VAC ] Unexpected error while initializing Pymem: {e}")
        return False

    def get_client_module(self):
        try:
            client_module = pymem.process.module_from_name(self.pm.process_handle, "client.dll")
            if not client_module:
                raise pymem.exception.ModuleNotFoundError("client.dll not found")
            self.client_base = client_module.lpBaseOfDll
            self.force_jump_address = self.client_base + self.dwForceJump
            logging.info(f"{Fore.GREEN}[ VAC ] Found client.dll. Jump address is set.")
            return True
        except pymem.exception.ModuleNotFoundError as mnfe:
            logging.error(f"{Fore.RED}[ VAC ] Error: {mnfe}. Make sure client.dll is loaded.")
        except Exception as e:
            logging.error(f"{Fore.RED}[ VAC ] Something went wrong while accessing client module: {e}")
        return False

    def toggle_bhop(self):
        self.bhop_enabled = not self.bhop_enabled
        state = "enabled" if self.bhop_enabled else "disabled"
        logging.info(f"{Fore.YELLOW}[ VAC ] Bunnyhop {state}.")

    def start(self):
        logging.info(f"{Fore.YELLOW}[ VAC ] Preparing to attach to cs2.exe and locate client module...")

        if not self.initialize_pymem() or not self.get_client_module():
            logging.error(f"{Fore.RED}[ VAC ] Could not complete setup. Exiting...")
            input("Press Enter to close...")
            return

        logging.info(f"{Fore.CYAN}[ VAC ] Bunnyhop is active! Press F6 to toggle on/off.")
        is_jumping = False

        try:
            while True:
                if ctypes.windll.user32.GetAsyncKeyState(KEY_TOGGLE) & 0x8000:
                    self.toggle_bhop()
                    time.sleep(0.3)
                
                if self.bhop_enabled and (ctypes.windll.user32.GetAsyncKeyState(KEY_SPACE) & 0x8000):
                    if not is_jumping:
                        time.sleep(0.01)
                        self.pm.write_int(self.force_jump_address, FORCE_JUMP_ACTIVE)
                        is_jumping = True
                    else:
                        time.sleep(0.01)
                        self.pm.write_int(self.force_jump_address, FORCE_JUMP_INACTIVE)
                        is_jumping = False
                else:
                    time.sleep(0.005)
        except KeyboardInterrupt:
            logging.info(f"{Fore.YELLOW}[ VAC ] Bunnyhop process stopped by user.")
        except Exception as e:
            logging.error(f"{Fore.RED}[ VAC ] A critical error occurred in the Bunnyhop loop: {e}")
            input("Press Enter to close...")

if __name__ == "__main__":
    Logger.setup_logging()
    bhop = Bhop()
    bhop.start()
