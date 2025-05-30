# No fall script for minecraft bedrock

import ctypes
import win32api
import win32con
import win32process
import struct
import psutil

PROCESS_ALL_ACCESS = 0x1F0FFF

def get_pid(process_name):
    for proc in psutil.process_iter():
        if proc.name() == process_name:
            return proc.pid
    return None

def open_process(pid):
    return ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)

def enum_process_modules(process_handle):
    module_list = []
    h_module_snap = ctypes.windll.kernel32.CreateToolhelp32Snapshot(0x00000008, process_handle)  # TH32CS_SNAPMODULE
    module_entry = MODULEENTRY32()
    module_entry.dwSize = ctypes.sizeof(MODULEENTRY32)
    if ctypes.windll.kernel32.Module32First(h_module_snap, ctypes.byref(module_entry)):
        while ctypes.windll.kernel32.Module32Next(h_module_snap, ctypes.byref(module_entry)):
            module_list.append(module_entry)
    return module_list

class MODULEENTRY32(ctypes.Structure):
    _fields_ = [("dwSize", ctypes.c_ulong),
                ("th32ModuleID", ctypes.c_ulong),
                ("th32ProcessID", ctypes.c_ulong),
                ("GlblcntUsage", ctypes.c_ulong),
                ("ProccntUsage", ctypes.c_ulong),
                ("modBaseAddr", ctypes.POINTER(ctypes.c_ulong)),
                ("modBaseSize", ctypes.c_ulong),
                ("hModule", ctypes.c_void_p),
                ("szModule", ctypes.c_char * 256),
                ("szExePath", ctypes.c_char * 260)]

def aob_scan(process_handle, module_base, module_size, aob_pattern):
    aob = bytes.fromhex(aob_pattern.replace(" ", ""))
    buffer = ctypes.create_string_buffer(module_size)
    bytesRead = ctypes.c_size_t()
    ctypes.windll.kernel32.ReadProcessMemory(process_handle, module_base, buffer, module_size, ctypes.byref(bytesRead))
    for i in range(module_size - len(aob)):
        if buffer.raw[i:i+len(aob)] == aob:
            return module_base + i
    return None

def inject_code(process_handle, injection_address, shellcode):
    # Allocate memory
    alloc_address = ctypes.windll.kernel32.VirtualAllocEx(
        process_handle, 0, len(shellcode), win32con.MEM_COMMIT, win32con.PAGE_EXECUTE_READWRITE)

    # Write shellcode to allocated memory
    written = ctypes.c_size_t()
    ctypes.windll.kernel32.WriteProcessMemory(
        process_handle, alloc_address, shellcode, len(shellcode), ctypes.byref(written))

    # Overwrite original instructions with a jump to shellcode
    rel_jump = alloc_address - (injection_address + 5)
    jump_instr = b'\xE9' + struct.pack('<i', rel_jump)  # JMP
    padding = b'\x90' * (6 - len(jump_instr))  # NOPs to fill original bytes
    patch = jump_instr + padding
    ctypes.windll.kernel32.WriteProcessMemory(
        process_handle, injection_address, patch, len(patch), ctypes.byref(written))

    return alloc_address

# -----------------------------

process_name = "Minecraft.Windows.exe"
aob = "F3 0F 11 44 87 74"  # Your signature

pid = get_pid(process_name)
if not pid:
    print("Minecraft not running.")
    exit()

handle = open_process(pid)

# Get the base address of the module
modules = enum_process_modules(handle)
module_base = None
for module in modules:
    if module.szModule.decode() == "Minecraft.Windows.exe":
        module_base = ctypes.cast(module.modBaseAddr, ctypes.POINTER(ctypes.c_ulong)).contents.value
        module_size = module.modBaseSize
        break

if not module_base:
    print("Module base not found.")
    exit()

# Step 1: Find AoB location
target_address = aob_scan(handle, module_base, module_size, aob)
if not target_address:
    print("AoB pattern not found.")
    exit()

print(f"Found injection point at: {hex(target_address)}")

# Step 2: Prepare your shellcode (x64 assembly, compiled to bytes)
# You’d use a tool like x64dbg or a hex editor to prepare this
# For example:
shellcode = b"\xF3\x0F\x58\x05\xAA\xAA\xAA\xAA" \
            b"\xF3\x0F\x11\x44\x87\x74" \
            b"\xE9\xBB\xBB\xBB\xBB"  # <-- JMP back to original code + NOPs

# Step 3: Inject code
alloc = inject_code(handle, target_address, shellcode)
print(f"Injected code at: {hex(alloc)}")
