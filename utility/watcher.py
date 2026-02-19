import subprocess
import time
import sys
import os
import signal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


COMMAND = ["python", "main.py"]   # The application to run
WATCH_EXT = ".py"

running_process = None
DEBOUNCE_DELAY = 0.5
last_trigger = 0


def start_app():
    global running_process
    running_process = subprocess.Popen(COMMAND)
    print(f"Started application (PID {running_process.pid})")


def stop_app():
    global running_process
    if running_process and running_process.poll() is None:
        print(f"Stopping application (PID {running_process.pid})...")
        try:
            if os.name == "nt":
                running_process.terminate()
            else:
                os.kill(running_process.pid, signal.SIGTERM)
        except Exception:
            pass

        try:
            running_process.wait(timeout=2)
        except Exception:
            pass

    running_process = None


class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global last_trigger

        # Ignore folders
        if event.is_directory:
            return

        # Only watch .py files
        if not event.src_path.endswith(WATCH_EXT):
            return

        now = time.time()
        if now - last_trigger < DEBOUNCE_DELAY:
            return  # Ignore duplicate save events
        last_trigger = now

        print(f"Change detected in: {event.src_path}")

        stop_app()
        start_app()


def main():
    if len(sys.argv) < 2:
        print("Usage: python watch.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]

    if not os.path.isdir(directory):
        print("Invalid directory")
        sys.exit(1)

    print(f"Watching directory recursively: {directory}")

    # Start the application initially
    start_app()

    observer = Observer()
    observer.schedule(ChangeHandler(), directory, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping watcher...")
        observer.stop()
        stop_app()

    observer.join()
    print("Watcher stopped.")


if __name__ == "__main__":
    main()
