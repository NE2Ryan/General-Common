import socket
import csv
import os
import sys
import signal
import logging

# --- Configuration ---
RECEIVER_IP = "192.168.12.40"
RECEIVER_PORT = 5005
PACKET_SIZE = 1024
CSV_FILENAME = "received_packets.csv"
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

    # Store PID
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver_socket.bind((RECEIVER_IP, RECEIVER_PORT))
    
    logging.info(f"Receiver listening on {RECEIVER_IP}:{RECEIVER_PORT}")

    file_exists = os.path.isfile(CSV_FILENAME)
    
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
        with open(CSV_FILENAME, 'a', newline='') as csvfile:
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
