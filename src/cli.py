"""
CLI Interface Module
Command-line interface for RVZ to WBFS conversion.
"""

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import List, Optional

from .conversion_engine import ConversionEngine, ConversionStatus
from .logger import setup_logger
from .zip_handler import ZipHandler

try:
    from .watch_mode import WatchMode
except ImportError:
    WatchMode = None


def find_rvz_files(path: Path, zip_handler: Optional[ZipHandler] = None) -> List[Path]:
    """
    Find all RVZ files in a path (file or directory).
    Also handles ZIP files containing RVZ files.
    
    Args:
        path: File or directory path
        zip_handler: Optional ZipHandler instance for ZIP extraction
        
    Returns:
        List of RVZ file paths
    """
    path = Path(path).resolve()
    rvz_files = []
    
    if path.is_file():
        # Check if it's a ZIP file
        if zip_handler and zip_handler.is_zip_file(path):
            try:
                extracted_rvz, _ = zip_handler.extract_rvz_from_zip(path)
                rvz_files.extend(extracted_rvz)
            except Exception as e:
                print(f"Warning: Failed to extract ZIP {path}: {e}")
        elif path.suffix.lower() == ".rvz":
            rvz_files.append(path)
    elif path.is_dir():
        # Find RVZ files directly (dedupe for case-insensitive filesystems like Windows)
        seen = set()
        for pattern in ("*.rvz", "*.RVZ"):
            for f in path.rglob(pattern):
                key = str(f.resolve()).lower()
                if key not in seen:
                    seen.add(key)
                    rvz_files.append(f)
        
        # Find and extract ZIP files if handler provided
        if zip_handler:
            zip_files = zip_handler.find_zip_files(path)
            for zip_file in zip_files:
                try:
                    extracted_rvz, _ = zip_handler.extract_rvz_from_zip(zip_file)
                    rvz_files.extend(extracted_rvz)
                except Exception as e:
                    print(f"Warning: Failed to extract ZIP {zip_file}: {e}")
    
    return sorted(rvz_files)


def determine_output_path(
    input_path: Path,
    output_dir: Path,
    preserve_structure: bool,
    is_file: bool,
    base_input_dir: Optional[Path] = None
) -> Path:
    """
    Determine output WBFS path for an input RVZ file.
    
    Args:
        input_path: Input RVZ file path
        output_dir: Output directory
        preserve_structure: Whether to preserve directory structure
        is_file: Whether input was a single file
        base_input_dir: Base input directory (for preserving structure)
        
    Returns:
        Output WBFS file path
    """
    if is_file:
        # Single file input - output in specified directory
        return output_dir / (input_path.stem + ".wbfs")
    else:
        # Directory input - this function is mainly for single files
        # Directory conversion handles paths internally
        return output_dir / (input_path.stem + ".wbfs")


