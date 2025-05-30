# Lists all installed Plug and Play device drivers on Windows with their name, version, and date using WMI.

import wmi

w = wmi.WMI()
for driver in w.Win32_PnPSignedDriver():
    print(f"Device: {driver.DeviceName}")
    print(f"Driver Version: {driver.DriverVersion}")
    print(f"Driver Date: {driver.DriverDate}")
    print('-' * 40)
