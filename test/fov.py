import pymem
import pymem.process

pm = pymem.Pymem("cs2.exe")

# Get the all what i need
client = pymem.process.module_from_name(pm.process_handle, "client.dll") # client
dwLocalPlayerController = pm.read_longlong(client.lpBaseOfDll + 0x1A89E90) # local player

# Read + change memory, or basically change fov
pm.write_int(dwLocalPlayerController + 0x6F4,120)
