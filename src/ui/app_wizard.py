"""
Main Application Window - Wizard-Based UI
Bootstrap and orchestration for the wizard-based interface.
"""

import customtkinter as ctk
from pathlib import Path
from typing import Optional
import threading
import queue

from .theme import COLORS, SPACING, configure_theme
from .wizard.wizard_controller import WizardController, ConversionConfig
from .wizard.page_input import PageInput
from .wizard.page_output import PageOutput
from .wizard.page_network import PageNetwork
from .wizard.page_progress import PageProgress
from .shared.navigation import NavigationBar

from ..conversion_engine import ConversionEngine, ConversionStatus, ConversionResult
from ..logger import setup_logger
from ..zip_handler import ZipHandler
from ..watch_mode import WatchMode
from ..network_mover import NetworkMover, OverwriteBehavior
from ..tool_downloader import ToolDownloader

from tkinter import messagebox


class ConversionUI:
    """
    Wizard-based desktop GUI for RVZ to WBFS conversion.
    Multi-page guided workflow with state management.
    """
    
    def __init__(self, root: ctk.CTk):
        """Initialize the wizard-based UI."""
        self.root = root
        
        # Configure theme first
        configure_theme()
        
        # Window configuration
        self.root.title("WiiAutoConvert - RVZ to WBFS Converter")
        self.root.geometry("1200x850")  # Increased from 1100x750 for better visibility on progress page
        self.root.minsize(700, 600)
        
        # Set window background
        self.root.configure(fg_color=COLORS["bg"])
        
        # Optional: Windows-only window alpha for glass effect
        try:
            self.root.attributes("-alpha", 0.97)
        except:
            pass  # Not supported on all platforms
        
        # State management
        self.conversion_thread: Optional[threading.Thread] = None
        self.is_converting = False
        self.cancel_requested = False
        self.zip_handler = ZipHandler()
        self.watch_mode: Optional[WatchMode] = None
        self.is_watching = False
        self.network_mover: Optional[NetworkMover] = None
        
        # Queue for thread-safe UI updates
        self.update_queue = queue.Queue()
        
        # Logger
        self.logger = setup_logger()
        
        # Check for required tools on startup
        self._check_tools_on_startup()
        
        # Build wizard UI
        self._build_wizard()
        
        # Start processing UI update queue
        self.root.after(100, self._process_queue)
    
    def _check_tools_on_startup(self):
        """Check if required tools are available, download if missing."""
        try:
            downloader = ToolDownloader()
        except Exception as e:
            # Log error and show message
            self.logger.error(f"Failed to initialize tool downloader: {e}", exc_info=True)
            messagebox.showerror(
                "Initialization Error",
                f"Failed to initialize tool downloader:\n{str(e)}\n\n"
                "Please check tool_download.log for details."
            )
            return
        dolphin_ok = downloader.check_dolphin_tool()
        wit_ok = downloader.check_wit()
        
        if not dolphin_ok or not wit_ok:
            # Show dialog asking if user wants to download
            missing = []
            if not dolphin_ok:
                missing.append("Dolphin Tool")
            if not wit_ok:
                missing.append("WIT")
            
            msg = (
                f"The following required tools are missing:\n\n"
                f"{', '.join(missing)}\n\n"
                "Would you like to download them automatically?\n\n"
                "Note: This requires an internet connection."
            )
            
            result = messagebox.askyesno(
                "Missing Tools",
                msg,
                icon="question"
            )
            
            if result:
                # Download tools in background thread
                def download_tools():
                    try:
                        import logging
                        tool_logger = logging.getLogger('src.tool_downloader')
                        tool_logger.info("Tool download thread started")
                        
                        def progress_callback(msg):
                            self.update_queue.put(("tool_download", msg))
                            tool_logger.info(f"Progress: {msg}")
                        
                        if not dolphin_ok:
                            self.update_queue.put(("tool_download", "Starting Dolphin download..."))
                            success, msg = downloader.download_dolphin(progress_callback)
                            if not success:
                                self.update_queue.put(("tool_download", f"Dolphin: {msg}"))
                        
                        if not wit_ok:
                            self.update_queue.put(("tool_download", "Starting WIT download..."))
                            success, msg = downloader.download_wit(progress_callback)
                            if not success:
                                self.update_queue.put(("tool_download", f"WIT download failed: {msg}"))
                        
                        # Wait a moment for files to be written
                        import time
                        time.sleep(0.5)
                        
                        # Check final status
                        final_dolphin = downloader.check_dolphin_tool()
                        final_wit = downloader.check_wit()
                        
                        if final_dolphin and final_wit:
                            self.update_queue.put(("tool_download", "success"))
                        else:
                            missing_final = []
                            if not final_dolphin:
                                missing_final.append("Dolphin Tool")
                            if not final_wit:
                                missing_final.append("WIT")
                            self.update_queue.put(("tool_download", f"failed:{','.join(missing_final)}"))
                    except Exception as e:
                        import logging
                        import traceback
                        tool_logger = logging.getLogger('src.tool_downloader')
                        error_msg = f"Error during tool download: {str(e)}"
                        tool_logger.error(error_msg, exc_info=True)
                        self.update_queue.put(("tool_download", error_msg))
                
                threading.Thread(target=download_tools, daemon=True).start()
            else:
                # User declined, show instructions
                instructions = (
                    "To use WiiAutoConvert, you need to download the following tools:\n\n"
                )
                if not dolphin_ok:
                    instructions += (
                        "• Dolphin Tool:\n"
                        "  Download from: https://dolphin-emu.org/download/\n"
                        f"  Extract DolphinTool.exe to: {downloader.dolphin_dir}\n\n"
                    )
                if not wit_ok:
                    instructions += (
                        "• WIT (Wiimms ISO Toolset):\n"
                        "  Download from: https://wit.wiimm.de/\n"
                        f"  Extract wit.exe to: {downloader.wit_dir}\n\n"
                    )
                instructions += "The application will check for these tools on next launch."
                
                messagebox.showinfo("Manual Tool Installation", instructions)
    
    def _build_wizard(self):
        """Build the wizard-based user interface."""
        # Main container with minimal top padding
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=SPACING["card_gap"], pady=(0, SPACING["card_gap"]))
        
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create navigation bar (will be positioned at bottom for pages 2-3, top for others)
        nav = NavigationBar(
            main_container,
            on_back=None,  # Will be set after wizard creation
            on_next=None,  # Will be set after wizard creation
            next_text="Next",
            show_watch=False,
            on_watch=None
        )
        self.nav = nav
        
        # Create wizard controller (will pack before navigation)
        self.wizard = WizardController(
            main_container,
            on_start_conversion=self._start_conversion_from_config,
            on_start_watch=self._start_watch_from_config
        )
        
        # Set navigation callbacks now that wizard exists
        self.nav.back_button.configure(command=self.wizard.previous_page)
        self.nav.next_button.configure(command=self.wizard.next_page)
        
        # Create pages
        config = self.wizard.config
        
        # Page 1: Input Selection
        page1 = PageInput(main_container, config, on_update=lambda: self.wizard._update_navigation())
        self.wizard.add_page(page1, validator=lambda: page1.is_valid())
        
        # Page 2: Output Directory
        page2 = PageOutput(main_container, config, on_update=lambda: self.wizard._update_navigation())
        self.wizard.add_page(page2, validator=lambda: page2.is_valid())
        
        # Page 3: Network & Advanced Options
        page3 = PageNetwork(main_container, config, on_update=lambda: self.wizard._update_navigation())
        self.wizard.add_page(page3, validator=lambda: page3.is_valid())
        
        # Page 4: Conversion Progress
        page4 = PageProgress(
            main_container,
            on_cancel=self._cancel_conversion,
            on_watch=self._toggle_watch_mode
        )
        self.wizard.add_page(page4, validator=lambda: True)  # Always valid
        
        self.progress_page = page4
        
        # Set navigation reference
        self.wizard.set_navigation(nav)
        
        # Initial navigation update
        self.wizard._update_navigation()
        
        # Start wizard on page 0
        self.wizard.start()
    
    def _start_conversion_from_config(self, config: ConversionConfig):
        """Start conversion using wizard config."""
        # Validate inputs
        if not config.input_items:
            messagebox.showwarning("No Input", "Please add at least one RVZ file or folder.")
            return
        
        if not config.output_dir:
            messagebox.showwarning("No Output", "Please select an output directory.")
            return
        
        # Update state
        self.is_converting = True
        self.cancel_requested = False
        
        # Initialize network mover if enabled
        self.network_mover = None
        if config.enable_network_move and config.network_path:
            try:
                network_path = Path(config.network_path)
                overwrite_behavior = OverwriteBehavior(config.overwrite_mode)
                
                # Note: keep_local is set to False if delete_after_network_move is enabled
                delete_after_move = config.cleanup.delete_after_network_move
                keep_local = config.keep_local_copy and not delete_after_move
                
                self.network_mover = NetworkMover(
                    network_root=network_path,
                    keep_local=keep_local,
                    overwrite_behavior=overwrite_behavior,
                    max_retries=config.retries,
                    retry_delay=2.0
                )
                
                def network_status_callback(message: str):
                    self.update_queue.put(("log", f"[Network] {message}"))
                
                self.network_mover.set_status_callback(network_status_callback)
                self.update_queue.put(("log", f"Network mover enabled: {network_path}"))
            except Exception as e:
                self.update_queue.put(("log", f"Warning: Failed to initialize network mover: {e}"))
        
        # Navigate to progress page
        self.wizard.go_to_page(3)  # Progress page is index 3
        
        # Update UI
        self.wizard.set_executing(True)
        self.progress_page.set_status("Converting", COLORS["accent"])
        self.progress_page.set_cancel_enabled(True)
        self.progress_page.clear_progress()
        self.progress_page.clear_log()
        
        # Start conversion in separate thread
        self.conversion_thread = threading.Thread(
            target=self._run_conversion,
            args=(config,),
            daemon=True
        )
        self.conversion_thread.start()
    
    def _start_watch_from_config(self, config: ConversionConfig):
        """Start watch mode using wizard config."""
        # This will be called from navigation if watch mode button is clicked
        # For now, we'll implement it separately
        pass
    
    def _cancel_conversion(self):
        """Cancel the conversion process."""
        self.cancel_requested = True
        self.progress_page.set_status("Cancelling...", COLORS["warning"])
        self.progress_page.log_message("Conversion cancelled by user.")
    
    def _toggle_watch_mode(self):
        """Toggle watch mode on/off."""
        if self.is_watching:
            self._stop_watch_mode()
        else:
            self._start_watch_mode()
    
    def _start_watch_mode(self):
        """Start watch mode."""
        config = self.wizard.config
        
        if not config.output_dir:
            messagebox.showwarning("No Output", "Please select an output directory.")
            return
        
        # Use first input as watch directory, or ask user
        if config.input_items:
            watch_dir = config.input_items[0]
            if watch_dir.is_file():
                watch_dir = watch_dir.parent
        else:
            from tkinter import filedialog
            watch_dir = filedialog.askdirectory(title="Select Directory to Watch")
            if not watch_dir:
                return
            watch_dir = Path(watch_dir)
        
        if not watch_dir.exists():
            messagebox.showerror("Invalid Directory", f"Watch directory does not exist: {watch_dir}")
            return
        
        # Initialize network mover if enabled (same logic as conversion)
        watch_network_mover = None
        if config.enable_network_move and config.network_path:
            try:
                network_path = Path(config.network_path)
                overwrite_behavior = OverwriteBehavior(config.overwrite_mode)
                delete_after_move = config.cleanup.delete_after_network_move
                keep_local = config.keep_local_copy and not delete_after_move
                
                watch_network_mover = NetworkMover(
                    network_root=network_path,
                    keep_local=keep_local,
                    overwrite_behavior=overwrite_behavior,
                    max_retries=config.retries,
                    retry_delay=2.0
                )
                
                def network_status_callback(message: str):
                    self.update_queue.put(("log", f"[Network] {message}"))
                
                watch_network_mover.set_status_callback(network_status_callback)
            except Exception as e:
                self.update_queue.put(("log", f"Warning: Failed to initialize network mover: {e}"))
        
        # Create watch mode callback
        def watch_conversion_callback(input_file: Path, output_dir: Path):
            """Callback for watch mode conversions."""
            try:
                use_metadata = True
                watch_engine = ConversionEngine(
                    use_metadata_naming=use_metadata,
                    max_concurrent=config.max_concurrent
                )
                watch_zip_handler = ZipHandler()
                
                def progress_callback(file_path: Path, status: ConversionStatus, message: str):
                    if not self.cancel_requested:
                        self.update_queue.put(("progress", file_path, status, message))
                        self.update_queue.put(("log", f"[Watch] {file_path.name}: {message}"))
                
                watch_engine.set_progress_callback(progress_callback)
                
                is_zip = watch_zip_handler.is_zip_file(input_file)
                
                if is_zip:
                    self.update_queue.put(("log", f"[Watch] Processing ZIP: {input_file.name}"))
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
                            keep_iso=config.cleanup.keep_iso,
                            verbose=False
                        )
                        zip_results.append(result)
                        
                        if watch_network_mover and result.status == ConversionStatus.SUCCESS and result.output_file:
                            self.update_queue.put(("log", f"[Watch] Moving {result.output_file.name} to network..."))
                            move_result = watch_network_mover.move_file(result.output_file, output_dir)
                            if move_result.success:
                                self.update_queue.put(("log", f"[Watch] Successfully moved {result.output_file.name} to network"))
                                if config.cleanup.delete_after_network_move:
                                    try:
                                        result.output_file.unlink()
                                        self.update_queue.put(("log", f"[Watch] Deleted local WBFS file: {result.output_file.name}"))
                                    except Exception as e:
                                        self.update_queue.put(("log", f"[Watch] Warning: Could not delete local WBFS file {result.output_file.name}: {e}"))
                    
                    if not config.cleanup.keep_extracted:
                        watch_zip_handler.cleanup_extraction(extract_dir)
                    
                    should_delete_zip = not watch_network_mover or config.cleanup.delete_zip or (config.cleanup.delete_after_network_move and watch_network_mover)
                    if should_delete_zip:
                        all_succeeded = all(r.status == ConversionStatus.SUCCESS for r in zip_results)
                        if all_succeeded:
                            try:
                                input_file.unlink()
                                self.update_queue.put(("log", f"[Watch] Deleted ZIP: {input_file.name}"))
                            except Exception as e:
                                self.update_queue.put(("log", f"[Watch] Warning: Could not delete ZIP {input_file.name}: {e}"))
                else:
                    output_wbfs = output_dir / (input_file.stem + ".wbfs")
                    result = watch_engine.convert_file(
                        input_file,
                        output_wbfs,
                        keep_iso=config.cleanup.keep_iso,
                        verbose=False
                    )
                    
                    if result.status == ConversionStatus.SUCCESS:
                        self.update_queue.put(("log", f"[Watch] Successfully converted: {input_file.name}"))
                        
                        if watch_network_mover and result.output_file:
                            self.update_queue.put(("log", f"[Watch] Moving {result.output_file.name} to network..."))
                            move_result = watch_network_mover.move_file(result.output_file, output_dir)
                            if move_result.success:
                                self.update_queue.put(("log", f"[Watch] Successfully moved {result.output_file.name} to network"))
                                if config.cleanup.delete_after_network_move:
                                    try:
                                        result.output_file.unlink()
                                        self.update_queue.put(("log", f"[Watch] Deleted local WBFS file: {result.output_file.name}"))
                                    except Exception as e:
                                        self.update_queue.put(("log", f"[Watch] Warning: Could not delete local WBFS file {result.output_file.name}: {e}"))
            
            except Exception as e:
                self.update_queue.put(("log", f"[Watch] ERROR: Failed to process {input_file.name}: {e}"))
        
        self.watch_mode = WatchMode(
            watch_dir=watch_dir,
            output_dir=config.output_dir,
            conversion_callback=watch_conversion_callback,
            check_interval=5.0,
            file_stable_time=10.0
        )
        
        def status_callback(message: str):
            self.update_queue.put(("log", f"[Watch] {message}"))
        
        self.watch_mode.set_status_callback(status_callback)
        
        try:
            self.watch_mode.start()
            self.is_watching = True
            self.progress_page.set_status("Watching", COLORS["success"])
            self.progress_page.set_watch_text("▣ Stop Watch Mode", active=True)
            self.progress_page.log_message(f"Watch mode started. Monitoring: {watch_dir}")
        except Exception as e:
            messagebox.showerror("Watch Mode Error", f"Failed to start watch mode: {e}")
    
    def _stop_watch_mode(self):
        """Stop watch mode."""
        if self.watch_mode:
            self.watch_mode.stop()
            self.is_watching = False
            self.progress_page.set_status("Idle")
            self.progress_page.set_watch_text("▢ Start Watch Mode", active=False)
            self.progress_page.log_message("Watch mode stopped")
    
    def _run_conversion(self, config: ConversionConfig):
        """Run conversion in background thread."""
        try:
            engine = ConversionEngine(
                use_metadata_naming=True,
                max_concurrent=config.max_concurrent
            )
            
            def progress_callback(file_path: Path, status: ConversionStatus, message: str):
                if self.cancel_requested:
                    return
                self.update_queue.put(("progress", file_path, status, message))
            
            engine.set_progress_callback(progress_callback)
            
            all_results = []
            
            # Process each input (same logic as original)
            for input_path in config.input_items:
                if self.cancel_requested:
                    break
                
                self.update_queue.put(("log", f"Processing: {input_path}"))
                
                is_zip = self.zip_handler.is_zip_file(input_path) if input_path.is_file() else False
                
                if is_zip:
                    self.update_queue.put(("log", f"Detected ZIP file: {input_path}"))
                    try:
                        extracted_rvz, extract_dir = self.zip_handler.extract_rvz_from_zip(input_path)
                        self.update_queue.put(("log", f"Extracted {len(extracted_rvz)} RVZ file(s) from ZIP"))
                        
                        for rvz_file in extracted_rvz:
                            if self.cancel_requested:
                                break
                            
                            if len(extracted_rvz) == 1:
                                output_wbfs = config.output_dir / (input_path.stem + ".wbfs")
                            else:
                                output_wbfs = config.output_dir / (rvz_file.stem + ".wbfs")
                            
                            result = engine.convert_file(
                                rvz_file,
                                output_wbfs,
                                keep_iso=config.cleanup.keep_iso,
                                verbose=False
                            )
                            all_results.append(result)
                            
                            if self.network_mover and result.status == ConversionStatus.SUCCESS and result.output_file:
                                move_result = self.network_mover.move_file(result.output_file, config.output_dir)
                                if move_result.success:
                                    self.update_queue.put(("log", f"Successfully moved {result.output_file.name} to network"))
                                    if config.cleanup.delete_after_network_move:
                                        try:
                                            result.output_file.unlink()
                                            self.update_queue.put(("log", f"Deleted local WBFS file: {result.output_file.name}"))
                                        except Exception as e:
                                            self.update_queue.put(("log", f"Warning: Could not delete local WBFS file {result.output_file.name}: {e}"))
                                elif not move_result.skipped:
                                    self.update_queue.put(("log", f"Failed to move {result.output_file.name} to network: {move_result.error_message}"))
                                else:
                                    self.update_queue.put(("log", f"Skipped moving {result.output_file.name} to network (file exists)"))
                        
                        if not config.cleanup.keep_extracted:
                            self.zip_handler.cleanup_extraction(extract_dir)
                            self.update_queue.put(("log", "Cleaned up extracted files"))
                        
                        should_delete_zip = not self.network_mover or config.cleanup.delete_zip or (config.cleanup.delete_after_network_move and self.network_mover)
                        if should_delete_zip:
                            zip_results = all_results[-len(extracted_rvz):] if len(extracted_rvz) > 0 else []
                            all_succeeded = all(r.status == ConversionStatus.SUCCESS for r in zip_results) if zip_results else False
                            if all_succeeded:
                                try:
                                    input_path.unlink()
                                    self.update_queue.put(("log", f"Deleted original ZIP file: {input_path.name}"))
                                except Exception as e:
                                    self.update_queue.put(("log", f"Warning: Could not delete ZIP file {input_path.name}: {e}"))
                            else:
                                self.update_queue.put(("log", f"Not deleting ZIP file due to conversion failures: {input_path.name}"))
                    
                    except Exception as e:
                        self.update_queue.put(("log", f"ERROR: Failed to process ZIP {input_path}: {e}"))
                        all_results.append(ConversionResult(
                            input_file=input_path,
                            output_file=None,
                            status=ConversionStatus.FAILED,
                            error_message=f"ZIP extraction failed: {str(e)}"
                        ))
                
                elif input_path.is_file():
                    output_wbfs = config.output_dir / (input_path.stem + ".wbfs")
                    result = engine.convert_file(
                        input_path,
                        output_wbfs,
                        keep_iso=config.cleanup.keep_iso,
                        verbose=False
                    )
                    all_results.append(result)
                else:
                    # Directory processing (same as original)
                    zip_files = self.zip_handler.find_zip_files(input_path)
                    for zip_file in zip_files:
                        if self.cancel_requested:
                            break
                        
                        self.update_queue.put(("log", f"Processing ZIP file: {zip_file.name}"))
                        try:
                            extracted_rvz, extract_dir = self.zip_handler.extract_rvz_from_zip(zip_file)
                            self.update_queue.put(("log", f"Extracted {len(extracted_rvz)} RVZ file(s) from ZIP"))
                            
                            zip_results = []
                            for rvz_file in extracted_rvz:
                                if self.cancel_requested:
                                    break
                                
                                if config.cleanup.preserve_structure:
                                    output_wbfs = config.output_dir / (rvz_file.stem + ".wbfs")
                                else:
                                    output_wbfs = config.output_dir / (rvz_file.stem + ".wbfs")
                                
                                result = engine.convert_file(
                                    rvz_file,
                                    output_wbfs,
                                    keep_iso=config.cleanup.keep_iso,
                                    verbose=False
                                )
                                zip_results.append(result)
                                all_results.append(result)
                            
                            if not config.cleanup.keep_extracted:
                                self.zip_handler.cleanup_extraction(extract_dir)
                                self.update_queue.put(("log", "Cleaned up extracted files"))
                            
                            should_delete_zip = not self.network_mover or config.cleanup.delete_zip or (config.cleanup.delete_after_network_move and self.network_mover)
                            if should_delete_zip:
                                all_succeeded = all(r.status == ConversionStatus.SUCCESS for r in zip_results)
                                if all_succeeded:
                                    try:
                                        zip_file.unlink()
                                        self.update_queue.put(("log", f"Deleted original ZIP file: {zip_file.name}"))
                                    except Exception as e:
                                        self.update_queue.put(("log", f"Warning: Could not delete ZIP file {zip_file.name}: {e}"))
                                else:
                                    self.update_queue.put(("log", f"Not deleting ZIP file due to conversion failures: {zip_file.name}"))
                        
                        except Exception as e:
                            self.update_queue.put(("log", f"ERROR: Failed to process ZIP {zip_file.name}: {e}"))
                            all_results.append(ConversionResult(
                                input_file=zip_file,
                                output_file=None,
                                status=ConversionStatus.FAILED,
                                error_message=f"ZIP processing failed: {str(e)}"
                            ))
                    
                    rvz_files = list(input_path.rglob("*.rvz"))
                    rvz_files.extend(input_path.rglob("*.RVZ"))
                    
                    extract_base = self.zip_handler.extract_dir
                    rvz_files = [f for f in rvz_files if extract_base not in f.parents]
                    
                    if rvz_files:
                        self.update_queue.put(("log", f"Found {len(rvz_files)} regular RVZ file(s) to convert"))
                        for rvz_file in rvz_files:
                            if self.cancel_requested:
                                break
                            
                            if config.cleanup.preserve_structure:
                                try:
                                    rel_path = rvz_file.relative_to(input_path)
                                    output_wbfs = config.output_dir / rel_path.with_suffix(".wbfs")
                                except ValueError:
                                    output_wbfs = config.output_dir / (rvz_file.stem + ".wbfs")
                            else:
                                output_wbfs = config.output_dir / (rvz_file.stem + ".wbfs")
                            
                            result = engine.convert_file(
                                rvz_file,
                                output_wbfs,
                                keep_iso=config.cleanup.keep_iso,
                                verbose=False
                            )
                            all_results.append(result)
                            
                            if self.network_mover and result.status == ConversionStatus.SUCCESS and result.output_file:
                                move_result = self.network_mover.move_file(result.output_file, config.output_dir)
                                if move_result.success:
                                    self.update_queue.put(("log", f"Successfully moved {result.output_file.name} to network"))
                                    if config.cleanup.delete_after_network_move:
                                        try:
                                            result.output_file.unlink()
                                            self.update_queue.put(("log", f"Deleted local WBFS file: {result.output_file.name}"))
                                        except Exception as e:
                                            self.update_queue.put(("log", f"Warning: Could not delete local WBFS file {result.output_file.name}: {e}"))
                                elif not move_result.skipped:
                                    self.update_queue.put(("log", f"Failed to move {result.output_file.name} to network: {move_result.error_message}"))
                                else:
                                    self.update_queue.put(("log", f"Skipped moving {result.output_file.name} to network (file exists)"))
                    
                    if not all_results:
                        self.update_queue.put(("log", f"WARNING: No RVZ files found in {input_path}"))
                        all_results.append(ConversionResult(
                            input_file=input_path,
                            output_file=None,
                            status=ConversionStatus.FAILED,
                            error_message="No RVZ files found (including in ZIP archives)"
                        ))
            
            # Final summary
            if not self.cancel_requested:
                self.update_queue.put(("summary", all_results))
        
        except Exception as e:
            self.update_queue.put(("error", str(e)))
        finally:
            self.update_queue.put(("done",))
    
    def _process_queue(self):
        """Process UI update queue (thread-safe)."""
        try:
            while True:
                try:
                    item = self.update_queue.get_nowait()
                    self._handle_queue_item(item)
                except queue.Empty:
                    break
        except Exception as e:
            self.logger.error(f"Error processing queue: {e}")
        
        # Schedule next check
        self.root.after(100, self._process_queue)
    
    def _handle_queue_item(self, item):
        """Handle a queue item."""
        item_type = item[0]
        
        if item_type == "tool_download":
            _, message = item
            if message == "success":
                messagebox.showinfo("Tools Downloaded", "All required tools have been downloaded successfully!")
            elif message.startswith("failed:"):
                missing = message.split(":")[1]
                messagebox.showerror(
                    "Download Failed",
                    f"Failed to download: {missing}\n\n"
                    "Please download the tools manually from:\n"
                    "• Dolphin: https://dolphin-emu.org/download/\n"
                    "• WIT: https://wit.wiimm.de/\n\n"
                    "The application will check for tools on next launch."
                )
            else:
                # Progress message - could show in status bar if we had one
                self.logger.info(f"Tool download: {message}")
        
        elif item_type == "progress":
            _, file_path, status, message = item
            self.progress_page.update_progress(file_path, status, message)
        
        elif item_type == "log":
            _, message = item
            self.progress_page.log_message(message)
        
        elif item_type == "summary":
            _, results = item
            self._show_summary(results)
        
        elif item_type == "error":
            _, error = item
            self.progress_page.log_message(f"ERROR: {error}")
            messagebox.showerror("Conversion Error", f"An error occurred:\n{error}")
        
        elif item_type == "done":
            self.is_converting = False
            self.wizard.set_executing(False)
            self.progress_page.set_status("Idle")
            self.progress_page.set_cancel_enabled(False)
            self.nav.set_next_text("Next")
            self.nav.set_back_enabled(True)
    
    def _show_summary(self, results):
        """Show conversion summary."""
        total = len(results)
        success = sum(1 for r in results if r.status == ConversionStatus.SUCCESS)
        failed = sum(1 for r in results if r.status == ConversionStatus.FAILED)
        skipped = sum(1 for r in results if r.status == ConversionStatus.SKIPPED)
        
        summary = f"\n{'='*60}\n"
        summary += "CONVERSION SUMMARY\n"
        summary += f"{'='*60}\n"
        summary += f"Total files: {total}\n"
        summary += f"Successful: {success}\n"
        summary += f"Failed: {failed}\n"
        summary += f"Skipped: {skipped}\n"
        summary += f"{'='*60}\n"
        
        if failed > 0:
            summary += "\nFailed conversions:\n"
            for result in results:
                if result.status == ConversionStatus.FAILED:
                    summary += f"  - {result.input_file}\n"
                    if result.error_message:
                        summary += f"    Error: {result.error_message}\n"
        
        self.progress_page.log_message(summary)
        
        # Show message box
        if failed == 0:
            messagebox.showinfo("Conversion Complete", f"Successfully converted {success} file(s).")
        else:
            messagebox.showwarning(
                "Conversion Complete",
                f"Conversion finished with {failed} error(s).\n\nSee log for details."
            )


def main():
    """Main UI entry point."""
    root = ctk.CTk()
    app = ConversionUI(root)
    
    # Handle window close - stop watch mode if running
    def on_closing():
        if app.is_watching and app.watch_mode:
            app._stop_watch_mode()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()

