"""
Network Mover Module
Handles moving WBFS files to network shares with folder structure preservation.
"""

import time
import shutil
from pathlib import Path
from typing import Optional, Tuple
from enum import Enum


class OverwriteBehavior(Enum):
    """Behavior when target file already exists."""
    SKIP = "skip"
    APPEND_TIMESTAMP = "append_timestamp"
    APPEND_VERSION = "append_version"
    OVERWRITE = "overwrite"


class NetworkMoveResult:
    """Result of a network move operation."""
    
    def __init__(
        self,
        source_file: Path,
        target_file: Path,
        success: bool,
        error_message: Optional[str] = None,
        skipped: bool = False
    ):
        self.source_file = source_file
        self.target_file = target_file
        self.success = success
        self.error_message = error_message
        self.skipped = skipped


class NetworkMover:
    """
    Moves WBFS files to network shares, preserving folder structure.
    """
    
    def __init__(
        self,
        network_root: Path,
        keep_local: bool = False,
        overwrite_behavior: OverwriteBehavior = OverwriteBehavior.SKIP,
        max_retries: int = 3,
        retry_delay: float = 2.0
    ):
        """
        Initialize network mover.
        
        Args:
            network_root: Root path on network share (e.g., \\\\server\\share)
            keep_local: If True, copy instead of move (keep local copy)
            overwrite_behavior: What to do if target file exists
            max_retries: Maximum number of retry attempts for network failures
            retry_delay: Delay between retries in seconds
        """
        self.network_root = Path(network_root)
        self.keep_local = keep_local
        self.overwrite_behavior = overwrite_behavior
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Status callback
        self.status_callback: Optional[callable] = None
    
    def set_status_callback(self, callback: callable):
        """Set callback for status updates (message: str)."""
        self.status_callback = callback
    
    def _log_status(self, message: str):
        """Log status message."""
        if self.status_callback:
            self.status_callback(message)
    
    def _ensure_network_path(self) -> bool:
        """
        Verify network path is accessible.
        
        Returns:
            True if accessible, False otherwise
        """
        try:
            # Try to access the network path
            if not self.network_root.exists():
                # Try to create it
                try:
                    self.network_root.mkdir(parents=True, exist_ok=True)
                except (OSError, PermissionError) as e:
                    self._log_status(f"Network path not accessible: {e}")
                    return False
            
            # Try to write a test (check if writable)
            test_file = self.network_root / ".wbfs_mover_test"
            try:
                test_file.touch()
                test_file.unlink()
            except (OSError, PermissionError) as e:
                self._log_status(f"Network path not writable: {e}")
                return False
            
            return True
        
        except Exception as e:
            self._log_status(f"Error checking network path: {e}")
            return False
    
    def _compute_relative_path(self, local_file: Path, local_output_root: Path) -> Path:
        """
        Compute relative path from local output root.
        
        Args:
            local_file: Full path to local WBFS file
            local_output_root: Root of local output directory
            
        Returns:
            Relative path (e.g., "Game Title [ID]/ID.wbfs")
        """
        try:
            rel_path = local_file.relative_to(local_output_root)
            return rel_path
        except ValueError:
            # File is not under output root, use just the filename
            return Path(local_file.name)
    
    def _compute_network_path(self, local_file: Path, local_output_root: Path) -> Path:
        """
        Compute full network path for a local file.
        
        Args:
            local_file: Full path to local WBFS file
            local_output_root: Root of local output directory
            
        Returns:
            Full path on network share
        """
        rel_path = self._compute_relative_path(local_file, local_output_root)
        network_path = self.network_root / rel_path
        return network_path
    
    def _handle_existing_file(self, target_path: Path) -> Optional[Path]:
        """
        Handle case where target file already exists.
        
        Args:
            target_path: Path that already exists
            
        Returns:
            New path to use, or None if should skip
        """
        if self.overwrite_behavior == OverwriteBehavior.SKIP:
            return None
        
        elif self.overwrite_behavior == OverwriteBehavior.OVERWRITE:
            return target_path
        
        elif self.overwrite_behavior == OverwriteBehavior.APPEND_TIMESTAMP:
            # Append timestamp: file.wbfs -> file_20240101_120000.wbfs
            stem = target_path.stem
            suffix = target_path.suffix
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            new_name = f"{stem}_{timestamp}{suffix}"
            return target_path.parent / new_name
        
        elif self.overwrite_behavior == OverwriteBehavior.APPEND_VERSION:
            # Append version: file.wbfs -> file_1.wbfs, file_2.wbfs, etc.
            stem = target_path.stem
            suffix = target_path.suffix
            counter = 1
            while True:
                new_name = f"{stem}_{counter}{suffix}"
                new_path = target_path.parent / new_name
                if not new_path.exists():
                    return new_path
                counter += 1
                if counter > 1000:  # Safety limit
                    return None
        
        return None
    
    def _atomic_move(self, source: Path, target: Path) -> bool:
        """
        Perform atomic move (copy then delete) to avoid partial files.
        
        Args:
            source: Source file path
            target: Target file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure target directory exists
            target.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy to temporary name first
            temp_target = target.with_suffix(target.suffix + ".tmp")
            
            # Copy file
            shutil.copy2(source, temp_target)
            
            # Verify copy succeeded
            if not temp_target.exists() or temp_target.stat().st_size != source.stat().st_size:
                temp_target.unlink(missing_ok=True)
                return False
            
            # Rename temp to final name (atomic on most filesystems)
            temp_target.replace(target)
            
            # Delete source if not keeping local
            if not self.keep_local:
                source.unlink()
            
            return True
        
        except Exception as e:
            # Clean up temp file on error
            temp_target = target.with_suffix(target.suffix + ".tmp")
            temp_target.unlink(missing_ok=True)
            raise e
    
    def move_file(
        self,
        local_file: Path,
        local_output_root: Path
    ) -> NetworkMoveResult:
        """
        Move a WBFS file to the network share.
        
        Args:
            local_file: Full path to local WBFS file
            local_output_root: Root of local output directory
            
        Returns:
            NetworkMoveResult with operation status
        """
        if not local_file.exists():
            return NetworkMoveResult(
                source_file=local_file,
                target_file=Path(),
                success=False,
                error_message="Source file does not exist"
            )
        
        # Compute network path
        network_path = self._compute_network_path(local_file, local_output_root)
        
        # Check if target exists
        if network_path.exists():
            self._log_status(f"Target file exists: {network_path}")
            new_path = self._handle_existing_file(network_path)
            if new_path is None:
                return NetworkMoveResult(
                    source_file=local_file,
                    target_file=network_path,
                    success=True,
                    skipped=True,
                    error_message="Target file exists and overwrite behavior is SKIP"
                )
            network_path = new_path
        
        # Retry loop for network operations
        last_error = None
        for attempt in range(self.max_retries):
            try:
                # Verify network path is accessible
                if not self._ensure_network_path():
                    if attempt < self.max_retries - 1:
                        self._log_status(f"Network path not accessible, retrying in {self.retry_delay}s (attempt {attempt + 1}/{self.max_retries})")
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        return NetworkMoveResult(
                            source_file=local_file,
                            target_file=network_path,
                            success=False,
                            error_message="Network path not accessible after retries"
                        )
                
                # Perform atomic move
                self._log_status(f"Moving {local_file.name} to network: {network_path}")
                success = self._atomic_move(local_file, network_path)
                
                if success:
                    action = "Copied" if self.keep_local else "Moved"
                    self._log_status(f"{action} {local_file.name} to network successfully")
                    return NetworkMoveResult(
                        source_file=local_file,
                        target_file=network_path,
                        success=True
                    )
                else:
                    last_error = "Atomic move failed (size mismatch)"
            
            except (OSError, PermissionError, shutil.Error) as e:
                last_error = str(e)
                if attempt < self.max_retries - 1:
                    self._log_status(f"Network move failed, retrying in {self.retry_delay}s (attempt {attempt + 1}/{self.max_retries}): {e}")
                    time.sleep(self.retry_delay)
                else:
                    self._log_status(f"Network move failed after {self.max_retries} attempts: {e}")
            
            except Exception as e:
                last_error = str(e)
                self._log_status(f"Unexpected error during network move: {e}")
                break
        
        return NetworkMoveResult(
            source_file=local_file,
            target_file=network_path,
            success=False,
            error_message=last_error or "Unknown error"
        )

