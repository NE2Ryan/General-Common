import os
import sys
import signal

PID_FILE = "receiver.pid"

def main():
    # Check if the PID file exists
    if not os.path.exists(PID_FILE):
        print(f"Error: Process is not running or PID file '{PID_FILE}' not found.")
        sys.exit(1)

    # Read the PID
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
    except (IOError, ValueError) as e:
        print(f"Error reading PID file: {e}")
        sys.exit(1)

    print(f"Stopping process with PID: {pid}")

    # Send termination signal
    try:
        os.kill(pid, signal.SIGTERM)
        print("Termination signal sent.")
    except ProcessLookupError:
        print(f"Warning: Process with PID {pid} not found. It may have already stopped.")
        os.remove(PID_FILE)
    except Exception as e:
        print(f"Error stopping process: {e}")
        if sys.platform == "win32":
            import subprocess
            subprocess.run(f"taskkill /F /PID {pid}", shell=True)


if __name__ == "__main__":
    main()
