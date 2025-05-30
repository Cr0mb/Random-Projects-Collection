# continuously monitors the Steam store for games with discounts of 80% or more or 100% (free), emails new promotions to the user, and logs them to avoid duplicates, with colorful terminal output and a 24-hour check interval.

import requests
import time
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pyfiglet
from colorama import init, Fore, Style

init(autoreset=True)

SENDER_EMAIL = ""
SENDER_PASSWORD = ""
RECEIVER_EMAIL = ""

SEEN_PROMOS_FILE = "seen_promotions.txt"
CHECK_INTERVAL = 24 * 60 * 60

def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(Fore.GREEN + "✅ Email sent successfully.\n")
    except Exception as e:
        print(Fore.RED + f"❌ Error sending email: {e}\n")

def load_seen_promotions():
    if not os.path.exists(SEEN_PROMOS_FILE):
        return set()
    with open(SEEN_PROMOS_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)

def save_seen_promotions(promotions):
    with open(SEEN_PROMOS_FILE, "a", encoding="utf-8") as f:
        for promo in promotions:
            f.write(promo + "\n")

def get_app_id_from_logo_url(logo_url):
    try:
        parts = logo_url.split("/apps/")
        if len(parts) > 1:
            app_part = parts[1]
            app_id = app_part.split("/")[0]
            return app_id
    except Exception:
        return None
    return None

def fetch_app_details(app_id):
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
    try:
        response = requests.get(url)
        data = response.json()
        app_data = data.get(str(app_id), {})
        if not app_data.get("success", False):
            return None
        return app_data.get("data", None)
    except Exception as e:
        print(Fore.RED + f"❌ Error fetching app details for {app_id}: {e}")
        return None

def fetch_promotions(maxprice=None):
    url = "https://store.steampowered.com/search/results/"
    params = {
        "specials": "1",
        "ndl": "1",
        "json": "1"
    }
    if maxprice:
        params["maxprice"] = maxprice

    try:
        response = requests.get(url, params=params)
        data = response.json()
        items = data.get("items", [])
        promotions = []

        for item in items:
            title = item.get("name", "Unknown")
            logo_url = item.get("logo", "")
            app_id = get_app_id_from_logo_url(logo_url)
            if not app_id:
                continue

            details = fetch_app_details(app_id)
            if not details:
                continue

            price_overview = details.get("price_overview")
            if price_overview:
                discount = price_overview.get("discount_percent", 0)
                original_price_cents = price_overview.get("initial", 0)
                discounted_price_cents = int(original_price_cents * (100 - discount) / 100)
                discounted_price = discounted_price_cents / 100.0
            else:
                discount = 0
                discounted_price = 0.0

            if discount >= 80 or discounted_price == 0.0:
                promotions.append({
                    "title": title,
                    "discount": discount,
                    "price": discounted_price,
                    "app_id": app_id
                })

        return promotions
    except Exception as e:
        print(Fore.RED + f"❌ Error fetching promotions list: {e}")
        return []

def print_promo(game):
    print(Fore.CYAN + "=" * 60)
    print(Fore.YELLOW + "Title: " + Fore.WHITE + f"{game['title']}")
    print(Fore.YELLOW + "Discount: " + Fore.GREEN + f"{game['discount']}%")
    price_color = Fore.GREEN if game['price'] == 0.0 else Fore.WHITE
    print(Fore.YELLOW + "Price: " + price_color + f"${game['price']:.2f}")
    print(Fore.YELLOW + "Steam Link: " + Fore.BLUE + f"https://store.steampowered.com/app/{game['app_id']}")
    print(Fore.CYAN + "=" * 60 + "\n")

def main_loop():
    ascii_title = pyfiglet.figlet_format("Slice Strip")
    print(Fore.MAGENTA + ascii_title)
    print(Style.BRIGHT + Fore.GREEN + "Made by GitHub.com/Cr0mb\n")

    print(Style.BRIGHT + Fore.WHITE + "Steam Promotion Checker is now running 24/7.\n")
    seen_promotions = load_seen_promotions()

    while True:
        print(Style.BRIGHT + Fore.YELLOW + "Checking for new promotions (discounts >= 80%)...")
        discounted_promos = fetch_promotions()

        print(Style.BRIGHT + Fore.YELLOW + "Checking for new 100% free promotions...")
        free_promos = fetch_promotions(maxprice="free")

        combined_promos_dict = {}
        for promo in discounted_promos + free_promos:
            combined_promos_dict[promo["title"]] = promo

        combined_promos = list(combined_promos_dict.values())

        new_promos = [p for p in combined_promos if p["title"] not in seen_promotions]

        filtered_new_promos = [p for p in new_promos if not (p["discount"] == 0 and p["price"] == 0.0)]

        if filtered_new_promos:
            print(Style.BRIGHT + Fore.GREEN + f"\nFound {len(filtered_new_promos)} new promotion(s). Sending email and printing to terminal...\n")
            message_lines = []
            for game in filtered_new_promos:
                print_promo(game)
                message_lines.append(
                    f"Title: {game['title']}\n"
                    f"Discount: {game['discount']}%\n"
                    f"Price: ${game['price']:.2f}\n"
                    f"Steam Link: https://store.steampowered.com/app/{game['app_id']}\n"
                    + ("-"*40)
                )

            message = "\n".join(message_lines)
            send_email("New High-Discount Steam Promotions!", message)

            seen_promotions.update(p["title"] for p in filtered_new_promos)
            save_seen_promotions([p["title"] for p in filtered_new_promos])
        else:
            print(Style.BRIGHT + Fore.RED + "No new promotions found.\n")

        print(Style.BRIGHT + Fore.WHITE + "Sleeping for 24 hours...\n")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main_loop()
