"""
Tool Downloader Module
Automatically downloads Dolphin and WIT tools if they are missing.
"""

import os
import sys
import zipfile
import shutil
import logging
import subprocess
from pathlib import Path
from typing import Optional, Tuple
import urllib.request
import urllib.error
from io import BytesIO

# Set up logger
logger = logging.getLogger(__name__)

# Official download URLs
# Note: These URLs may need to be updated periodically
# WIT download URLs (Wiimms ISO Toolset) - Direct download links
# Verified working URL (r8638 returns valid 14.8MB zip, r8427 returns HTML error page)
WIT_WINDOWS_URL = "https://wit.wiimm.de/download/wit-v3.05a-r8638-cygwin64.zip"
WIT_LINUX_URL = "https://wit.wiimm.de/download/wit-v3.05a-r8427-x86_64.tar.gz"
WIT_MACOS_URL = "https://wit.wiimm.de/download/wit-v3.05a-r8427-x86_64.tar.gz"

# Dolphin download URLs
# Using stable release URL (verified working - 16.4MB 7z archive)
# Format: https://dl.dolphin-emu.org/releases/{version}/dolphin-{version}-x64.7z
DOLPHIN_WINDOWS_URL = "https://dl.dolphin-emu.org/releases/2506a/dolphin-2506a-x64.7z"
DOLPHIN_DOWNLOAD_PAGE = "https://dolphin-emu.org/download/"


