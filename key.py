# gives you the steam guard code for your steam account (steam shared secret necessary)

import base64
import hashlib
import hmac
import math
import time
import sched

# Your Steam Guard shared secret (base64-encoded)
SHARED_SECRET = ""

def get_steam_guard_code(shared_secret, for_time=None):
    if for_time is None:
        for_time = int(time.time())

    # Decode the shared secret from base64 to bytes
    secret = base64.b64decode(shared_secret)

    # Steam Guard codes change every 30 seconds
    time_interval = int(for_time / 30)

    # Pack time_interval as 8-byte big-endian
    time_bytes = time_interval.to_bytes(8, byteorder='big')

    # HMAC-SHA1 using secret key and time bytes
    hmac_hash = hmac.new(secret, time_bytes, hashlib.sha1).digest()

    # Dynamic truncation to get 4 bytes from hash
    offset = hmac_hash[19] & 0x0F
    truncated_hash = hmac_hash[offset:offset + 4]

    # Convert bytes to integer
    code_int = int.from_bytes(truncated_hash, byteorder='big') & 0x7FFFFFFF

    # Steam uses a custom charset for the 5-char code
    charset = "23456789BCDFGHJKMNPQRTVWXY"
    code = ''

    for _ in range(5):
        code += charset[code_int % len(charset)]
        code_int //= len(charset)

    # Return code and time left until next code
    time_left = 30 - (for_time % 30)
    return code, time_left


def main():
    scheduler = sched.scheduler(time.time, time.sleep)

    def print_code():
        code, time_left = get_steam_guard_code(SHARED_SECRET)
        print(f"Steam Guard Code: {code} | Refresh in {time_left}s", end='\r', flush=True)
        scheduler.enter(1, 1, print_code)

    scheduler.enter(1, 1, print_code)
    scheduler.run()


if __name__ == "__main__":
    main()
