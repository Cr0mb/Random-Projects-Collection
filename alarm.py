# Cross-platform alarm script that waits until 6:30 A.M. and plays a system-specific wake-up sound.

import datetime
import time
import platform
import os

def play_default_sound():
    system = platform.system()

    if system == "Windows":
        import winsound
        duration = 1000  # milliseconds
        freq = 1000      # Hz
        for _ in range(3):  # Beep 3 times
            winsound.Beep(freq, duration)
            time.sleep(0.5)
    elif system == "Darwin":
        os.system('say "Wake up! It is 6 30 A M"')
    elif system == "Linux":
        if os.system("which beep > /dev/null 2>&1") == 0:
            os.system("beep -f 1000 -l 1000 -r 3")
        else:
            print("[!] No sound program found. Install 'beep' or use 'say' for audio feedback.")
    else:
        print("[!] Unknown OS - cannot play default sound.")

# Set target time for 6:30 A.M. tomorrow
now = datetime.datetime.now()
alarm_time = now.replace(hour=6, minute=30, second=0, microsecond=0)
if alarm_time < now:
    alarm_time += datetime.timedelta(days=1)

print(f"[+] Alarm set for {alarm_time.strftime('%Y-%m-%d %H:%M:%S')}")

# Wait until the alarm time
while datetime.datetime.now() < alarm_time:
    time.sleep(10)

# Alarm triggered
print("[!] Wake up! It's 6:30 A.M!")
play_default_sound()