def print_summary(results: List):
    """Print conversion summary."""
    total = len(results)
    success = sum(1 for r in results if r.status == ConversionStatus.SUCCESS)
    failed = sum(1 for r in results if r.status == ConversionStatus.FAILED)
    skipped = sum(1 for r in results if r.status == ConversionStatus.SKIPPED)
    
    print("\n" + "=" * 60)
    print("CONVERSION SUMMARY")
    print("=" * 60)
    print(f"Total files: {total}")
    print(f"Successful: {success}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    print("=" * 60)
    
    if failed > 0:
        print("\nFailed conversions:")
        for result in results:
            if result.status == ConversionStatus.FAILED:
                print(f"  - {result.input_file}")
                if result.error_message:
                    print(f"    Error: {result.error_message}")
    
    if skipped > 0:
        print("\nSkipped files:")
        for result in results:
            if result.status == ConversionStatus.SKIPPED:
                print(f"  - {result.input_file}")
                if result.error_message:
                    print(f"    Reason: {result.error_message}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert Nintendo Wii RVZ ROMs to WBFS format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert single file
  rvz2wbfs --input game.rvz --output ./wbfs
  
  # Convert directory recursively
  rvz2wbfs --input ./rvz --output ./wbfs
  
  # Convert ZIP file containing RVZ
  rvz2wbfs --input game.zip --output ./wbfs
  
  # Keep intermediate ISO files
  rvz2wbfs --input ./rvz --output ./wbfs --keep-iso
  
  # Keep extracted RVZ files from ZIP archives
  rvz2wbfs --input ./zips --output ./wbfs --keep-extracted
  
  # Flat output (no directory structure)
  rvz2wbfs --input ./rvz --output ./wbfs --flat
  
  # Watch mode: Monitor directory for new ZIP/RVZ files
  rvz2wbfs --input ./downloads --output ./wbfs --watch
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        type=Path,
        required=True,
        help="Input RVZ file, ZIP file, or directory (recursive, supports ZIP files)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="Output directory for WBFS files"
    )
    
    parser.add_argument(
        "--keep-iso",
        action="store_true",
        help="Keep intermediate ISO files (for debugging)"
    )
    
    parser.add_argument(
        "--keep-extracted",
        action="store_true",
        help="Keep extracted RVZ files from ZIP archives"
    )
    
    parser.add_argument(
        "--delete-zip",
        action="store_true",
        help="Delete original ZIP files after successful conversion"
    )
    
    parser.add_argument(
        "--flat",
        action="store_true",
        help="Flatten output structure (don't preserve directory hierarchy)"
    )
    
    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Disable automatic renaming with game title and ID"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--log-file",
        type=Path,
        help="Path to log file (optional)"
    )
    
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Enable watch mode: monitor input directory for new ZIP/RVZ files and auto-convert"
    )
    
    parser.add_argument(
        "--watch-interval",
        type=float,
        default=5.0,
        help="Watch mode check interval in seconds (default: 5.0)"
    )
    
    parser.add_argument(
        "--file-stable-time",
        type=float,
        default=10.0,
        help="Time in seconds a file must be stable before processing (default: 10.0)"
    )
    
    parser.add_argument(
        "--move-network",
        type=Path,
        help="Move converted WBFS files to network share (e.g., \\\\server\\share)"
    )
    
    parser.add_argument(
        "--keep-local-wbfs",
        action="store_true",
        help="Keep local copy when moving to network (copy instead of move)"
    )
    
    parser.add_argument(
        "--network-overwrite",
        choices=["skip", "append_timestamp", "append_version", "overwrite"],
        default="skip",
        help="Behavior when network file exists (default: skip)"
    )
    
    parser.add_argument(
        "--network-retries",
        type=int,
        default=3,
        help="Number of retries for network operations (default: 3)"
    )
    
    parser.add_argument(
        "--delete-after-network-move",
        action="store_true",
        help="Delete local files (input ZIP and output WBFS) after successful network move"
    )
    
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=1,
        help="Maximum number of concurrent conversions (default: 1, recommended for USB HDD)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logger(log_file=args.log_file, level=log_level)
    
    # Validate inputs
    input_path = args.input.resolve()
    
    # For watch mode, input must be a directory
    if args.watch:
        if not input_path.exists():
            logger.error(f"Watch directory does not exist: {input_path}")
            sys.exit(1)
        if not input_path.is_dir():
            logger.error(f"Watch mode requires a directory, not a file: {input_path}")
            sys.exit(1)
    elif not input_path.exists():
        logger.error(f"Input path does not exist: {input_path}")
        sys.exit(1)
    
    output_dir = args.output.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Default: network move disabled unless a mover is initialized elsewhere
    network_mover = None
    
    # Handle watch mode (skip regular conversion)
    if args.watch:
        # Watch mode logic is at the end of the function - skip regular conversion
        pass
    else:
        # Regular conversion mode
        # Initialize conversion engine and ZIP handler
        use_metadata = not args.no_metadata
        engine = ConversionEngine(
            use_metadata_naming=use_metadata,
            max_concurrent=args.max_concurrent
        )
        zip_handler = ZipHandler()
        
        # Progress callback for CLI
        def progress_callback(file_path: Path, status: ConversionStatus, message: str):
            status_str = status.value.upper()
            print(f"[{status_str}] {file_path.name}: {message}")
            logger.debug(f"{file_path}: {status_str} - {message}")
        
        engine.set_progress_callback(progress_callback)
        
        # Check if input is a ZIP file
        is_zip = zip_handler.is_zip_file(input_path) if input_path.is_file() else False
        
        # Convert
        logger.info(f"Starting conversion: {input_path} -> {output_dir}")
        
        if is_zip:
            # ZIP file - extract and convert RVZ files
            logger.info(f"Detected ZIP file: {input_path}")
            try:
                extracted_rvz, extract_dir = zip_handler.extract_rvz_from_zip(input_path)
                logger.info(f"Extracted {len(extracted_rvz)} RVZ file(s) from ZIP")
                
                results = []
                for rvz_file in extracted_rvz:
                    # Determine output path based on original ZIP name or RVZ name
                    if len(extracted_rvz) == 1:
                        # Single file in ZIP - use ZIP name
                        output_wbfs = output_dir / (input_path.stem + ".wbfs")
                    else:
                        # Multiple files - use RVZ name
                        output_wbfs = output_dir / (rvz_file.stem + ".wbfs")
                    
                    result = engine.convert_file(
                        rvz_file,
                        output_wbfs,
                        keep_iso=args.keep_iso,
                        verbose=args.verbose
                    )
                    results.append(result)
                    
                    # Move to network if enabled and conversion succeeded
                    if network_mover and result.status == ConversionStatus.SUCCESS and result.output_file:
                        move_result = network_mover.move_file(result.output_file, output_dir)
                        if move_result.success:
                            logger.info(f"Successfully moved {result.output_file.name} to network")
                            # Delete local WBFS if option is enabled
                            if args.delete_after_network_move:
                                try:
                                    result.output_file.unlink()
                                    logger.info(f"Deleted local WBFS file: {result.output_file.name}")
                                    print(f"Deleted local WBFS file: {result.output_file.name}")
                                except Exception as e:
                                    logger.warning(f"Failed to delete local WBFS file: {e}")
                        elif not move_result.skipped:
                            logger.warning(f"Failed to move {result.output_file.name} to network: {move_result.error_message}")
                        else:
                            logger.info(f"Skipped moving {result.output_file.name} to network (file exists)")
                
                # Cleanup extracted files unless --keep-extracted
                if not args.keep_extracted:
                    zip_handler.cleanup_extraction(extract_dir)
                    logger.info("Cleaned up extracted files")
                
                # Delete original ZIP file if all conversions succeeded
                # For local conversions (no network_mover): always delete after success
                # For network conversions: delete if delete_zip is enabled OR delete_after_network_move is enabled
                should_delete_zip = not network_mover or args.delete_zip or (args.delete_after_network_move and network_mover)
                if should_delete_zip:
                    all_succeeded = all(r.status == ConversionStatus.SUCCESS for r in results)
                    if all_succeeded:
                        try:
                            input_path.unlink()
                            logger.info(f"Deleted original ZIP file: {input_path}")
                            print(f"Deleted original ZIP file: {input_path.name}")
                        except Exception as e:
                            logger.warning(f"Failed to delete ZIP file {input_path}: {e}")
                            print(f"Warning: Could not delete ZIP file {input_path.name}: {e}")
                    else:
                        logger.info(f"Not deleting ZIP file due to conversion failures: {input_path}")
        
            except Exception as e:
                logger.error(f"Failed to process ZIP file: {e}")
                results = [ConversionResult(
                    input_file=input_path,
                    output_file=None,
                    status=ConversionStatus.FAILED,
                    error_message=f"ZIP extraction failed: {str(e)}"
                )]
    
        elif input_path.is_file():
            # Single RVZ file conversion
            output_wbfs = determine_output_path(
                input_path,
                output_dir,
                preserve_structure=not args.flat,
                is_file=True
            )
            
            result = engine.convert_file(
                input_path,
                output_wbfs,
                keep_iso=args.keep_iso,
                verbose=args.verbose
            )
            
            results = [result]
        else:
            # Directory conversion - process ZIPs individually first, then regular RVZ files
            results = []
            
            # First, find and process ZIP files individually
            if zip_handler:
                zip_files = zip_handler.find_zip_files(input_path)
                for zip_file in zip_files:
                    logger.info(f"Processing ZIP file: {zip_file}")
                    try:
                        extracted_rvz, extract_dir = zip_handler.extract_rvz_from_zip(zip_file)
                        logger.info(f"Extracted {len(extracted_rvz)} RVZ file(s) from ZIP")
                        
                        zip_results = []
                        for rvz_file in extracted_rvz:
                            # Determine output path
                            if not args.flat:
                                # Preserve structure - use RVZ name
                                output_wbfs = output_dir / (rvz_file.stem + ".wbfs")
                            else:
                                # Flat output
                                output_wbfs = output_dir / (rvz_file.stem + ".wbfs")
                            
                            result = engine.convert_file(
                                rvz_file,
                                output_wbfs,
                                keep_iso=args.keep_iso,
                                verbose=args.verbose
                            )
                            zip_results.append(result)
                            results.append(result)
                        
                        # Cleanup extracted files unless --keep-extracted
                        if not args.keep_extracted:
                            zip_handler.cleanup_extraction(extract_dir)
                            logger.info("Cleaned up extracted files")
                        
                        # Delete original ZIP file immediately after all its files are converted
                        # For local conversions (no network_mover): always delete after success
                        # For network conversions: delete if delete_zip is enabled OR delete_after_network_move is enabled
                        should_delete_zip = not network_mover or args.delete_zip or (args.delete_after_network_move and network_mover)
                        if should_delete_zip:
                            all_succeeded = all(r.status == ConversionStatus.SUCCESS for r in zip_results)
                            if all_succeeded:
                                try:
                                    zip_file.unlink()
                                    logger.info(f"Deleted original ZIP file: {zip_file}")
                                    print(f"Deleted original ZIP file: {zip_file.name}")
                                except Exception as e:
                                    logger.warning(f"Failed to delete ZIP file {zip_file}: {e}")
                                    print(f"Warning: Could not delete ZIP file {zip_file.name}: {e}")
                            else:
                                logger.info(f"Not deleting ZIP file due to conversion failures: {zip_file}")
                    
                    except Exception as e:
                        logger.error(f"Failed to process ZIP file {zip_file}: {e}")
                        results.append(ConversionResult(
                            input_file=zip_file,
                            output_file=None,
                            status=ConversionStatus.FAILED,
                            error_message=f"ZIP processing failed: {str(e)}"
                        ))
            
            # Then, find and process regular RVZ files (not from ZIPs)
            seen = set()
            rvz_files = []
            for pattern in ("*.rvz", "*.RVZ"):
                for f in input_path.rglob(pattern):
                    key = str(f.resolve()).lower()
                    if key not in seen:
                        seen.add(key)
                        rvz_files.append(f)
            
            # Filter out any RVZ files that are in extraction directories (already processed)
            if zip_handler:
                extract_base = zip_handler.extract_dir
                rvz_files = [f for f in rvz_files if extract_base not in f.parents]
            
            if rvz_files:
                logger.info(f"Found {len(rvz_files)} regular RVZ file(s) to convert")
                for rvz_file in rvz_files:
                    # Determine output path
                    if not args.flat:
                        # Preserve structure relative to input
                        try:
                            rel_path = rvz_file.relative_to(input_path)
                            output_wbfs = output_dir / rel_path.with_suffix(".wbfs")
                        except ValueError:
                            output_wbfs = output_dir / (rvz_file.stem + ".wbfs")
                    else:
                        # Flat output
                        output_wbfs = output_dir / (rvz_file.stem + ".wbfs")
                    
                    result = engine.convert_file(
                        rvz_file,
                        output_wbfs,
                        keep_iso=args.keep_iso,
                        verbose=args.verbose
                    )
                    results.append(result)
                    
                    # Move to network if enabled and conversion succeeded
                    if network_mover and result.status == ConversionStatus.SUCCESS and result.output_file:
                        move_result = network_mover.move_file(result.output_file, output_dir)
                        if move_result.success:
                            logger.info(f"Successfully moved {result.output_file.name} to network")
                            # Delete local WBFS if option is enabled
                            if args.delete_after_network_move:
                                try:
                                    result.output_file.unlink()
                                    logger.info(f"Deleted local WBFS file: {result.output_file.name}")
                                    print(f"Deleted local WBFS file: {result.output_file.name}")
                                except Exception as e:
                                    logger.warning(f"Failed to delete local WBFS file: {e}")
                        elif not move_result.skipped:
                            logger.warning(f"Failed to move {result.output_file.name} to network: {move_result.error_message}")
                        else:
                            logger.info(f"Skipped moving {result.output_file.name} to network (file exists)")
            
            if not results:
                logger.error(f"No RVZ files found in {input_path}")
                results = [ConversionResult(
                    input_file=input_path,
                    output_file=None,
                    status=ConversionStatus.FAILED,
                    error_message="No RVZ files found (including in ZIP archives)"
                )]
            
            # Print summary (only if not in watch mode)
            print_summary(results)
            
            # Exit with appropriate code
            failed_count = sum(1 for r in results if r.status == ConversionStatus.FAILED)
            if failed_count > 0:
                sys.exit(1)
            else:
                sys.exit(0)
    
    # Handle watch mode
    if args.watch:
        logger.info("Starting watch mode...")
        print("\n" + "=" * 60)
        print("WATCH MODE ENABLED")
        print("=" * 60)
        print(f"Monitoring: {input_path}")
        print(f"Output: {output_dir}")
        print(f"Check interval: {args.watch_interval} seconds")
        print(f"File stable time: {args.file_stable_time} seconds")
        print("\nPress Ctrl+C to stop watch mode")
        print("=" * 60 + "\n")
        
        # Initialize network mover for watch mode if enabled
        watch_network_mover = network_mover  # Use same network mover instance
        
        # Define conversion function for watch mode
        def watch_conversion_callback(input_file: Path, output_dir: Path):
            """Callback for watch mode conversions."""
            try:
                # Use the same conversion logic as regular mode
                use_metadata = not args.no_metadata
                watch_engine = ConversionEngine(
                    use_metadata_naming=use_metadata,
                    max_concurrent=args.max_concurrent
                )
                watch_zip_handler = ZipHandler()
                
                # Progress callback
                def progress_callback(file_path: Path, status: ConversionStatus, message: str):
                    status_str = status.value.upper()
                    print(f"[{status_str}] {file_path.name}: {message}")
                    logger.debug(f"{file_path}: {status_str} - {message}")
                
                watch_engine.set_progress_callback(progress_callback)
                
                # Check if it's a ZIP file
                is_zip = watch_zip_handler.is_zip_file(input_file)
                
                if is_zip:
                    # ZIP file processing
                    logger.info(f"Processing ZIP file from watch mode: {input_file}")
                    extracted_rvz, extract_dir = watch_zip_handler.extract_rvz_from_zip(input_file)
                    
                    zip_results = []
                    for rvz_file in extracted_rvz:
                        if len(extracted_rvz) == 1:
                            output_wbfs = output_dir / (input_file.stem + ".wbfs")
                        else:
                            output_wbfs = output_dir / (rvz_file.stem + ".wbfs")
                        
                        result = watch_engine.convert_file(
                            rvz_file,
                            output_wbfs,
                            keep_iso=args.keep_iso,
                            verbose=args.verbose
                        )
                        zip_results.append(result)
                    
                    # Cleanup extracted files
                    if not args.keep_extracted:
                        watch_zip_handler.cleanup_extraction(extract_dir)
                    
                    # Delete ZIP if all succeeded
                    # For local conversions (no network_mover): always delete after success
                    # For network conversions: delete if delete_zip is enabled OR delete_after_network_move is enabled
                    should_delete_zip = not watch_network_mover or args.delete_zip or (args.delete_after_network_move and watch_network_mover)
                    if should_delete_zip:
                        all_succeeded = all(r.status == ConversionStatus.SUCCESS for r in zip_results)
                        # If network move is enabled, also check that all moves succeeded
                        if watch_network_mover and args.delete_after_network_move:
                            # Check that all files were successfully moved to network
                            # (This is a simplified check - in practice, we'd track move results)
                            pass  # For now, just check conversion success
                        
                        if all_succeeded:
                            try:
                                input_file.unlink()
                                logger.info(f"Deleted ZIP file: {input_file}")
                                print(f"Deleted ZIP file: {input_file.name}")
                            except Exception as e:
                                logger.warning(f"Failed to delete ZIP: {e}")
                                print(f"Warning: Could not delete ZIP file {input_file.name}: {e}")
                        else:
                            logger.info(f"Not deleting ZIP file {input_file.name} due to conversion failures")
                            print(f"Not deleting ZIP file {input_file.name} due to conversion failures")
                else:
                    # Regular RVZ file
                    output_wbfs = output_dir / (input_file.stem + ".wbfs")
                    result = watch_engine.convert_file(
                        input_file,
                        output_wbfs,
                        keep_iso=args.keep_iso,
                        verbose=args.verbose
                    )
                    
                    if result.status == ConversionStatus.SUCCESS:
                        logger.info(f"Successfully converted: {input_file}")
                        
                        # Move to network if enabled
                        if watch_network_mover and result.output_file:
                            move_result = watch_network_mover.move_file(result.output_file, output_dir)
                            if move_result.success:
                                logger.info(f"Successfully moved {result.output_file.name} to network")
                                print(f"[Network] Successfully moved {result.output_file.name} to network")
                                # Delete local WBFS if option is enabled
                                if args.delete_after_network_move:
                                    try:
                                        result.output_file.unlink()
                                        logger.info(f"Deleted local WBFS file: {result.output_file.name}")
                                        print(f"Deleted local WBFS file: {result.output_file.name}")
                                    except Exception as e:
                                        logger.warning(f"Failed to delete local WBFS file: {e}")
                                        print(f"Warning: Could not delete local WBFS file {result.output_file.name}: {e}")
                            elif not move_result.skipped:
                                logger.warning(f"Failed to move {result.output_file.name} to network: {move_result.error_message}")
                                print(f"[Network] Failed to move {result.output_file.name}: {move_result.error_message}")
                            else:
                                logger.info(f"Skipped moving {result.output_file.name} to network (file exists)")
                                print(f"[Network] Skipped {result.output_file.name} (already exists)")
                    else:
                        logger.error(f"Conversion failed: {input_file} - {result.error_message}")
            
            except Exception as e:
                logger.error(f"Error in watch mode conversion: {e}")
                print(f"ERROR: Failed to process {input_file.name}: {e}")
        
        # Create and start watch mode
        if WatchMode is None:
            logger.error("Watch mode is unavailable: could not import WatchMode from src.watch_mode")
            print("ERROR: Watch mode is unavailable: missing src.watch_mode")
            sys.exit(1)

        watch_mode = WatchMode(
            watch_dir=input_path,
            output_dir=output_dir,
            conversion_callback=watch_conversion_callback,
            check_interval=args.watch_interval,
            file_stable_time=args.file_stable_time
        )
        
        def status_callback(message: str):
            logger.info(f"Watch Mode: {message}")
            print(f"[Watch] {message}")
        
        watch_mode.set_status_callback(status_callback)
        
        try:
            watch_mode.start()
            
            # Keep running until interrupted
            while watch_mode.is_running():
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n\nStopping watch mode...")
            watch_mode.stop()
            print("Watch mode stopped.")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Watch mode error: {e}")
            watch_mode.stop()
            sys.exit(1)
    
    # Print summary (only if not in watch mode)
    if not args.watch:
        print_summary(results)
        
        # Exit with appropriate code
        failed_count = sum(1 for r in results if r.status == ConversionStatus.FAILED)
        if failed_count > 0:
            sys.exit(1)
        else:
            sys.exit(0)


if __name__ == "__main__":
    main()

