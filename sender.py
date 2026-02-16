import socket
import time
import datetime
import sys
import os
import signal
import logging
import random
import csv

# --- Configuration ---
RECEIVER_IP = "192.168.12.40"
RECEIVER_PORT = 5005
SEND_INTERVAL_SECONDS = 1
LOG_FILE = "sender.log"
PID_FILE = "sender.pid"

# Burst and sleep configuration (in hours)
BURST_DURATION_HOURS_MIN = 1
BURST_DURATION_HOURS_MAX = 2
SLEEP_DURATION_HOURS_MIN = 1
SLEEP_DURATION_HOURS_MAX = 24

def setup_logging():
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def main():
    """
    Sends data packets to the receiver in bursts, with sleep intervals.
    """
    setup_logging()
    logging.info("Sender process started.")

    # Store PID
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

    sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sequence_number = 0

    # Generate a unique CSV filename for the sender
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    csv_filename = f"sent_packets_{timestamp_str}.csv"
    logging.info(f"Logging sent packets to {csv_filename}")

    def shutdown_handler(signum, frame):
        logging.info("Shutdown signal received. Stopping sender.")
        sender_socket.close()
        try:
            os.remove(PID_FILE)
        except OSError as e:
            logging.error(f"Error removing PID file: {e}")
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown_handler)

    try:
        with open(csv_filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["SequenceNumber", "Timestamp", "Data"])

            while True:
                # --- Burst Phase ---
                burst_duration_hours = random.uniform(BURST_DURATION_HOURS_MIN, BURST_DURATION_HOURS_MAX)
                burst_duration_seconds = burst_duration_hours * 3600
                logging.info(f"Starting sending burst for {burst_duration_hours:.2f} hours.")
                
                burst_start_time = time.time()
                while (time.time() - burst_start_time) < burst_duration_seconds:
                    sequence_number += 1
                    timestamp = datetime.datetime.now().isoformat()
                    message = f"{sequence_number},{timestamp},DataPacket_{sequence_number}"
                    
                    # Send the message
                    sender_socket.sendto(message.encode(), (RECEIVER_IP, RECEIVER_PORT))
                    logging.info(f"Sent: {message}")
                    
                    # Log to sender's CSV
                    csv_writer.writerow([sequence_number, timestamp, f"DataPacket_{sequence_number}"])
                    csvfile.flush()

                    time.sleep(SEND_INTERVAL_SECONDS)

                logging.info("Sending burst finished.")

                # --- Sleep Phase ---
                sleep_duration_hours = random.uniform(SLEEP_DURATION_HOURS_MIN, SLEEP_DURATION_HOURS_MAX)
                sleep_duration_seconds = sleep_duration_hours * 3600
                logging.info(f"Entering sleep mode for {sleep_duration_hours:.2f} hours.")
                time.sleep(sleep_duration_seconds)
                logging.info("Waking up from sleep.")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        logging.info("Sender process finished.")
        if sender_socket:
            sender_socket.close()
        if os.path.exists(PID_FILE):
             os.remove(PID_FILE)

if __name__ == "__main__":
    main()
