import socket
import time
import requests

SERVER_HOST = 'builder.reonic.dev'
SERVER_PORT = 65432
METER_SERVER_URL = 'http://localhost:5340/api/v0/dial/{dial_id}/set?key={key}&value={value}'
BACKLIGHT_URL = 'http://localhost:5340/api/v0/dial/{dial_id}/backlight?key={key}&red={red}&green={green}&blue={blue}'
KEY = 'cTpAWYuRpA2zx75Yh961Cg'

# Dial IDs
DIAL_1_MIN = '35002A000650564139323920'
DIAL_5_MIN = '1F003C000650564139323920'
DIAL_15_MIN = '800031000650564139323920'

def send_dial_request(dial_id, value):
    """Send an HTTP GET request to set the dial value."""
    value = min(100, max(0, value))  # Ensure value is between 0 and 100
    url = METER_SERVER_URL.format(dial_id=dial_id, key=KEY, value=value)
    try:
        response = requests.get(url)
        if response.status_code < 200 or response.status_code >= 300:
            print(f"Error setting dial {dial_id}: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error connecting to meter server: {e}")

def send_backlight_request(dial_id, load_value):
    """Send an HTTP GET request to set the dial backlight color."""
    # Calculate the color based on load_value (0-100)
    if load_value <= 30:
        # Set to white when load is between 0% and 30%
        red, green, blue = 100, 100, 100
    else:
        # Transition from yellow (30%) to red (100%) as load increases
        red = min(100, int((load_value - 30) * 2.5))  # Increase red as load increases
        green = max(0, 100 - red)  # Decrease green as red increases
        blue = 0  # No blue component

    # Print debugging info for color components
    print(f"Setting backlight for dial {dial_id} to RGB({red}, {green}, {blue})")

    # Send backlight request
    url = BACKLIGHT_URL.format(dial_id=dial_id, key=KEY, red=red, green=green, blue=blue)
    try:
        response = requests.get(url)
        if response.status_code < 200 or response.status_code >= 300:
            print(f"Error setting backlight for dial {dial_id}: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error connecting to meter server: {e}")

def process_load_avg(load_avg):
    """Process the load averages and send requests to the meter server."""
    load_avg = load_avg.strip().split()
    if len(load_avg) >= 3:
        try:
            # Convert the load averages to percentages (multiply by 10)
            load_1m = float(load_avg[0]) * 10
            load_5m = float(load_avg[1]) * 10
            load_15m = float(load_avg[2]) * 10

            # Send requests to set the dials
            send_dial_request(DIAL_1_MIN, load_1m)
            send_dial_request(DIAL_5_MIN, load_5m)
            send_dial_request(DIAL_15_MIN, load_15m)

            # Send requests to set the backlights based on load values
            send_backlight_request(DIAL_1_MIN, load_1m)
            send_backlight_request(DIAL_5_MIN, load_5m)
            send_backlight_request(DIAL_15_MIN, load_15m)

        except ValueError:
            print("Error: Invalid load average values received.")

def client():
    """Connect to the loadavg server and process the load averages."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_HOST, SERVER_PORT))
        print(f"Connected to {SERVER_HOST}:{SERVER_PORT}")

        while True:
            try:
                # Receive load average from the server
                load_avg = s.recv(1024).decode('utf-8').strip()
                if load_avg:
                    print(f"Received load average: {load_avg}")
                    process_load_avg(load_avg)
                else:
                    print("Error: Empty load average received.")
            except socket.error as e:
                print(f"Error receiving data: {e}")
            time.sleep(1)  # Small delay before checking again

if __name__ == "__main__":
    client()
