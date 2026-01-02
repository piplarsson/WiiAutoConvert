"""
Tool Runner Module
Handles execution of bundled external tools (dolphin-tool and wit).
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple, List
from .tool_downloader import ToolDownloader


class ToolRunner:
    """
    Manages execution of bundled conversion tools.
    Handles path resolution, subprocess execution, and output capture.
    """
    
    def __init__(self, project_root: Optional[Path] = None, auto_download: bool = True):
        """
        Initialize the tool runner.
        
        Args:
            project_root: Root directory of the project. If None, auto-detects.
            auto_download: If True, automatically download missing tools.
        """
        if project_root is None:
            # Auto-detect project root (parent of src/)
            project_root = Path(__file__).parent.parent
        
        self.project_root = Path(project_root).resolve()
        self._dolphin_tool = None
        self._wit = None
        
        # Check and download tools if missing
        if auto_download:
            self._ensure_tools()
    
    def _ensure_tools(self):
        """Ensure required tools are available, download if missing."""
        downloader = ToolDownloader(self.project_root)
        dolphin_ok = downloader.check_dolphin_tool()
        wit_ok = downloader.check_wit()
        
        if not dolphin_ok or not wit_ok:
            # Try to download missing tools (silent mode for CLI)
            downloader.ensure_tools()
    
    @property
    def dolphin_tool(self) -> Path:
        """Get path to dolphin-tool executable."""
        if self._dolphin_tool is None:
            if sys.platform == "win32":
                tool_path = self.project_root / "tools" / "dolphin" / "DolphinTool.exe"
            else:
                tool_path = self.project_root / "tools" / "dolphin" / "dolphin-tool"
            
            if not tool_path.exists():
                # Try to download if not found
                downloader = ToolDownloader(self.project_root)
                if not downloader.check_dolphin_tool():
                    downloader.download_dolphin()
                
                # Check again
                if not tool_path.exists():
                    raise FileNotFoundError(
                        f"Dolphin tool not found at {tool_path}. "
                        "Please download Dolphin from https://dolphin-emu.org/download/ "
                        f"and extract DolphinTool.exe to {tool_path.parent}"
                    )
            self._dolphin_tool = tool_path
        return self._dolphin_tool
    
    @property
    def wit(self) -> Path:
        """Get path to wit executable."""
        if self._wit is None:
            if sys.platform == "win32":
                tool_path = self.project_root / "tools" / "wit" / "wit.exe"
            else:
                tool_path = self.project_root / "tools" / "wit" / "wit"
            
            if not tool_path.exists():
                # Try to download if not found
                downloader = ToolDownloader(self.project_root)
                if not downloader.check_wit():
                    success, _ = downloader.download_wit()
                    if not success:
                        # If download failed, check one more time
                        if not tool_path.exists():
                            raise FileNotFoundError(
                                f"WIT tool not found at {tool_path}. "
                                "Automatic download failed. Please download WIT from "
                                "https://wit.wiimm.de/ and extract wit.exe to "
                                f"{tool_path.parent}"
                            )
            self._wit = tool_path
        return self._wit
    
    def run_dolphin_convert(
        self,
        input_rvz: Path,
        output_iso: Path,
        verbose: bool = False
    ) -> Tuple[int, str, str]:
        """
        Execute dolphin-tool convert command.
        
        Args:
            input_rvz: Path to input RVZ file
            output_iso: Path to output ISO file
            verbose: Enable verbose output
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        # Ensure output directory exists
        output_iso.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            str(self.dolphin_tool),
            "convert",
            "-i", str(input_rvz),
            "-o", str(output_iso),
            "-f", "iso"
        ]
        
        if verbose:
            cmd.append("-v")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout for large files
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Dolphin conversion timed out for {input_rvz}")
        except Exception as e:
            raise RuntimeError(f"Failed to execute dolphin-tool: {e}")
    
    def run_wit_copy(
        self,
        input_iso: Path,
        output_wbfs: Path,
        verbose: bool = False
    ) -> Tuple[int, str, str]:
        """
        Execute wit copy command.
        
        Args:
            input_iso: Path to input ISO file
            output_wbfs: Path to output WBFS file
            verbose: Enable verbose output
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        # Ensure output directory exists
        output_wbfs.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            str(self.wit),
            "copy",
            str(input_iso),
            str(output_wbfs)
        ]
        
        if verbose:
            cmd.append("-v")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout for large files
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"WIT conversion timed out for {input_iso}")
        except Exception as e:
            raise RuntimeError(f"Failed to execute wit: {e}")

