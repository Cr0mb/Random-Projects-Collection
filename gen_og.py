# fake gift card generator

import time
import random
import os
import subprocess
import threading
import requests
import base64
import hashlib
from colorama import Fore, Style, init
from cryptography.fernet import Fernet

init(autoreset=True)

ACCESS_PASSWORD = "Sqat_Rot_Carder"
CHAR_SET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
CARD_FORMATS = {
    "minecraft": [4, 4, 4], "paypal": [4, 4, 4], "playstation": [4, 4, 4],
    "amazon": [4, 6, 4], "netflix": [4, 6, 4], "steam": [4, 6, 5],
    "fortnite": [5, 4, 4], "roblox": [3, 3, 4], "itunes": [16],
    "ebay": [10], "imvu": [10], "webkinz": [8], "pokemontgc": [3, 4, 3, 3],
    "playstore": [4, 4, 4, 4, 4], "xbox": [5, 5, 5, 5, 5]
}
CARD_OPTIONS = list(CARD_FORMATS.keys())
SAVE_FILE = "valid_wallets.enc"

def clear_screen():
    os.system('cls')  # For Windows

def generate_code(pattern):
    return "-".join("".join(random.choice(CHAR_SET) for _ in range(section)) for section in pattern)

def generate_fake_balance():
    return round(random.uniform(0.00, 100.00) if random.random() < 0.05 else 0.00, 2)

def derive_key(password):
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

def encrypt_data(data, password):
    key = derive_key(password)
    cipher = Fernet(key)
    return cipher.encrypt(data.encode())

def decrypt_data(encrypted_data, password):
    key = derive_key(password)
    cipher = Fernet(key)
    return cipher.decrypt(encrypted_data).decode()

def save_wallets_to_file(wallets):
    if wallets:
        encrypted_data = encrypt_data("\n".join(wallets), ACCESS_PASSWORD)
        with open(SAVE_FILE, "wb") as file:
            file.write(encrypted_data)

def view_saved_wallets():
    if not os.path.exists(SAVE_FILE):
        print(Fore.RED + "\n[!] No saved wallets found!\n")
        return

    entered_password = input(Fore.YELLOW + "Enter password to view saved gift cards:\n> " + Fore.RESET).strip()
    if entered_password != ACCESS_PASSWORD:
        print(Fore.RED + "\n[!] Access Denied! Returning to menu...\n")
        time.sleep(1)
        return

    try:
        with open(SAVE_FILE, "rb") as file:
            encrypted_data = file.read()

        decrypted_data = decrypt_data(encrypted_data, entered_password)
        print(Fore.CYAN + "\n════════════════════════════════════════")
        print(Fore.MAGENTA + "      SAVED GIFT CARD BALANCES        ")
        print(Fore.CYAN + "════════════════════════════════════════\n")
        print(Fore.LIGHTYELLOW_EX + decrypted_data)
        print(Fore.CYAN + "\n════════════════════════════════════════")

    except Exception:
        print(Fore.RED + "\n[!] Error decrypting file. Invalid password or corrupt file.\n")

    input(Fore.YELLOW + "\nPress Enter to return to the main menu...")
    clear_screen()

def generate_codes():
    display_card_list()
    card_type = get_valid_card_choice()
    count = get_valid_integer("\nHow many codes do you want to generate?\n> ")

    clear_screen()
    print(Fore.MAGENTA + "\nGenerating codes... (Press CTRL+C to cancel and return to the menu)\n")

    all_wallets_with_balance = []  # List to store wallets with non-zero balance

    try:
        for _ in range(count):
            code = generate_code(CARD_FORMATS[card_type])
            balance = generate_fake_balance()
            time.sleep(random.uniform(0.3, 0.8))

            balance_msg = Fore.LIGHTYELLOW_EX + Style.BRIGHT + "Gift Balance Found!" if balance > 0 else Fore.GREEN
            wallet_with_balance = f"{code}  |  Balance: ${balance:.2f}"

            print(balance_msg + wallet_with_balance)

            # Save only wallets with balance greater than 0
            if balance > 0:
                all_wallets_with_balance.append(wallet_with_balance)

        save_wallets_to_file(all_wallets_with_balance)

        print(Fore.CYAN + "\n╔══════════════════════════════════════╗")
        print(Fore.MAGENTA + "║       GENERATION COMPLETED           ║")
        print(Fore.CYAN + "╚══════════════════════════════════════╝\n")
        time.sleep(3)
        clear_screen()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Operation interrupted. Returning to menu...\n")
        time.sleep(1)
        return


def display_menu():
    print(Fore.CYAN + Style.BRIGHT + "\n╔══════════════════════════════════════╗")
    print(Fore.MAGENTA + "║          GIFT CARD GENERATOR         ║")
    print(Fore.CYAN + "╠══════════════════════════════════════╣")
    print(Fore.YELLOW + "║          1) Generate Gift Cards      ║")
    print(Fore.YELLOW + "║          2) View Saved Gift Cards    ║")
    print(Fore.YELLOW + "║          3) Exit                     ║")
    print(Fore.CYAN + "╚══════════════════════════════════════╝\n")

def display_card_list():
    print(Fore.YELLOW + "Available Gift Cards:\n")
    for i, card in enumerate(CARD_OPTIONS, 1):
        print(Fore.GREEN + f" [{i}] {card.capitalize()}".ljust(30), end="  " if i % 2 == 0 else "\n")
    print("\n" + Fore.CYAN + "════════════════════════════════════════\n")

def get_valid_card_choice():
    while True:
        user_input = input(Fore.CYAN + "Select a gift card (number or name):\n> " + Fore.RESET).strip().lower()
        if user_input.isdigit():
            index = int(user_input) - 1
            if 0 <= index < len(CARD_OPTIONS):
                return CARD_OPTIONS[index]
        elif user_input in CARD_FORMATS:
            return user_input
        print(Fore.RED + "[ERROR] Invalid selection.")

def get_valid_integer(prompt):
    while True:
        user_input = input(Fore.CYAN + prompt + Fore.RESET).strip()
        if user_input.isdigit() and int(user_input) > 0:
            return int(user_input)
        print(Fore.RED + "[ERROR] Please enter a valid positive integer.")
        clear_screen()

def main():
    while True:
        display_menu()
        choice = input(Fore.CYAN + "Select an option (1-3):\n> " + Fore.RESET).strip()
        if choice == "1":
            generate_codes()
        elif choice == "2":
            view_saved_wallets()
        elif choice == "3":
            print(Fore.YELLOW + "\nExiting. Have a great day!\n")
            break
        else:
            print(Fore.RED + "[ERROR] Invalid choice!")

if __name__ == "__main__":
    main()
