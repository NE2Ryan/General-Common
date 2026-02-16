import os
import sys
import signal
import time
import subprocess

PID_FILE = "sender.pid"

def is_process_running(pid):
    """Check if a process with the given PID is running."""
    if sys.platform == "win32":
        # FINDSTR returns error level 1 if the process is not found
        cmd = f'tasklist /FI "PID eq {pid}" | findstr /R "\\<{pid}\\>"'
        result = subprocess.run(cmd, shell=True, capture_output=True)
        return result.returncode == 0
    else:
        # On Unix, os.kill(pid, 0) checks if the process exists
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True

def main():
    # Check if the PID file exists
    if not os.path.exists(PID_FILE):
        print(f"Info: Process does not appear to be running (PID file '{PID_FILE}' not found).")
        sys.exit(0)

    # Read the PID
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
    except (IOError, ValueError) as e:
        print(f"Error reading PID file: {e}. If the process is stuck, please remove '{PID_FILE}' manually.")
        sys.exit(1)

    print(f"Stopping process with PID: {pid}")

    # Send termination signal
    try:
        if sys.platform == "win32":
            # Attempt to gracefully terminate on Windows. This sends a WM_CLOSE message.
            # The python script is unlikely to catch it, but it's the "polite" way.
            # We suppress the output and ignore errors, as it will likely tell us to use /F.
            subprocess.run(f"taskkill /PID {pid}", shell=True, capture_output=True)
        else:
            # Gracefully terminate on Unix-like systems
            os.kill(pid, signal.SIGTERM)
        print("Termination signal sent. Waiting for process to exit...")
    except ProcessLookupError:
        print(f"Warning: Process with PID {pid} not found. It may have already stopped.")
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        print(f"Cleaned up stale PID file '{PID_FILE}'.")
        sys.exit(0)
    except OSError as e:
        # Catch other OS-level errors, e.g., if the process is already gone on Unix
        print(f"Warning: OS error during termination signal (process may be gone): {e}")
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        print(f"Cleaned up stale PID file '{PID_FILE}'.")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred while sending termination signal: {e}")
        sys.exit(1)

    # Wait for the process to terminate
    timeout = 10  # seconds
    start_time = time.time()
    while time.time() - start_time < timeout:
        if not is_process_running(pid):
            print("Process terminated successfully.")
            break
        time.sleep(0.5)
    else:
        print(f"Warning: Process {pid} did not terminate within {timeout} seconds. Forcing termination.")
        try:
            if sys.platform == "win32":
                subprocess.run(f"taskkill /F /PID {pid}", shell=True, check=True)
            else:
                os.kill(pid, signal.SIGKILL)
            print("Process forcefully terminated.")
        except Exception as e:
            print(f"Error during forceful termination: {e}. The process may be orphaned.")

    # Final cleanup of the PID file
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)
        print(f"PID file '{PID_FILE}' removed.")

if __name__ == "__main__":
    main()
