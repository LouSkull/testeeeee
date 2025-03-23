
import ctypes

def read_memory(pid, address, size):
    process = ctypes.windll.kernel32.OpenProcess(0x10, False, pid)
    buffer = ctypes.create_string_buffer(size)
    bytesRead = ctypes.c_size_t()
    ctypes.windll.kernel32.ReadProcessMemory(process, address, buffer, size, ctypes.byref(bytesRead))
    ctypes.windll.kernel32.CloseHandle(process)
    return buffer.raw
