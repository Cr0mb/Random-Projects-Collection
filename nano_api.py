# Shows nano pool information for monero / xmr mining pool

import urllib.request
import json
from colorama import Fore, Style, init
import pyfiglet
import time

# Initialize colorama
init(autoreset=True)

def clear_screen():
    print("\033c", end="")  # ANSI escape code to reset the terminal (works in most terminals)

def print_title():
    # Print the title using pyfiglet
    title = pyfiglet.figlet_format("Palace")
    print(Fore.MAGENTA + title)
    print(Fore.YELLOW + "Black Hat Services")

def get_nanopool_data(account):
    base_url = "https://api.nanopool.org/v1/xmr"
    
    endpoints = {
        "balance": f"{base_url}/balance/{account}",
        "avg_hashrate": f"{base_url}/avghashrate/{account}",
        "current_hashrate": f"{base_url}/hashrate/{account}",
        "workers": f"{base_url}/workers/{account}"
    }
    
    data = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for key, url in endpoints.items():
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                data[key] = json.load(response).get("data", "N/A")
        except urllib.error.URLError as e:
            print(Fore.RED + f"Error fetching {key}: {e}")
            data[key] = "N/A"
    
    return data

def count_underscore_addresses(workers):
    underscore_addresses = [worker.get("id", "") for worker in workers if "_" in worker.get("id", "")]
    print(Fore.GREEN + f"\n[+] Total Addresses: {len(underscore_addresses)}")
    for addr in underscore_addresses:
        print(f"  - {addr}")

def display_worker_info(workers):
    underscore_workers = [worker for worker in workers if "_" in worker.get('id', '')]
    sorted_workers = sorted(underscore_workers, key=lambda x: x.get('hashrate', 0), reverse=True)

    print(Fore.CYAN + "\n[+] Worker Details (Underscore Addresses, Sorted by Hashrate):")
    for worker in sorted_workers:
        print(Fore.YELLOW + f"  {worker.get('id', 'N/A')} | Last Share: {worker.get('lastShare', 'N/A')}s | Rating: {worker.get('rating', 'N/A')} | Hashrate: {worker.get('hashrate', 'N/A')} H/s")

def main():
    print_title()  # Print the title at the start

    account = "82WFpBT3pLrBHDHXpe5TL2cQLEepYDieiDMZADyb3pHLd8oQCrMLs44WCi8vBN3aT8AkbRXnhry5JFEdyS9nzWSP6jDNWn1"
    
    while True:
        data = get_nanopool_data(account)
        
        print(Fore.BLUE + "\n========== Account Summary ==========")
        print(Fore.GREEN + f"[+] Current Hashrate: {data['current_hashrate']} H/s")
        # print(Fore.GREEN + f"[+] Average Hashrate: {data['avg_hashrate']} H/s")
        print(Fore.YELLOW + f"[+] Balance: {data['balance']} XMR")
        print(Fore.BLUE + "=====================================")
        
        workers = data['workers'] if isinstance(data['workers'], list) else []
        count_underscore_addresses(workers)
        display_worker_info(workers)
        
        time.sleep(60)
        clear_screen()
        # while True:
          #   user_input = input(Fore.CYAN + "\nDo you want to refresh the data? (y/n): ").strip().lower()
            # if user_input == 'y':
              #   break
            # elif user_input == 'n':
              #   print(Fore.RED + "Exiting the program.")
                # return
            # else:
              #   print(Fore.RED + "Invalid input, please enter 'y' or 'n'.")

if __name__ == "__main__":
    main()
