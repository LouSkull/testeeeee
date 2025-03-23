
import ctypes

def write_memory(pid, address, data):
    process = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, pid)
    buffer = ctypes.create_string_buffer(data)
    bytesWritten = ctypes.c_size_t()
    ctypes.windll.kernel32.WriteProcessMemory(process, address, buffer, len(data), ctypes.byref(bytesWritten))
    ctypes.windll.kernel32.CloseHandle(process)
