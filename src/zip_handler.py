"""
ZIP Handler Module
Handles extraction of RVZ files from ZIP archives.
"""

import zipfile
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple
import shutil


class ZipHandler:
    """
    Handles extraction of RVZ files from ZIP archives.
    """
    
    def __init__(self, extract_dir: Optional[Path] = None):
        """
        Initialize ZIP handler.
        
        Args:
            extract_dir: Directory for extracted files. If None, uses temp directory.
        """
        if extract_dir is None:
            self.extract_dir = Path(tempfile.gettempdir()) / "rvz2wbfs_extract"
        else:
            self.extract_dir = Path(extract_dir)
        
        self.extract_dir.mkdir(parents=True, exist_ok=True)
    
    def is_zip_file(self, path: Path) -> bool:
        """
        Check if a file is a ZIP archive.
        
        Args:
            path: File path to check
            
        Returns:
            True if file is a ZIP archive
        """
        if not path.is_file():
            return False
        
        # Check extension
        if path.suffix.lower() not in ['.zip', '.7z', '.rar']:
            # Only support .zip for now, but check magic bytes for .zip
            try:
                with open(path, 'rb') as f:
                    magic = f.read(4)
                    return magic == b'PK\x03\x04'  # ZIP magic bytes
            except:
                return False
        
        # Try to open as ZIP to verify
        try:
            with zipfile.ZipFile(path, 'r') as zf:
                return True
        except (zipfile.BadZipFile, zipfile.LargeZipFile):
            return False
        except Exception:
            return False
    
    def extract_rvz_from_zip(
        self,
        zip_path: Path,
        password: Optional[str] = None
    ) -> Tuple[List[Path], Path]:
        """
        Extract RVZ files from a ZIP archive.
        
        Args:
            zip_path: Path to ZIP file
            password: Optional password for encrypted ZIP
            
        Returns:
            Tuple of (list of extracted RVZ file paths, extraction directory)
            
        Raises:
            zipfile.BadZipFile: If ZIP file is corrupted
            RuntimeError: If extraction fails
        """
        zip_path = Path(zip_path).resolve()
        
        if not zip_path.exists():
            raise FileNotFoundError(f"ZIP file not found: {zip_path}")
        
        # Create extraction directory for this ZIP
        zip_name = zip_path.stem
        extract_path = self.extract_dir / zip_name
        extract_path.mkdir(parents=True, exist_ok=True)
        
        rvz_files = []
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                # Check if password is needed
                if zf.testzip() is not None:
                    if password is None:
                        # Try without password first
                        try:
                            zf.testzip()
                        except RuntimeError:
                            raise RuntimeError(
                                f"ZIP file appears to be password-protected: {zip_path}\n"
                                "Password-protected ZIPs are not yet supported."
                            )
                
                # Extract all files
                zf.extractall(extract_path, pwd=password.encode() if password else None)
                
                # Find all RVZ files in extracted contents
                for extracted_file in extract_path.rglob("*"):
                    if extracted_file.is_file():
                        if extracted_file.suffix.lower() == '.rvz':
                            rvz_files.append(extracted_file)
        
        except zipfile.BadZipFile as e:
            raise RuntimeError(f"Invalid or corrupted ZIP file: {zip_path} - {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to extract ZIP file {zip_path}: {e}")
        
        if not rvz_files:
            # Clean up empty extraction directory
            try:
                shutil.rmtree(extract_path)
            except:
                pass
            raise RuntimeError(f"No RVZ files found in ZIP archive: {zip_path}")
        
        return rvz_files, extract_path
    
    def cleanup_extraction(self, extract_path: Path):
        """
        Clean up extracted files.
        
        Args:
            extract_path: Path to extraction directory
        """
        try:
            if extract_path.exists() and extract_path.is_dir():
                shutil.rmtree(extract_path)
        except Exception as e:
            # Log but don't fail
            print(f"Warning: Failed to cleanup extraction directory {extract_path}: {e}")
    
    def find_zip_files(self, path: Path) -> List[Path]:
        """
        Find all ZIP files in a path (file or directory).
        
        Args:
            path: File or directory path
            
        Returns:
            List of ZIP file paths
        """
        path = Path(path).resolve()
        zip_files = []
        
        if path.is_file():
            if self.is_zip_file(path):
                zip_files.append(path)
        elif path.is_dir():
            # Find ZIP files
            for zip_file in path.rglob("*.zip"):
                if self.is_zip_file(zip_file):
                    zip_files.append(zip_file)
            for zip_file in path.rglob("*.ZIP"):
                if self.is_zip_file(zip_file):
                    zip_files.append(zip_file)
        
        return sorted(zip_files)

