import pymem
import pymem.process
import requests
from Settings.Config import get_offsets_and_client_dll

def set_anti_flash(enable=True):
    offsets, client_dll = get_offsets_and_client_dll()
    dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
    m_flFlashMaxAlpha = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_flFlashMaxAlpha']
    try:
        pm = pymem.Pymem("cs2.exe")
        client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
        player = pm.read_longlong(client + dwLocalPlayerPawn)
        if enable:
            pm.write_int(player + m_flFlashMaxAlpha, 0)
        else:
            pm.write_int(player + m_flFlashMaxAlpha, 1132396544)
    except Exception as e:
        print("Failed to set anti-flash:", e)
