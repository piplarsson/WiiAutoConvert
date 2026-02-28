"""
Metadata Lookup Module
Extracts game IDs and looks up titles from GameTDB/WIT titles database.
"""

import re
import subprocess
from pathlib import Path
from typing import Optional, Tuple
import sys


class MetadataLookup:
    """
    Handles game ID extraction and title lookup from WIT titles database.
    """
    
    def __init__(self, tool_runner=None, titles_file: Optional[Path] = None):
        """
        Initialize metadata lookup.
        
        Args:
            tool_runner: ToolRunner instance (for accessing wit)
            titles_file: Path to titles.txt file. If None, uses bundled one.
        """
        from .tool_runner import ToolRunner
        
        self.tool_runner = tool_runner or ToolRunner()
        
        # Find titles file
        if titles_file is None:
            # Use bundled titles.txt from wit directory
            titles_file = self.tool_runner.project_root / "tools" / "wit" / "titles.txt"
        
        self.titles_file = Path(titles_file)
        self._titles_cache = None
    
    def _load_titles(self) -> dict:
        """
        Load titles database into memory.
        
        Returns:
            Dictionary mapping game ID to title
        """
        if self._titles_cache is not None:
            return self._titles_cache
        
        titles = {}
        
        if not self.titles_file.exists():
            return titles
        
        try:
            with open(self.titles_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse format: GAMEID = Title
                    # Support both 4-char and 6-char IDs
                    match = re.match(r'^([A-Z0-9]{4,6})\s*=\s*(.+)$', line)
                    if match:
                        game_id = match.group(1).upper()
                        title = match.group(2).strip()
                        titles[game_id] = title
        except Exception as e:
            print(f"Warning: Failed to load titles database: {e}")
        
        self._titles_cache = titles
        return titles
    
    def extract_game_id(self, iso_or_wbfs_path: Path) -> Optional[str]:
        """
        Extract game ID from ISO or WBFS file using WIT.
        
        Args:
            iso_or_wbfs_path: Path to ISO or WBFS file
            
        Returns:
            Game ID (6 characters) or None if extraction fails
        """
        iso_or_wbfs_path = Path(iso_or_wbfs_path).resolve()
        
        if not iso_or_wbfs_path.exists():
            return None
        
        try:
            # Use WIT to extract game ID
            # WIT ID command shows disc info including game ID
            cmd = [
                str(self.tool_runner.wit),
                "ID",
                str(iso_or_wbfs_path)
            ]
            
            kwargs = {
                "capture_output": True,
                "text": True,
                "timeout": 30,
            }

            if sys.platform == "win32":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                kwargs["startupinfo"] = startupinfo

            result = subprocess.run(cmd, **kwargs)
            
            if result.returncode != 0:
                return None
            
            # Parse output for game ID
            # WIT ID output format includes lines like:
            # "ID6:  SM2E52"
            # "ID4:  SM2E"
            output = result.stdout
            
            # Try to find ID6 (6-character game ID)
            id6_match = re.search(r'ID6:\s*([A-Z0-9]{6})', output, re.IGNORECASE)
            if id6_match:
                return id6_match.group(1).upper()
            
            # Fallback to ID4 (4-character game ID)
            id4_match = re.search(r'ID4:\s*([A-Z0-9]{4})', output, re.IGNORECASE)
            if id4_match:
                return id4_match.group(1).upper()
            
            # Alternative: look for 6-char pattern in output
            id_pattern = re.search(r'\b([A-Z0-9]{6})\b', output)
            if id_pattern:
                return id_pattern.group(1).upper()
        
        except subprocess.TimeoutExpired:
            return None
        except Exception as e:
            # Silently fail - metadata lookup is optional
            return None
        
        return None
    
    def lookup_title(self, game_id: str) -> Optional[str]:
        """
        Look up game title from titles database.
        
        Args:
            game_id: Game ID (4 or 6 characters)
            
        Returns:
            Game title or None if not found
        """
        if not game_id:
            return None
        
        game_id = game_id.upper()
        titles = self._load_titles()
        
        # Try 6-char ID first
        if len(game_id) >= 6:
            title = titles.get(game_id[:6])
            if title:
                return title
        
        # Try 4-char ID
        if len(game_id) >= 4:
            title = titles.get(game_id[:4])
            if title:
                return title
        
        return None
    
    def get_game_info(self, iso_or_wbfs_path: Path) -> Tuple[Optional[str], Optional[str]]:
        """
        Get game ID and title for a file.
        
        Args:
            iso_or_wbfs_path: Path to ISO or WBFS file
            
        Returns:
            Tuple of (game_id, title) or (None, None) if extraction fails
        """
        game_id = self.extract_game_id(iso_or_wbfs_path)
        if not game_id:
            return None, None
        
        title = self.lookup_title(game_id)
        return game_id, title
    
    def format_filename(self, title: str, game_id: str, extension: str = ".wbfs") -> str:
        """
        Format filename in Wii Backup Manager style: "Game Title [GAMEID]"
        Used for folder names. The file itself will be named "GAMEID.wbfs"
        
        Args:
            title: Game title
            game_id: Game ID
            extension: File extension (default: .wbfs, but typically not used for folder names)
            
        Returns:
            Formatted folder name: "Title [GAMEID]"
        """
        # Sanitize title for filename (remove invalid characters)
        # Windows invalid chars: < > : " / \ | ? *
        invalid_chars = r'[<>:"/\\|?*]'
        sanitized_title = re.sub(invalid_chars, '', title)
        
        # Remove leading/trailing spaces and dots
        sanitized_title = sanitized_title.strip(' .')
        
        # Limit length to avoid path issues (max ~200 chars total)
        max_title_len = 200 - len(f" [{game_id}]")
        if len(sanitized_title) > max_title_len:
            sanitized_title = sanitized_title[:max_title_len].rstrip()
        
        # Format: "Title [GAMEID]"
        folder_name = f"{sanitized_title} [{game_id}]"
        
        # Add extension if provided (for backward compatibility)
        if extension:
            folder_name += extension
        
        return folder_name

