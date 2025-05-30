# verifying offsets for half life 2 deathmatch (outdated)

import pymem
import pymem.process

# Offsets
LocalPlayer = 0x4E7C64
EntityList = 0x4478FC
pjump = 0x507ED4

# Netvars
m_iHealth = 0x90
m_lifestate = 0x8F
m_flMaxspeed = 0x10E0
m_iFlags = 0x34C
m_iHidehud = 0x3C
m_flFOVRate = 0x40
m_vecPunchAngle = 0x6C
m_IDefaultFov = 0x1048
m_iFov = 0x103C
m_iFovStart = 0x1040
m_flFOVTime = 0x1044

def read_offset(pm, address, description, read_type="int"):
    try:
        if read_type == "int":
            value = pm.read_int(address)
        elif read_type == "float":
            value = pm.read_float(address)
        else:
            value = pm.read_bytes(address, 4)
        print(f"{description} at 0x{address:X} = {value}")
    except Exception as e:
        print(f"Failed to read {description} at 0x{address:X}: {e}")

def main():
    try:
        pm = pymem.Pymem("hl2.exe")  # or "hl2dm.exe"
        client_module = pymem.process.module_from_name(pm.process_handle, "client.dll")
        client_base = client_module.lpBaseOfDll

        print(f"[+] Client base: 0x{client_base:X}")

        local_player_ptr = pm.read_int(client_base + LocalPlayer)
        print(f"[+] Local Player address: 0x{local_player_ptr:X}")

        # Try reading some known fields
        read_offset(pm, local_player_ptr + m_iHealth, "Health")
        read_offset(pm, local_player_ptr + m_lifestate, "Life State")
        read_offset(pm, local_player_ptr + m_flMaxspeed, "Max Speed", read_type="float")
        read_offset(pm, local_player_ptr + m_iFlags, "Flags")

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
