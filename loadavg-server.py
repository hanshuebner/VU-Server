import socket
import time
import threading
import shutil  # To get disk usage

HOST = '0.0.0.0'  # Bind to all interfaces
PORT = 65432      # Port to listen on (non-privileged ports are > 1023)

def get_load_average():
    """Reads and returns the raw load average from /proc/loadavg."""
    with open("/proc/loadavg", "r") as f:
        load_avg = f.readline().strip().split()[:3]  # Get the 1, 5, and 15 minute load averages

    # Get disk usage of the root filesystem
    total, used, free = shutil.disk_usage("/")
    disk_usage_percentage = (used / total) * 100

    # Return load averages and disk usage percentage
    return ' '.join(load_avg) + f' {disk_usage_percentage:.2f}'

def handle_client(conn, addr):
    """Handles a single client connection, sending load average and disk usage every 15 seconds."""
    print(f"Connected by {addr}")
    try:
        while True:
            # Get load average and disk usage percentage
            load_avg = get_load_average()
            # Send data to client
            conn.sendall(load_avg.encode('utf-8') + b'\n')
            # Wait for 15 seconds
            time.sleep(15)
    except (BrokenPipeError, ConnectionResetError):
        print(f"Connection closed by {addr}")
    finally:
        conn.close()

def start_server():
    """Starts the TCP server to accept multiple clients and handle them concurrently."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Set the SO_REUSEADDR option
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")

        while True:
            # Accept new connections
            conn, addr = s.accept()
            # Handle each client in a new thread
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.daemon = True  # Set thread as daemon so it exits when main thread exits
            client_thread.start()

if __name__ == "__main__":
    start_server()

