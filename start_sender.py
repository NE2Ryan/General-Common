import os
import sys
import subprocess

PID_FILE = "sender.pid"
SCRIPT_TO_RUN = "sender.py"

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
        # This is a simplified daemonization. The child process will be orphaned 
        # and adopted by init/launchd when this script exits.
        proc = subprocess.Popen([sys.executable, SCRIPT_TO_RUN])

    print(f"'{SCRIPT_TO_RUN}' started in the background with PID: {proc.pid}")
    # The PID is now written by the script itself, so no need to write it here.

if __name__ == "__main__":
    main()
