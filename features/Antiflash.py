import requests
import pymem
import pymem.process

offsets_url = "https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json"
client_dll_url = "https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json"

offsets_json = requests.get(offsets_url).json()
client_dll_json = requests.get(client_dll_url).json()

dwLocalPlayerPawn = offsets_json["client.dll"]["dwLocalPlayerPawn"]

try:
    m_flFlashMaxAlpha = client_dll_json["client.dll"]["classes"]["C_BaseEntity"]["fields"]["m_flFlashMaxAlpha"]
except KeyError:
    print("Не найден ключ m_flFlashMaxAlpha в JSON, используется значение по умолчанию 5128")
    m_flFlashMaxAlpha = 5128

pm = pymem.Pymem("cs2.exe")
client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll

player = pm.read_longlong(client + dwLocalPlayerPawn)

def enable():
    pm.write_int(player + m_flFlashMaxAlpha, 0)

def disable():
    pm.write_int(player + m_flFlashMaxAlpha, 1132396544)

if __name__ == '__main__':
    while True:
        input("Нажмите Enter для отключения ослепления...")
        enable()
        input("Нажмите Enter для восстановления ослепления...")
        disable()
