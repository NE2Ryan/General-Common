import socket
import csv
import os
import sys
import signal
import logging
import datetime

# --- Configuration ---
RECEIVER_IP = "192.168.1.2"
RECEIVER_PORT = 5005
PACKET_SIZE = 1024
LOG_FILE = "receiver.log"
PID_FILE = "receiver.pid"

def setup_logging():
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def main():
    """
    Receives data packets and logs them to a CSV file.
    """
    setup_logging()
    logging.info("Receiver process started.")

    # Generate a unique CSV filename with a timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    csv_filename = f"received_packets_{timestamp}.csv"
    logging.info(f"Logging received packets to {csv_filename}")

    # Store PID
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver_socket.bind((RECEIVER_IP, RECEIVER_PORT))
    
    logging.info(f"Receiver listening on {RECEIVER_IP}:{RECEIVER_PORT}")

    file_exists = os.path.isfile(csv_filename)
    
    def shutdown_handler(signum, frame):
        logging.info("Shutdown signal received. Stopping receiver.")
        receiver_socket.close()
        try:
            os.remove(PID_FILE)
        except OSError as e:
            logging.error(f"Error removing PID file: {e}")
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown_handler)

    try:
        with open(csv_filename, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            
            if not file_exists:
                csv_writer.writerow(["SequenceNumber", "Timestamp", "Data"])
            
            while True:
                data, addr = receiver_socket.recvfrom(PACKET_SIZE)
                message = data.decode()
                logging.info(f"Received: {message}")
                
                try:
                    parts = message.split(',', 2)
                    csv_writer.writerow(parts)
                    csvfile.flush()
                except IndexError:
                    logging.warning(f"Received malformed packet: {message}")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        logging.info("Receiver process finished.")
        if receiver_socket:
            receiver_socket.close()
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)

if __name__ == "__main__":
    main()