class ToolDownloader:
    """
    Handles automatic downloading of Dolphin and WIT tools.
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize the tool downloader.
        
        Args:
            project_root: Root directory of the project. If None, auto-detects.
        """
        if project_root is None:
            # Auto-detect project root
            # If running as executable (PyInstaller), use sys.executable's directory
            # Otherwise, use parent of src/
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                project_root = Path(sys.executable).parent
            else:
                # Running as script
                project_root = Path(__file__).parent.parent
        
        self.project_root = Path(project_root).resolve()
        self.tools_dir = self.project_root / "tools"
        self.dolphin_dir = self.tools_dir / "dolphin"
        self.wit_dir = self.tools_dir / "wit"
        
        # Create tools directory if it doesn't exist
        self.tools_dir.mkdir(exist_ok=True)
        self.dolphin_dir.mkdir(exist_ok=True)
        self.wit_dir.mkdir(exist_ok=True)
        
        # Set up file logger for tool downloads
        self._setup_file_logger()
    
    def _setup_file_logger(self):
        """Set up file logging for tool downloads."""
        log_file = self.project_root / "tool_download.log"
        
        # Remove existing handlers to avoid duplicates
        logger.handlers = [h for h in logger.handlers if not isinstance(h, logging.FileHandler)]
        
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.setLevel(logging.DEBUG)
        
        # Also add console handler for immediate feedback
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
            logger.addHandler(console_handler)
        
        logger.info("=" * 60)
        logger.info("Tool Downloader initialized")
        logger.info(f"Log file: {log_file}")
        logger.info(f"Project root: {self.project_root}")
        logger.info(f"Tools directory: {self.tools_dir}")
    
    def check_dolphin_tool(self) -> bool:
        """Check if Dolphin tool exists."""
        if sys.platform == "win32":
            tool_path = self.dolphin_dir / "DolphinTool.exe"
        else:
            tool_path = self.dolphin_dir / "dolphin-tool"
        
        return tool_path.exists() and tool_path.is_file()
    
    def check_wit(self) -> bool:
        """Check if WIT tool exists."""
        if sys.platform == "win32":
            tool_path = self.wit_dir / "wit.exe"
        else:
            tool_path = self.wit_dir / "wit"
        
        return tool_path.exists() and tool_path.is_file()
    
    def _download_file(self, url: str, save_path: Path, progress_callback=None) -> bool:
        """
        Download a file from URL with logging.
        
        Args:
            url: URL to download from
            save_path: Path to save the file
            progress_callback: Optional callback function(status_message)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Starting download: {url}")
            logger.info(f"Save path: {save_path}")
            
            if progress_callback:
                progress_callback(f"Downloading from {url}...")
            
            # Create parent directory if needed
            save_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {save_path.parent}")
            
            # Download with progress
            last_percent = -1
            def reporthook(blocknum, blocksize, totalsize):
                nonlocal last_percent
                if totalsize > 0:
                    percent = min(100, (blocknum * blocksize * 100) // totalsize)
                    # Only update every 5% to avoid spam
                    if percent >= last_percent + 5 or percent == 100:
                        last_percent = percent
                        if progress_callback:
                            progress_callback(f"Downloading... {percent}%")
            
            logger.info("Starting URL retrieval...")
            urllib.request.urlretrieve(url, save_path, reporthook)
            logger.info("URL retrieval completed")
            
            # Verify file was downloaded
            if not save_path.exists():
                error_msg = "Downloaded file does not exist"
                logger.error(error_msg)
                if progress_callback:
                    progress_callback(f"Error: {error_msg}")
                return False
            
            file_size = save_path.stat().st_size
            logger.info(f"Downloaded file size: {file_size} bytes ({file_size / (1024 * 1024):.2f} MB)")
            
            if file_size == 0:
                error_msg = "Downloaded file is empty"
                logger.error(error_msg)
                if progress_callback:
                    progress_callback(f"Error: {error_msg}")
                save_path.unlink(missing_ok=True)
                return False
            
            # Check if file is suspiciously small (likely an HTML error page)
            # WIT zip should be at least 1MB
            if file_size < 100000:  # Less than 100KB is suspicious
                logger.warning(f"Downloaded file is very small ({file_size} bytes), checking if it's an error page")
                # Check if it's HTML
                try:
                    with open(save_path, 'rb') as f:
                        first_bytes = f.read(512)
                        content_str = first_bytes.decode('utf-8', errors='ignore').lower()
                        if '<html' in content_str or '<!doctype' in content_str or '<body' in content_str or 'error' in content_str[:100] or 'title' in content_str[:100]:
                            error_msg = f"Downloaded file appears to be an HTML error page (not a ZIP file). File size: {file_size} bytes. The download URL may be incorrect or the file may no longer be available."
                            logger.error(error_msg)
                            logger.error(f"File content preview: {content_str[:200]}")
                            if progress_callback:
                                progress_callback(f"Error: {error_msg}")
                            save_path.unlink(missing_ok=True)
                            return False
                        else:
                            # File is small but not obviously HTML - still suspicious
                            logger.warning(f"Downloaded file is very small ({file_size} bytes) but doesn't appear to be HTML. Proceeding with caution.")
                except Exception as e:
                    logger.warning(f"Could not verify file type: {e}")
            
            if progress_callback:
                file_size_mb = file_size / (1024 * 1024)
                progress_callback(f"Download complete! ({file_size_mb:.1f} MB)")
            
            logger.info("Download completed successfully")
            return True
        except urllib.error.URLError as e:
            error_msg = f"Download failed (URLError): {str(e)}"
            logger.error(error_msg, exc_info=True)
            if progress_callback:
                progress_callback(error_msg)
            return False
        except Exception as e:
            error_msg = f"Download error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            if progress_callback:
                progress_callback(error_msg)
            return False
    
    def _extract_zip(self, zip_path: Path, extract_to: Path, progress_callback=None) -> bool:
        """Extract a ZIP file with logging."""
        """
        Extract a ZIP file.
        
        Args:
            zip_path: Path to ZIP file
            extract_to: Directory to extract to
            progress_callback: Optional callback function(status_message)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Starting extraction: {zip_path} -> {extract_to}")
            
            if progress_callback:
                progress_callback(f"Extracting {zip_path.name}...")
            
            # Verify ZIP file exists and is readable
            if not zip_path.exists():
                error_msg = f"ZIP file not found: {zip_path}"
                logger.error(error_msg)
                if progress_callback:
                    progress_callback(f"Error: {error_msg}")
                return False
            
            extract_to.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created extraction directory: {extract_to}")
            
            # Test if it's a valid ZIP file
            try:
                logger.debug("Opening ZIP file...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    file_list = zip_ref.namelist()
                    logger.info(f"ZIP contains {len(file_list)} files")
                    logger.debug(f"Files in ZIP: {file_list[:10]}...")  # Log first 10 files
                    
                    if progress_callback:
                        progress_callback(f"Extracting {len(file_list)} files...")
                    
                    logger.debug("Extracting files...")
                    zip_ref.extractall(extract_to)
                    logger.info("Extraction completed")
            except zipfile.BadZipFile as e:
                error_msg = f"Invalid or corrupted ZIP file: {zip_path}"
                logger.error(error_msg, exc_info=True)
                if progress_callback:
                    progress_callback(f"Error: {error_msg}")
                return False
            
            if progress_callback:
                progress_callback("Extraction complete!")
            
            return True
        except Exception as e:
            error_msg = f"Extraction error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            if progress_callback:
                progress_callback(error_msg)
            return False
    
    def _extract_7z(self, archive_path: Path, extract_to: Path, progress_callback=None) -> bool:
        """
        Extract a 7z archive using 7z.exe (Windows) or 7z command (Linux/macOS).
        
        Args:
            archive_path: Path to 7z archive
            extract_to: Directory to extract to
            progress_callback: Optional callback function(status_message)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Starting 7z extraction: {archive_path} -> {extract_to}")
            
            if progress_callback:
                progress_callback(f"Extracting {archive_path.name}...")
            
            if not archive_path.exists():
                error_msg = f"7z archive not found: {archive_path}"
                logger.error(error_msg)
                if progress_callback:
                    progress_callback(f"Error: {error_msg}")
                return False
            
            extract_to.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created extraction directory: {extract_to}")
            
            # Use 7z.exe on Windows, 7z command on Linux/macOS
            if sys.platform == "win32":
                # Try common 7z.exe locations
                seven_zip_paths = [
                    Path("C:/Program Files/7-Zip/7z.exe"),
                    Path("C:/Program Files (x86)/7-Zip/7z.exe"),
                    Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "7-Zip" / "7z.exe",
                ]
                
                # Also try if 7z is in PATH
                seven_zip = shutil.which("7z") or shutil.which("7z.exe")
                if seven_zip:
                    seven_zip_paths.insert(0, Path(seven_zip))
                
                seven_zip_exe = None
                for path in seven_zip_paths:
                    if path.exists():
                        seven_zip_exe = path
                        break
                
                if not seven_zip_exe:
                    error_msg = (
                        "7z.exe not found. Please install 7-Zip from https://www.7-zip.org/\n"
                        "or ensure 7z.exe is in your PATH."
                    )
                    logger.error(error_msg)
                    if progress_callback:
                        progress_callback(f"Error: {error_msg}")
                    return False
                
                logger.info(f"Using 7z.exe: {seven_zip_exe}")
                cmd = [str(seven_zip_exe), "x", str(archive_path), f"-o{extract_to}", "-y"]
            else:
                # Linux/macOS - use 7z command
                cmd = ["7z", "x", str(archive_path), f"-o{extract_to}", "-y"]
            
            logger.debug(f"Running command: {' '.join(cmd)}")
            
            if progress_callback:
                progress_callback("Extracting archive...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                error_msg = f"7z extraction failed: {result.stderr}"
                logger.error(error_msg)
                logger.error(f"7z stdout: {result.stdout}")
                if progress_callback:
                    progress_callback(f"Error: {error_msg}")
                return False
            
            logger.info("7z extraction completed successfully")
            if progress_callback:
                progress_callback("Extraction complete!")
            
            return True
            
        except subprocess.TimeoutExpired:
            error_msg = "7z extraction timed out (exceeded 5 minutes)"
            logger.error(error_msg)
            if progress_callback:
                progress_callback(f"Error: {error_msg}")
            return False
        except FileNotFoundError:
            error_msg = "7z command not found. Please install 7-Zip (Windows) or p7zip (Linux/macOS)"
            logger.error(error_msg)
            if progress_callback:
                progress_callback(f"Error: {error_msg}")
            return False
        except Exception as e:
            error_msg = f"7z extraction error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            if progress_callback:
                progress_callback(error_msg)
            return False
    
    def _find_dolphin_tool_in_extracted(self, extract_dir: Path) -> Optional[Path]:
        """Find DolphinTool.exe or dolphin-tool in extracted directory."""
        if sys.platform == "win32":
            # Look for DolphinTool.exe
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file == "DolphinTool.exe":
                        return Path(root) / file
        else:
            # Look for dolphin-tool
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file == "dolphin-tool" or (file.startswith("dolphin") and "tool" in file.lower()):
                        full_path = Path(root) / file
                        # Make executable
                        os.chmod(full_path, 0o755)
                        return full_path
        return None
    
    def _find_wit_in_extracted(self, extract_dir: Path) -> Optional[Path]:
        """Find wit.exe or wit in extracted directory."""
        if sys.platform == "win32":
            # Look for wit.exe
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file == "wit.exe":
                        return Path(root) / file
        else:
            # Look for wit executable
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file == "wit" and os.access(Path(root) / file, os.X_OK):
                        return Path(root) / file
        return None
    
    def download_dolphin(self, progress_callback=None) -> Tuple[bool, str]:
        """
        Download and extract Dolphin tool.
        
        Args:
            progress_callback: Optional callback function(status_message)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        logger.info("=" * 60)
        logger.info("Starting Dolphin download process")
        
        if self.check_dolphin_tool():
            logger.info("Dolphin tool already exists, skipping download")
            return True, "Dolphin tool already exists"
        
        try:
            if progress_callback:
                progress_callback("Downloading Dolphin tool...")
            
            if sys.platform == "win32":
                download_url = DOLPHIN_WINDOWS_URL
                archive_name = "dolphin.7z"
                logger.info(f"Platform: Windows, using URL: {download_url}")
            else:
                message = (
                    "Dolphin tool not found. Please download Dolphin from:\n"
                    "https://dolphin-emu.org/download/\n\n"
                    f"Extract dolphin-tool to: {self.dolphin_dir}\n"
                    "Make sure it's executable: chmod +x tools/dolphin/dolphin-tool"
                )
                if progress_callback:
                    progress_callback(message)
                return False, message
            
            temp_archive = self.tools_dir / archive_name
            logger.info(f"Download target: {temp_archive}")
            
            if not self._download_file(download_url, temp_archive, progress_callback):
                error_msg = (
                    f"Failed to download Dolphin tool from {download_url}\n\n"
                    "Possible reasons:\n"
                    "- The download URL may be incorrect or outdated\n"
                    "- Network connection issues\n\n"
                    "Please download Dolphin manually from:\n"
                    "https://dolphin-emu.org/download/\n\n"
                    f"Extract DolphinTool.exe to: {self.dolphin_dir}"
                )
                logger.error(error_msg)
                return False, error_msg
            
            # Extract 7z archive
            temp_extract = self.tools_dir / "dolphin_temp"
            if temp_extract.exists():
                logger.debug(f"Removing existing temp directory: {temp_extract}")
                shutil.rmtree(temp_extract)
            
            temp_extract.mkdir(parents=True, exist_ok=True)
            logger.info(f"Extracting to: {temp_extract}")
            
            if not self._extract_7z(temp_archive, temp_extract, progress_callback):
                error_msg = "Failed to extract Dolphin archive"
                logger.error(error_msg)
                if progress_callback:
                    progress_callback(f"Error: {error_msg}")
                return False, error_msg
            
            # Find DolphinTool.exe in extracted files
            dolphin_tool = self._find_dolphin_tool_in_extracted(temp_extract)
            if not dolphin_tool:
                error_msg = (
                    f"Could not find DolphinTool.exe in extracted archive.\n"
                    f"Searched in: {temp_extract}\n\n"
                    "Please download Dolphin manually from:\n"
                    "https://dolphin-emu.org/download/\n\n"
                    f"Extract DolphinTool.exe to: {self.dolphin_dir}"
                )
                logger.error(error_msg)
                if progress_callback:
                    progress_callback(f"Error: {error_msg}")
                return False, error_msg
            
            # Copy DolphinTool.exe to tools/dolphin/
            target_path = self.dolphin_dir / "DolphinTool.exe"
            logger.info(f"Copying {dolphin_tool} to {target_path}")
            if progress_callback:
                progress_callback("Installing Dolphin tool...")
            
            shutil.copy2(dolphin_tool, target_path)
            logger.info(f"Dolphin tool installed to: {target_path}")
            
            # Cleanup
            logger.debug("Cleaning up temporary files...")
            temp_archive.unlink(missing_ok=True)
            shutil.rmtree(temp_extract, ignore_errors=True)
            
            if progress_callback:
                progress_callback("Dolphin tool installed successfully!")
            
            logger.info("Dolphin download and installation completed successfully")
            return True, "Dolphin tool downloaded and installed successfully"
            
        except Exception as e:
            error_msg = f"An unexpected error occurred during Dolphin download: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    def download_wit(self, progress_callback=None) -> Tuple[bool, str]:
        """
        Download and extract WIT tool.
        
        Args:
            progress_callback: Optional callback function(status_message)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        logger.info("=" * 60)
        logger.info("Starting WIT download process")
        
        if self.check_wit():
            logger.info("WIT tool already exists, skipping download")
            return True, "WIT tool already exists"
        
        try:
            if progress_callback:
                progress_callback("Downloading WIT tool...")
            
            # Download URL based on platform
            if sys.platform == "win32":
                download_url = WIT_WINDOWS_URL
                zip_name = "wit.zip"
                logger.info(f"Platform: Windows, using URL: {download_url}")
            else:
                # For Linux/macOS, we'd need to handle .tar.gz
                # For now, provide instructions
                message = (
                    "WIT tool not found. Please download WIT from:\n"
                    "https://wit.wiimm.de/\n\n"
                    f"Extract the 'wit' executable to: {self.wit_dir}\n"
                    "Make sure it's executable: chmod +x tools/wit/wit"
                )
                if progress_callback:
                    progress_callback(message)
                return False, message
            
            # Download to temp location
            temp_zip = self.tools_dir / zip_name
            logger.info(f"Download target: {temp_zip}")
            
            if not self._download_file(download_url, temp_zip, progress_callback):
                error_msg = (
                    f"Failed to download WIT tool from {download_url}\n\n"
                    "Possible reasons:\n"
                    "- The download URL may be incorrect or outdated\n"
                    "- The server may be returning an error page instead of the file\n"
                    "- Network connection issues\n\n"
                    "Please download WIT manually from:\n"
                    "https://wit.wiimm.de/\n\n"
                    f"Extract wit.exe to: {self.wit_dir}"
                )
                logger.error(error_msg)
                return False, error_msg
            
            # Verify download completed
            if not temp_zip.exists():
                error_msg = "Downloaded ZIP file not found"
                logger.error(error_msg)
                return False, error_msg
            
            file_size = temp_zip.stat().st_size
            logger.info(f"Downloaded file size: {file_size} bytes ({file_size / (1024*1024):.2f} MB)")
            
            if file_size == 0:
                error_msg = "Downloaded file is empty - download may have failed"
                logger.error(error_msg)
                temp_zip.unlink(missing_ok=True)
                return False, error_msg
            
            # Check if file is suspiciously small (likely HTML error page)
            # WIT zip should be at least 1MB
            if file_size < 100000:  # Less than 100KB is suspicious
                logger.warning(f"Downloaded file is suspiciously small: {file_size} bytes (expected >1MB for WIT zip)")
                # Check if it's HTML
                try:
                    with open(temp_zip, 'rb') as f:
                        first_bytes = f.read(512)
                        content_str = first_bytes.decode('utf-8', errors='ignore').lower()
                        if '<html' in content_str or '<!doctype' in content_str or '<body' in content_str or 'error' in content_str[:100]:
                            error_msg = (
                                f"Downloaded file appears to be an HTML error page (not a ZIP file).\n"
                                f"File size: {file_size} bytes (expected >1MB).\n\n"
                                "The download URL may be incorrect, outdated, or the server may be returning an error page.\n\n"
                                "Please download WIT manually from:\n"
                                "https://wit.wiimm.de/\n\n"
                                f"Extract wit.exe to: {self.wit_dir}"
                            )
                            logger.error(error_msg)
                            logger.error(f"File content preview: {content_str[:200]}")
                            temp_zip.unlink(missing_ok=True)
                            return False, error_msg
                except Exception as e:
                    logger.warning(f"Could not verify file type: {e}")
            
            # Extract to temp directory first
            temp_extract = self.tools_dir / "wit_temp"
            if temp_extract.exists():
                logger.debug(f"Removing existing temp directory: {temp_extract}")
                shutil.rmtree(temp_extract)
            
            logger.info(f"Extracting to: {temp_extract}")
            
            if not self._extract_zip(temp_zip, temp_extract, progress_callback):
                error_msg = (
                    f"Failed to extract WIT tool. The downloaded file may be corrupted or not a valid ZIP file.\n\n"
                    f"Downloaded file size: {file_size} bytes ({file_size / (1024*1024):.2f} MB)\n"
                    f"Expected: >1 MB for a valid WIT zip file.\n\n"
                    "This usually means:\n"
                    "- The download URL returned an error page instead of the file\n"
                    "- The file was corrupted during download\n"
                    "- The URL is incorrect or outdated\n\n"
                    "Please download WIT manually from:\n"
                    "https://wit.wiimm.de/\n\n"
                    f"Extract wit.exe to: {self.wit_dir}\n\n"
                    "The application will check for tools on next launch."
                )
                logger.error(error_msg)
                temp_zip.unlink(missing_ok=True)
                return False, error_msg
            
            # Find wit.exe in extracted files
            wit_exe = self._find_wit_in_extracted(temp_extract)
            
            if not wit_exe:
                # Try to find any wit-related files and copy the whole directory structure
                # WIT zip might have a specific structure
                if progress_callback:
                    progress_callback("Locating WIT files...")
                
                # Check if wit.exe is directly in temp_extract
                direct_wit = temp_extract / "wit.exe"
                if direct_wit.exists():
                    wit_exe = direct_wit
                else:
                    # Look for any .exe files that might be wit
                    for exe_file in temp_extract.rglob("*.exe"):
                        if "wit" in exe_file.name.lower():
                            wit_exe = exe_file
                            break
                
                if not wit_exe:
                    # Copy entire extracted directory to wit_dir
                    if progress_callback:
                        progress_callback("Copying WIT files...")
                    shutil.copytree(temp_extract, self.wit_dir, dirs_exist_ok=True)
                    # Clean up
                    shutil.rmtree(temp_extract, ignore_errors=True)
                    temp_zip.unlink(missing_ok=True)
                    
                    # Check if we now have wit.exe
                    if self.check_wit():
                        return True, "WIT tool downloaded and extracted successfully"
                    else:
                        return False, "WIT tool extracted but wit.exe not found. Please check tools/wit/ directory."
            
            # Copy wit.exe and related files to wit_dir
            if progress_callback:
                progress_callback("Installing WIT tool...")
            
            # Copy the executable
            target_wit = self.wit_dir / wit_exe.name
            shutil.copy2(wit_exe, target_wit)
            
            # Copy any DLLs or related files from the same directory
            wit_dir = wit_exe.parent
            for item in wit_dir.iterdir():
                if item.is_file() and item.suffix in ['.dll', '.exe', '.txt', '.bat']:
                    target = self.wit_dir / item.name
                    if not target.exists():
                        shutil.copy2(item, target)
            
            # Clean up
            shutil.rmtree(temp_extract, ignore_errors=True)
            temp_zip.unlink(missing_ok=True)
            
            if self.check_wit():
                return True, "WIT tool downloaded and installed successfully"
            else:
                return False, "WIT tool installation incomplete"
                
        except Exception as e:
            error_msg = f"Error downloading WIT: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    def ensure_tools(self, progress_callback=None) -> Tuple[bool, str]:
        """
        Ensure both Dolphin and WIT tools are available.
        Downloads them if missing.
        
        Args:
            progress_callback: Optional callback function(status_message)
            
        Returns:
            Tuple of (all_available: bool, message: str)
        """
        messages = []
        dolphin_ok = self.check_dolphin_tool()
        wit_ok = self.check_wit()
        
        if dolphin_ok and wit_ok:
            return True, "All tools are available"
        
        # Try to download missing tools
        if not dolphin_ok:
            if progress_callback:
                progress_callback("Checking Dolphin tool...")
            success, msg = self.download_dolphin(progress_callback)
            messages.append(f"Dolphin: {msg}")
            if success:
                dolphin_ok = True
        
        if not wit_ok:
            if progress_callback:
                progress_callback("Checking WIT tool...")
            success, msg = self.download_wit(progress_callback)
            messages.append(f"WIT: {msg}")
            if success:
                wit_ok = True
        
        all_ok = dolphin_ok and wit_ok
        message = "\n".join(messages) if messages else "Tools check complete"
        
        return all_ok, message


def ensure_tools_available(project_root: Optional[Path] = None, progress_callback=None) -> Tuple[bool, str]:
    """
    Convenience function to ensure tools are available.
    
    Args:
        project_root: Root directory of the project
        progress_callback: Optional callback function(status_message)
        
    Returns:
        Tuple of (all_available: bool, message: str)
    """
    downloader = ToolDownloader(project_root)
    return downloader.ensure_tools(progress_callback)

