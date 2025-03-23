import os, ctypes

def clear_console():
  os.system('cls' if os.name=='nt' else 'clear')

def change_title(title):
  ctypes.windll.kernel32.SetConsoleTitleW(title)

