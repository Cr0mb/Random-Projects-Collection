# Real-time TCP traffic monitor using Scapy that logs connection stats, detects high packet rates, and flags suspicious hosts.

from scapy.all import sniff, IP, TCP
import os
import socket
import time
from collections import defaultdict

LOG_FILE = "all_traffic_with_stats.txt"
MY_IPS = {""}  # Your own IPs to ignore

seen_connections = {}  # conn string -> {packets, bytes, min_hops, total_hops, first_seen}
connection_rates = defaultdict(list)  # src_ip -> list of timestamps

SUSPECT_THRESHOLD_PPS = 100  # Packets per second threshold
script_start_time = time.time()

def resolve_ip(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return "NXDOMAIN"

def estimate_hops(ttl):
    for init_ttl in [64, 128, 255]:
        if ttl <= init_ttl:
            return init_ttl - ttl
    return -1

def format_time(seconds):
    mins, secs = divmod(int(seconds), 60)
    hrs, mins = divmod(mins, 60)
    return f"{hrs}h {mins}m {secs}s"

def log_packet(pkt):
    if IP in pkt and TCP in pkt:
        ip_layer = pkt[IP]
        tcp_layer = pkt[TCP]

        if ip_layer.src in MY_IPS or ip_layer.dst in MY_IPS:
            return

        src = ip_layer.src
        dst = ip_layer.dst
        src_host = resolve_ip(src)
        dst_host = resolve_ip(dst)

        conn = f"{src_host}:{tcp_layer.sport} -> {dst_host}:{tcp_layer.dport}"
        hop_count = estimate_hops(ip_layer.ttl)
        pkt_len = len(pkt)
        now = time.time()

        # Track rate
        connection_rates[src].append(now)
        connection_rates[src] = [t for t in connection_rates[src] if now - t < 1]
        pps = len(connection_rates[src])

        suspect = ""
        if pps >= SUSPECT_THRESHOLD_PPS:
            suspect += " 🚨 HIGH PPS"
        if src_host == "NXDOMAIN":
            suspect += " ❓ UNKNOWN HOST"

        if conn in seen_connections:
            stats = seen_connections[conn]
            stats["packets"] += 1
            stats["bytes"] += pkt_len
            stats["total_hops"] += max(0, hop_count)
            stats["min_hops"] = min(stats["min_hops"], hop_count) if hop_count >= 0 else stats["min_hops"]
        else:
            seen_connections[conn] = {
                "packets": 1,
                "bytes": pkt_len,
                "min_hops": hop_count if hop_count >= 0 else 0,
                "total_hops": hop_count if hop_count >= 0 else 0,
                "first_seen": now,
            }

        elapsed = time.time() - script_start_time
        elapsed_str = format_time(elapsed)

        # Write full log with elapsed time at top
        with open(LOG_FILE, "w") as f:
            f.write(f"Uptime: {elapsed_str}\n")
            for c, stats in seen_connections.items():
                f.write(f"{c} | packets: {stats['packets']} | bytes: {stats['bytes']} | min_hops: {stats['min_hops']} | total_hops: {stats['total_hops']}\n")

        # Print live update
        print(f"{conn} | packets: {seen_connections[conn]['packets']} | bytes: {seen_connections[conn]['bytes']} | min_hops: {seen_connections[conn]['min_hops']} | total_hops: {seen_connections[conn]['total_hops']} | PPS: {pps} | Uptime: {elapsed_str}{suspect}")

print(f"[*] Monitoring all TCP traffic. Logging to {LOG_FILE}")
sniff(filter="tcp", prn=log_packet, store=0)
