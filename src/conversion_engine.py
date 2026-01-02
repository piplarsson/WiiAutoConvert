"""
Conversion Engine Module
Core conversion logic for RVZ → ISO → WBFS pipeline.
"""

import os
import tempfile
import threading
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum

from .tool_runner import ToolRunner
from .metadata_lookup import MetadataLookup

# Global semaphore shared across all ConversionEngine instances
# This ensures concurrency limits are enforced globally, not per-instance
_global_conversion_semaphore: Optional[threading.Semaphore] = None
_semaphore_lock = threading.Lock()


class ConversionStatus(Enum):
    """Status of a conversion operation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ConversionResult:
    """Result of a single file conversion."""
    input_file: Path
    output_file: Optional[Path]
    status: ConversionStatus
    error_message: Optional[str] = None
    iso_path: Optional[Path] = None
    stdout: str = ""
    stderr: str = ""


class ConversionEngine:
    """
    Core conversion engine that orchestrates RVZ → ISO → WBFS conversion.
    Uses dolphin-tool for RVZ→ISO and wit for ISO→WBFS.
    """
    
    def __init__(
        self,
        tool_runner: Optional[ToolRunner] = None,
        temp_dir: Optional[Path] = None,
        use_metadata_naming: bool = True,
        max_concurrent: int = 1
    ):
        """
        Initialize the conversion engine.
        
        Args:
            tool_runner: ToolRunner instance. If None, creates a new one.
            temp_dir: Directory for temporary ISO files. If None, uses system temp.
            use_metadata_naming: If True, rename output files with game title and ID
            max_concurrent: Maximum number of concurrent conversions (default: 1 for USB HDD safety)
        """
        self.tool_runner = tool_runner or ToolRunner()
        self.temp_dir = temp_dir or Path(tempfile.gettempdir()) / "rvz2wbfs"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.use_metadata_naming = use_metadata_naming
        self.max_concurrent = max(1, max_concurrent)  # At least 1
        
        # Use global semaphore shared across all ConversionEngine instances
        # This ensures concurrency limits are enforced globally
        global _global_conversion_semaphore, _semaphore_lock
        with _semaphore_lock:
            if _global_conversion_semaphore is None:
                # Initialize global semaphore with the first instance's max_concurrent
                _global_conversion_semaphore = threading.Semaphore(self.max_concurrent)
            elif _global_conversion_semaphore._value != self.max_concurrent:
                # If max_concurrent differs, update the semaphore
                # Note: We can't directly change semaphore value, so we create a new one
                # This is a limitation, but in practice max_concurrent should be consistent
                pass  # Keep existing semaphore - first instance's setting takes precedence
        
        # Metadata lookup for game titles
        self.metadata_lookup = MetadataLookup(tool_runner=self.tool_runner) if use_metadata_naming else None
        
        # Progress callback: (file_path, status, message) -> None
        self.progress_callback: Optional[Callable[[Path, ConversionStatus, str], None]] = None
    
    def set_progress_callback(
        self,
        callback: Callable[[Path, ConversionStatus, str], None]
    ):
        """Set callback for progress updates."""
        self.progress_callback = callback
    
    def _notify_progress(
        self,
        file_path: Path,
        status: ConversionStatus,
        message: str = ""
    ):
        """Notify progress callback if set."""
        if self.progress_callback:
            self.progress_callback(file_path, status, message)
    
    def convert_file(
        self,
        input_rvz: Path,
        output_wbfs: Path,
        keep_iso: bool = False,
        verbose: bool = False
    ) -> ConversionResult:
        """
        Convert a single RVZ file to WBFS.
        Uses semaphore to limit concurrent conversions and prevent I/O overload.
        
        Args:
            input_rvz: Path to input RVZ file
            output_wbfs: Path to output WBFS file
            keep_iso: If True, keep intermediate ISO file
            verbose: Enable verbose tool output
            
        Returns:
            ConversionResult with status and details
        """
        # Acquire global semaphore to limit concurrent conversions
        # This prevents overwhelming slow storage devices (e.g., USB HDD)
        # Using global semaphore ensures all ConversionEngine instances share the same limit
        global _global_conversion_semaphore
        if _global_conversion_semaphore is None:
            # Fallback: create semaphore if somehow not initialized
            with _semaphore_lock:
                if _global_conversion_semaphore is None:
                    _global_conversion_semaphore = threading.Semaphore(self.max_concurrent)
        
        _global_conversion_semaphore.acquire()
        try:
            return self._convert_file_internal(input_rvz, output_wbfs, keep_iso, verbose)
        finally:
            # Always release semaphore, even on error
            _global_conversion_semaphore.release()
    
    def _convert_file_internal(
        self,
        input_rvz: Path,
        output_wbfs: Path,
        keep_iso: bool = False,
        verbose: bool = False
    ) -> ConversionResult:
        """
        Internal conversion method (called with semaphore already acquired).
        
        Args:
            input_rvz: Path to input RVZ file
            output_wbfs: Path to output WBFS file
            keep_iso: If True, keep intermediate ISO file
            verbose: Enable verbose tool output
            
        Returns:
            ConversionResult with status and details
        """
        input_rvz = Path(input_rvz).resolve()
        output_wbfs = Path(output_wbfs).resolve()
        
        # Check if final organized output already exists (if metadata naming is enabled)
        if self.use_metadata_naming and self.metadata_lookup:
            try:
                # Try to get game info from a temporary check (we'll need the WBFS file for this)
                # For now, we'll check after conversion, but we should also check the intermediate output
                pass
            except:
                pass
        
        # Check if intermediate output already exists (only if metadata naming is disabled)
        # With metadata naming, we'll check the final organized location after conversion
        if not self.use_metadata_naming and output_wbfs.exists():
            return ConversionResult(
                input_file=input_rvz,
                output_file=output_wbfs,
                status=ConversionStatus.SKIPPED,
                error_message=f"Output file already exists: {output_wbfs}"
            )
        
        # Check if input exists
        if not input_rvz.exists():
            return ConversionResult(
                input_file=input_rvz,
                output_file=None,
                status=ConversionStatus.FAILED,
                error_message=f"Input file not found: {input_rvz}"
            )
        
        # Validate input is RVZ
        if input_rvz.suffix.lower() != ".rvz":
            return ConversionResult(
                input_file=input_rvz,
                output_file=None,
                status=ConversionStatus.FAILED,
                error_message=f"Input file is not an RVZ file: {input_rvz}"
            )
        
        # Create temporary ISO path
        iso_name = input_rvz.stem + ".iso"
        iso_path = self.temp_dir / iso_name
        
        # Step 1: RVZ → ISO using Dolphin
        self._notify_progress(
            input_rvz,
            ConversionStatus.IN_PROGRESS,
            "Converting RVZ to ISO..."
        )
        
        try:
            exit_code, stdout, stderr = self.tool_runner.run_dolphin_convert(
                input_rvz,
                iso_path,
                verbose=verbose
            )
            
            if exit_code != 0:
                return ConversionResult(
                    input_file=input_rvz,
                    output_file=None,
                    status=ConversionStatus.FAILED,
                    error_message=f"Dolphin conversion failed with exit code {exit_code}",
                    stdout=stdout,
                    stderr=stderr
                )
            
            # Validate ISO was created
            if not iso_path.exists():
                return ConversionResult(
                    input_file=input_rvz,
                    output_file=None,
                    status=ConversionStatus.FAILED,
                    error_message="ISO file was not created by dolphin-tool",
                    stdout=stdout,
                    stderr=stderr
                )
            
            # Validate ISO size
            iso_size = iso_path.stat().st_size
            if iso_size == 0:
                iso_path.unlink()  # Clean up empty file
                return ConversionResult(
                    input_file=input_rvz,
                    output_file=None,
                    status=ConversionStatus.FAILED,
                    error_message="ISO file is empty (0 bytes)",
                    stdout=stdout,
                    stderr=stderr
                )
            
        except Exception as e:
            return ConversionResult(
                input_file=input_rvz,
                output_file=None,
                status=ConversionStatus.FAILED,
                error_message=f"Dolphin conversion error: {str(e)}"
            )
        
        # Step 2: ISO → WBFS using WIT
        self._notify_progress(
            input_rvz,
            ConversionStatus.IN_PROGRESS,
            "Converting ISO to WBFS..."
        )
        
        try:
            exit_code, stdout2, stderr2 = self.tool_runner.run_wit_copy(
                iso_path,
                output_wbfs,
                verbose=verbose
            )
            
            # Combine stdout/stderr from both steps
            combined_stdout = stdout + "\n" + stdout2
            combined_stderr = stderr + "\n" + stderr2
            
            if exit_code != 0:
                # Clean up ISO if not keeping
                if not keep_iso and iso_path.exists():
                    iso_path.unlink()
                
                return ConversionResult(
                    input_file=input_rvz,
                    output_file=None,
                    status=ConversionStatus.FAILED,
                    error_message=f"WIT conversion failed with exit code {exit_code}",
                    stdout=combined_stdout,
                    stderr=combined_stderr,
                    iso_path=iso_path if keep_iso else None
                )
            
            # Validate WBFS was created
            if not output_wbfs.exists():
                if not keep_iso and iso_path.exists():
                    iso_path.unlink()
                
                return ConversionResult(
                    input_file=input_rvz,
                    output_file=None,
                    status=ConversionStatus.FAILED,
                    error_message="WBFS file was not created by wit",
                    stdout=combined_stdout,
                    stderr=combined_stderr,
                    iso_path=iso_path if keep_iso else None
                )
            
            # Validate WBFS size (should be reasonable)
            wbfs_size = output_wbfs.stat().st_size
            if wbfs_size == 0:
                output_wbfs.unlink()
                if not keep_iso and iso_path.exists():
                    iso_path.unlink()
                
                return ConversionResult(
                    input_file=input_rvz,
                    output_file=None,
                    status=ConversionStatus.FAILED,
                    error_message="WBFS file is empty (0 bytes)",
                    stdout=combined_stdout,
                    stderr=combined_stderr,
                    iso_path=iso_path if keep_iso else None
                )
            
        except Exception as e:
            # Clean up ISO if not keeping
            if not keep_iso and iso_path.exists():
                iso_path.unlink()
            
            return ConversionResult(
                input_file=input_rvz,
                output_file=None,
                status=ConversionStatus.FAILED,
                error_message=f"WIT conversion error: {str(e)}",
                iso_path=iso_path if keep_iso else None
            )
        
        # Step 3: Organize with metadata if enabled (folder structure)
        final_output_wbfs = output_wbfs
        if self.use_metadata_naming and self.metadata_lookup:
            try:
                self._notify_progress(
                    input_rvz,
                    ConversionStatus.IN_PROGRESS,
                    "Looking up game metadata..."
                )
                
                game_id, title = self.metadata_lookup.get_game_info(output_wbfs)
                
                if game_id and title:
                    # Create folder structure: "Title [GAMEID]/GAMEID.wbfs"
                    folder_name = self.metadata_lookup.format_filename(title, game_id, "")
                    
                    # Create folder in output directory
                    game_folder = output_wbfs.parent / folder_name
                    game_folder.mkdir(parents=True, exist_ok=True)
                    
                    # Move file to folder with just game ID as filename
                    final_output_wbfs = game_folder / f"{game_id}.wbfs"
                    
                    # Check if target file already exists (from previous conversion)
                    if final_output_wbfs.exists():
                        # Target already exists - this is a duplicate conversion
                        # Delete the file we just created to avoid duplicates
                        duplicate_removed = False
                        try:
                            if output_wbfs.exists() and output_wbfs != final_output_wbfs:
                                # Check file sizes to make sure they're the same
                                if output_wbfs.stat().st_size == final_output_wbfs.stat().st_size:
                                    output_wbfs.unlink()
                                    duplicate_removed = True
                                    self._notify_progress(
                                        input_rvz,
                                        ConversionStatus.SKIPPED,
                                        f"Target file already exists, removed duplicate: {output_wbfs.name}"
                                    )
                                else:
                                    # Different sizes - might be different versions, keep both
                                    self._notify_progress(
                                        input_rvz,
                                        ConversionStatus.IN_PROGRESS,
                                        f"Warning: Target exists but different size, keeping both files"
                                    )
                        except Exception as e:
                            self._notify_progress(
                                input_rvz,
                                ConversionStatus.IN_PROGRESS,
                                f"Warning: Could not remove duplicate file: {e}"
                            )
                        # Use the existing file as the final output
                        final_output_wbfs = game_folder / f"{game_id}.wbfs"
                    elif final_output_wbfs != output_wbfs:
                        # Target doesn't exist, safe to move
                        try:
                            output_wbfs.rename(final_output_wbfs)
                            self._notify_progress(
                                input_rvz,
                                ConversionStatus.IN_PROGRESS,
                                f"Organized into: {game_folder.name}/{final_output_wbfs.name}"
                            )
                        except Exception as e:
                            # Rename failed - use original location
                            self._notify_progress(
                                input_rvz,
                                ConversionStatus.IN_PROGRESS,
                                f"Warning: Could not move file to organized location: {e}"
                            )
                            final_output_wbfs = output_wbfs
            except Exception as e:
                # Metadata lookup failed - use original filename
                # Don't fail the conversion, just log the warning
                self._notify_progress(
                    input_rvz,
                    ConversionStatus.IN_PROGRESS,
                    f"Metadata lookup failed, using original filename: {e}"
                )
        
        # Step 4: Cleanup
        if not keep_iso and iso_path.exists():
            try:
                iso_path.unlink()
            except Exception as e:
                # Log but don't fail the conversion
                print(f"Warning: Failed to delete temporary ISO {iso_path}: {e}")
        
        # Success!
        self._notify_progress(
            input_rvz,
            ConversionStatus.SUCCESS,
            f"Successfully converted to {final_output_wbfs}"
        )
        
        return ConversionResult(
            input_file=input_rvz,
            output_file=final_output_wbfs,
            status=ConversionStatus.SUCCESS,
            stdout=combined_stdout,
            stderr=combined_stderr,
            iso_path=iso_path if keep_iso else None
        )
    
    def convert_directory(
        self,
        input_dir: Path,
        output_dir: Path,
        keep_iso: bool = False,
        preserve_structure: bool = True,
        verbose: bool = False
    ) -> list[ConversionResult]:
        """
        Convert all RVZ files in a directory (recursively).
        
        Args:
            input_dir: Directory containing RVZ files
            output_dir: Output directory for WBFS files
            keep_iso: If True, keep intermediate ISO files
            preserve_structure: If True, preserve directory structure in output
            verbose: Enable verbose tool output
            
        Returns:
            List of ConversionResult for each file processed
        """
        input_dir = Path(input_dir).resolve()
        output_dir = Path(output_dir).resolve()
        
        if not input_dir.exists():
            return [ConversionResult(
                input_file=input_dir,
                output_file=None,
                status=ConversionStatus.FAILED,
                error_message=f"Input directory not found: {input_dir}"
            )]
        
        # Find all RVZ files
        rvz_files = list(input_dir.rglob("*.rvz"))
        rvz_files.extend(input_dir.rglob("*.RVZ"))
        
        if not rvz_files:
            return [ConversionResult(
                input_file=input_dir,
                output_file=None,
                status=ConversionStatus.FAILED,
                error_message=f"No RVZ files found in {input_dir}"
            )]
        
        results = []
        
        for rvz_file in rvz_files:
            # Determine output path
            if preserve_structure:
                # Preserve relative path structure
                rel_path = rvz_file.relative_to(input_dir)
                output_path = output_dir / rel_path.with_suffix(".wbfs")
            else:
                # Flat output
                output_path = output_dir / (rvz_file.stem + ".wbfs")
            
            # Convert file
            result = self.convert_file(
                rvz_file,
                output_path,
                keep_iso=keep_iso,
                verbose=verbose
            )
            results.append(result)
        
        return results

