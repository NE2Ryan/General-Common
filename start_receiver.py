import os
import sys
import subprocess

PID_FILE = "receiver.pid"
SCRIPT_TO_RUN = "receiver.py"

def main():
    # Check if the process is already running
    if os.path.exists(PID_FILE):
        print(f"Error: Process is already running. PID file '{PID_FILE}' exists.")
        sys.exit(1)

    # For Windows: Use DETACHED_PROCESS to run the script in a new console
    if sys.platform == "win32":
        creationflags = subprocess.DETACHED_PROCESS
        proc = subprocess.Popen([sys.executable, SCRIPT_TO_RUN], creationflags=creationflags)
    # For Unix-like systems (macOS, Linux)
    else:
        proc = subprocess.Popen([sys.executable, SCRIPT_TO_RUN])

    print(f"'{SCRIPT_TO_RUN}' started in the background with PID: {proc.pid}")

if __name__ == "__main__":
    main()
