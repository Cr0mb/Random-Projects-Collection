# This script scans a local IP range for active Minecraft servers on port 25565 using multithreading and socket connections.

import socket
import threading
from queue import Queue

# List of IPs or a range to scan
ip_range = ["192.168.1.{}".format(i) for i in range(1, 255)]

# Minecraft server port
minecraft_port = 25565

# Queue for threading
queue = Queue()

# Function to check if a Minecraft server is available
def check_minecraft_server(ip):
    try:
        # Create a socket and try to connect to the Minecraft server port
        with socket.create_connection((ip, minecraft_port), timeout=2) as s:
            s.send(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")  # Handshake packet
            s.settimeout(2)
            data = s.recv(1024)
            if data:
                print(f"[+] Found Minecraft server at {ip}:{minecraft_port}")
                # Optionally, parse the response data for MOTD, version, etc.
    except socket.timeout:
        pass
    except Exception as e:
        pass

# Worker function to process the queue
def worker():
    while not queue.empty():
        ip = queue.get()
        check_minecraft_server(ip)
        queue.task_done()

# Fill the queue with IPs to scan
for ip in ip_range:
    queue.put(ip)

# Start a few worker threads to scan IPs concurrently
threads = []
for _ in range(10):  # Number of threads
    t = threading.Thread(target=worker)
    threads.append(t)
    t.start()

# Wait for all threads to finish
queue.join()

# Wait for all threads to finish
for t in threads:
    t.join()

print("Scanning complete.")
