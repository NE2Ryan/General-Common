import socket
import time
import datetime
import sys
import os
import signal
import logging

# --- Configuration ---
RECEIVER_IP = "192.168.12.40"
RECEIVER_PORT = 5005
SEND_INTERVAL_SECONDS = 1
LOG_FILE = "sender.log"
PID_FILE = "sender.pid"

def setup_logging():
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def main():
    """
    Sends data packets to the receiver.
    """
    setup_logging()
    logging.info("Sender process started.")
    
    # Store PID
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

    sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    sequence_number = 0
    
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
        while True:
            sequence_number += 1
            timestamp = datetime.datetime.now().isoformat()
            message = f"{sequence_number},{timestamp},DataPacket_{sequence_number}"
            
            sender_socket.sendto(message.encode(), (RECEIVER_IP, RECEIVER_PORT))
            logging.info(f"Sent: {message}")
            
            time.sleep(SEND_INTERVAL_SECONDS)
            
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
