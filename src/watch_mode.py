"""
Watch Mode Module
Monitors directories for new ZIP/RVZ files and automatically processes them.
"""

import time
import threading
from pathlib import Path
from typing import Callable, Optional
from datetime import datetime


class WatchMode:
    """
    Monitors a directory for new ZIP/RVZ files and triggers conversion.
    Uses polling to detect new files (cross-platform, no external dependencies).
    """

    def __init__(
        self,
        watch_dir: Path,
        output_dir: Path,
        conversion_callback: Callable[[Path, Path], None],
        check_interval: float = 5.0,
        file_stable_time: float = 10.0,
        process_existing: bool = False,
    ):
        """
        Initialize watch mode.

        Args:
            watch_dir: Directory to watch for new files
            output_dir: Output directory for conversions
            conversion_callback: Function to call when new file is detected
                                Signature: (input_file: Path, output_dir: Path) -> None
            check_interval: How often to check for new files (seconds)
            file_stable_time: How long a file must be stable before processing (seconds)
            process_existing: If True, also process files that already exist when watch mode starts
        """
        self.watch_dir = Path(watch_dir).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.conversion_callback = conversion_callback
        self.check_interval = check_interval
        self.file_stable_time = file_stable_time
        self.process_existing = process_existing

        # Track known files and their states
        self.known_files: set[Path] = set()
        self.file_sizes: dict[Path, int] = {}
        self.file_times: dict[Path, datetime] = {}

        # Control
        self.is_watching = False
        self.watch_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()

        # Status callback
        self.status_callback: Optional[Callable[[str], None]] = None

    def set_status_callback(self, callback: Callable[[str], None]):
        """Set callback for status updates."""
        self.status_callback = callback

    def _log_status(self, message: str):
        """Log status message."""
        if self.status_callback:
            self.status_callback(message)
        else:
            print(f"[Watch Mode] {message}")

    def _scan_supported_files(self) -> list[Path]:
        """Return all ZIP/RVZ files in the watch directory, deduplicated."""
        if not self.watch_dir.exists():
            return []

        seen: set[str] = set()
        found: list[Path] = []

        for pattern in ("*.zip", "*.ZIP", "*.rvz", "*.RVZ"):
            for file_path in self.watch_dir.rglob(pattern):
                try:
                    key = str(file_path.resolve()).lower()
                except OSError:
                    key = str(file_path).lower()

                if key not in seen:
                    seen.add(key)
                    found.append(file_path)

        found.sort(key=lambda p: str(p).lower())
        return found

    def _find_new_files(self) -> list[Path]:
        """Find new ZIP and RVZ files in the watch directory."""
        new_files: list[Path] = []
        for file_path in self._scan_supported_files():
            if file_path not in self.known_files:
                new_files.append(file_path)
        return new_files

    def _is_file_stable(self, file_path: Path) -> bool:
        """Check if a file is stable (not currently being written)."""
        if not file_path.exists():
            return False

        try:
            current_size = file_path.stat().st_size

            if file_path in self.file_sizes:
                if self.file_sizes[file_path] == current_size:
                    if file_path in self.file_times:
                        time_since_seen_same_size = datetime.now() - self.file_times[file_path]
                        if time_since_seen_same_size.total_seconds() >= self.file_stable_time:
                            return True
                    else:
                        self.file_times[file_path] = datetime.now()
                        return False
                else:
                    self.file_sizes[file_path] = current_size
                    self.file_times[file_path] = datetime.now()
                    return False
            else:
                self.file_sizes[file_path] = current_size
                self.file_times[file_path] = datetime.now()
                return False

        except (OSError, PermissionError):
            return False

        return False

    def _process_new_file(self, file_path: Path):
        """Process a newly detected file."""
        self._log_status(f"Detected new file: {file_path.name}")
        self._log_status(f"Waiting for {file_path.name} to be stable...")

        stable_checks = 0
        required_stable_checks = int(self.file_stable_time / self.check_interval) + 1

        while stable_checks < required_stable_checks:
            if self.stop_event.is_set():
                return

            if self._is_file_stable(file_path):
                stable_checks += 1
            else:
                stable_checks = 0

            if stable_checks < required_stable_checks:
                time.sleep(self.check_interval)

        self._log_status(f"File {file_path.name} is stable, starting conversion...")

        try:
            self.conversion_callback(file_path, self.output_dir)
            self._log_status(f"Completed processing: {file_path.name}")
        except Exception as e:
            self._log_status(f"Error processing {file_path.name}: {e}")

    def _watch_loop(self):
        """Main watch loop (runs in separate thread)."""
        self._log_status(f"Watch mode started. Monitoring: {self.watch_dir}")
        self._log_status(f"Checking for new files every {self.check_interval} seconds")
        self._log_status(f"Files must be stable for {self.file_stable_time} seconds before processing")

        initial_files = self._find_new_files()
        if initial_files:
            if self.process_existing:
                self._log_status(f"Found {len(initial_files)} existing file(s), will process them")
            else:
                self.known_files.update(initial_files)
                self._log_status(f"Found {len(initial_files)} existing file(s), will not process them")

        while not self.stop_event.is_set():
            try:
                new_files = self._find_new_files()

                for file_path in new_files:
                    if self.stop_event.is_set():
                        break

                    self.known_files.add(file_path)

                    process_thread = threading.Thread(
                        target=self._process_new_file,
                        args=(file_path,),
                        daemon=True,
                    )
                    process_thread.start()

                self.stop_event.wait(self.check_interval)

            except Exception as e:
                self._log_status(f"Error in watch loop: {e}")
                time.sleep(self.check_interval)

        self._log_status("Watch mode stopped")

    def start(self):
        """Start watching for new files."""
        if self.is_watching:
            self._log_status("Watch mode is already running")
            return

        if not self.watch_dir.exists():
            raise ValueError(f"Watch directory does not exist: {self.watch_dir}")

        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.is_watching = True
        self.stop_event.clear()

        self.watch_thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.watch_thread.start()

        self._log_status("Watch mode started")

    def stop(self):
        """Stop watching for new files."""
        if not self.is_watching:
            return

        self._log_status("Stopping watch mode...")
        self.is_watching = False
        self.stop_event.set()

        if self.watch_thread and self.watch_thread.is_alive():
            self.watch_thread.join(timeout=5.0)

        self._log_status("Watch mode stopped")

    def is_running(self) -> bool:
        """Check if watch mode is currently running."""
        return self.is_watching and not self.stop_event.is_set()
