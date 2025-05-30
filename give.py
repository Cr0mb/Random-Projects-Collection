# Scans GiveawayBase.com for active giveaways with keyword filtering, pagination, and interactive CLI interface with colorful output.

import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pyfiglet
from colorama import Fore, Style, init
import time

init(autoreset=True)

POPULAR_KEYWORDS = [
    "Gaming PC", "Steam Deck", "RTX", "Razer", "Logitech", "Headset", "Keyboard", "Mouse",
    "Monitor", "GPU", "PS5", "Xbox", "Gift Card", "Amazon", "Meta Quest",
    "Laptop", "Smartphone", "Microphone", "Electric Scooter", "Eyewear"
]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def fetch_all_active_giveaways(keyword_filters=None, min_results=1):
    base_url = 'https://giveawaybase.com/category/active-giveaways/page/{}/'
    headers = {'User-Agent': 'Mozilla/5.0'}

    giveaways = []
    page = 1

    print(Fore.YELLOW + "\n🔍 Scanning pages and loading giveaways...\n")

    pbar = tqdm(desc="Loading pages", unit=" ", dynamic_ncols=True, leave=True)
    
    while True:
        url = base_url.format(page)
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            pbar.close()
            print(Fore.GREEN + "Done Searching.")
            time.sleep(2)
            break

        soup = BeautifulSoup(response.text, 'html.parser')

        if soup.find('h1', class_='entry-title', string="Oops! That page can’t be found."):
            break

        articles = soup.find_all('article')
        if not articles:
            break

        page_results = []
        for article in articles:
            title_tag = article.find('h2')
            link_tag = article.find('a', href=True)
            time_tag = article.find('time', class_='entry-date published')

            if title_tag and link_tag:
                title = title_tag.get_text(strip=True)
                link = link_tag['href']
                date = time_tag.get_text(strip=True) if time_tag else "Unknown Date"

                if not keyword_filters or any(kw.lower() in title.lower() for kw in keyword_filters):
                    page_results.append({'title': title, 'link': link, 'date': date})

        if len(page_results) >= min_results:
            giveaways.extend(page_results)

        pbar.update(1)
        page += 1

        time.sleep(0.3)

    pbar.close()
    print(Fore.GREEN + f"\n✅ Total pages scanned: {page - 1}\n")
    return giveaways

def choose_keyword_mode():
    print(Fore.YELLOW + "\n🎯 Choose input mode for giveaway keyword filtering:")
    print(Fore.CYAN + "1. Enter your own keyword(s) (comma-separated)")
    print(Fore.CYAN + "2. Select from the 20 most common keywords")
    print(Fore.CYAN + "3. Show all giveaways (no filtering)")

    try:
        choice = int(input(Fore.GREEN + "\nEnter your choice (1-3): ").strip())
        if choice == 1:
            keywords = input("Enter your own keyword(s), separated by commas: ").strip()
            return [k.strip() for k in keywords.split(',') if k.strip()]
        elif choice == 2:
            return choose_from_popular_keywords()
        elif choice == 3:
            return None
        else:
            print(Fore.YELLOW + "No keyword filtering will be used.")
            return None
    except ValueError:
        print(Fore.YELLOW + "Invalid input. No keyword filtering will be used.")
        return None

def choose_from_popular_keywords():
    print(Fore.YELLOW + "\nSelect one of the 20 most common keywords:")
    for i, kw in enumerate(POPULAR_KEYWORDS, start=1):
        print(Fore.CYAN + f"{i}. {kw}")
    try:
        choice = int(input(Fore.GREEN + f"\nEnter your choice (1-{len(POPULAR_KEYWORDS)}): ").strip())
        if 1 <= choice <= len(POPULAR_KEYWORDS):
            return [POPULAR_KEYWORDS[choice - 1]]
        else:
            print(Fore.YELLOW + "Invalid choice. No keyword filtering will be used.")
            return None
    except ValueError:
        print(Fore.YELLOW + "Invalid input. No keyword filtering will be used.")
        return None

def print_title():
    ascii_title = pyfiglet.figlet_format("Giveaway Scanner", font="slant")
    print(Fore.MAGENTA + ascii_title)
    print(Fore.YELLOW + Style.BRIGHT + "Made by github.com/Cr0mb/\n")

def display_page(giveaways, page_num, total_pages, page_size=10):
    clear_screen()
    print_title()
    print(Fore.YELLOW + Style.BRIGHT + f"--- Page {page_num} of {total_pages} ---\n")

    start_index = (page_num - 1) * page_size
    end_index = start_index + page_size
    page = giveaways[start_index:end_index]

    for idx, giveaway in enumerate(page, start=start_index + 1):
        print(Fore.GREEN + Style.BRIGHT + f"{idx}. " + Fore.CYAN + Style.BRIGHT + giveaway['title'])
        print(Fore.YELLOW + Style.BRIGHT + f"   Date: " + Fore.YELLOW + giveaway['date'])
        print(Fore.MAGENTA + Style.BRIGHT + f"   Link: " + Fore.BLUE + giveaway['link'] + "\n")

    print(Fore.GREEN + Style.BRIGHT + "Controls: [Enter] Next Page | [b] Back Page | [q] Quit\n")


def main():
    clear_screen()
    print_title()
    keyword_filters = choose_keyword_mode()

    try:
        min_results = int(input(Fore.YELLOW + "🔢 Minimum results per page to include (default 1): ").strip() or 1)
        if min_results < 1:
            raise ValueError()
    except ValueError:
        min_results = 1
        print(Fore.RED + "Invalid input. Using minimum results = 1")
        time.sleep(1)

    if keyword_filters:
        print(Fore.MAGENTA + f"\n⏳ Fetching giveaways filtered by: {', '.join(keyword_filters)}...\n")
    else:
        print(Fore.MAGENTA + "\n⏳ Fetching all giveaways...\n")

    giveaways = fetch_all_active_giveaways(keyword_filters=keyword_filters, min_results=min_results)

    if giveaways:
        total_pages = (len(giveaways) + 9) // 10
        current_page = 1

        while True:
            display_page(giveaways, current_page, total_pages, page_size=10)
            user_input = input(Fore.GREEN + "Your choice: ").strip().lower()

            if user_input == 'q':
                print(Fore.RED + "Exiting. Goodbye!")
                clear_screen()
                break
            elif user_input == 'b':
                if current_page > 1:
                    current_page -= 1
                else:
                    print(Fore.RED + "You are already on the first page.")
                    time.sleep(1.5)
            else:
                if current_page < total_pages:
                    current_page += 1
                else:
                    print(Fore.RED + "You are already on the last page.")
                    cont = input(Fore.GREEN + "Press 'b' to go back or 'q' to quit: ").strip().lower()
                    if cont == 'q':
                        print(Fore.RED + "Exiting. Goodbye!")
                        break
                    elif cont == 'b' and current_page > 1:
                        current_page -= 1
    else:
        print(Fore.RED + "No matching giveaways found.")

if __name__ == "__main__":
    main()
