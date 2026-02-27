"""
Wizard Controller
Manages wizard state, navigation, and page flow.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Callable
import customtkinter as ctk

from ..theme import COLORS, SPACING


@dataclass
class CleanupOptions:
    """Cleanup behavior flags."""
    delete_after_network_move: bool = False
    keep_iso: bool = False
    preserve_structure: bool = True
    keep_extracted: bool = False
    delete_zip: bool = False


@dataclass
class ConversionConfig:
    """Centralized conversion configuration state."""
    input_items: List[Path] = field(default_factory=list)
    output_dir: Optional[Path] = None
    
    # Network options
    enable_network_move: bool = False
    network_path: str = ""
    keep_local_copy: bool = False
    
    # Transfer behavior
    overwrite_mode: str = "skip"
    retries: int = 3
    max_concurrent: int = 1
    
    # Cleanup options
    cleanup: CleanupOptions = field(default_factory=CleanupOptions)


class WizardController:
    """
    Controls wizard navigation and state.
    Manages page flow and validation.
    """
    
    def __init__(self, root: ctk.CTk, on_start_conversion: Callable = None, on_start_watch: Callable = None):
        """
        Initialize the wizard controller.
        
        Args:
            root: Root window
            on_start_conversion: Callback when conversion starts
            on_start_watch: Callback when watch mode starts
        """
        self.root = root
        self.on_start_conversion = on_start_conversion
        self.on_start_watch = on_start_watch
        
        # State
        self.config = ConversionConfig()
        self.current_page = 0
        self.is_executing = False  # Lock pages during execution
        
        # Page references (set by pages themselves)
        self.pages: List[ctk.CTkFrame] = []
        self.page_validators: List[Callable[[], bool]] = []
        
        # Container for pages (don't pack yet - will be packed after navigation)
        self.container = ctk.CTkFrame(root, fg_color="transparent")
        
        # Navigation bar (will be created after pages)
        self.nav_frame: Optional[ctk.CTkFrame] = None
    
    def add_page(self, page: ctk.CTkFrame, validator: Callable[[], bool] = None):
        """
        Register a page with the wizard.
        
        Args:
            page: Page widget
            validator: Function that returns True if page is valid
        """
        self.pages.append(page)
        self.page_validators.append(validator or (lambda: True))
        page.pack_forget()  # Hide initially
    
    def set_navigation(self, nav_frame: ctk.CTkFrame):
        """Set the navigation bar and pack container after navigation."""
        self.nav_frame = nav_frame
        # Pack container to fill available space (positioning will be handled in _update_navigation)
        self.container.pack(fill="both", expand=True, side="top", anchor="n")
    
    def go_to_page(self, page_index: int):
        """Navigate to a specific page."""
        if self.is_executing and page_index < len(self.pages) - 1:
            return  # Can't navigate away from progress page during execution
        
        if 0 <= page_index < len(self.pages):
            # Hide current page
            if 0 <= self.current_page < len(self.pages):
                self.pages[self.current_page].pack_forget()
            
            # Show new page - expand to fill space but ensure content is top-anchored
            self.current_page = page_index
            # Pack page to fill container, content inside will be top-anchored
            self.pages[self.current_page].pack(fill="both", expand=True, side="top", anchor="n", before=self.nav_frame if self.nav_frame else None)
            
            # Update navigation
            if self.nav_frame:
                self._update_navigation()
    
    def get_next_button_text(self) -> str:
        """Get the text for the next button based on current page."""
        # The progress page is the last page. Conversion must start from the
        # page before it, otherwise the user lands on the progress page and the
        # only obvious action is the watch-mode button.
        if self.current_page == len(self.pages) - 2:
            return "Start Conversion"
        return "Next"
    
    def next_page(self):
        """Move to next page if current page is valid."""
        if self._is_current_page_valid():
            # Normal page advance until the last configuration page.
            if self.current_page < len(self.pages) - 2:
                self.go_to_page(self.current_page + 1)
            # Start conversion from the final configuration page.
            elif self.current_page == len(self.pages) - 2:
                if self.on_start_conversion:
                    self.is_executing = True
                    self.on_start_conversion(self.config)
                    self._update_navigation()
    
    def previous_page(self):
        """Move to previous page."""
        if not self.is_executing and self.current_page > 0:
            self.go_to_page(self.current_page - 1)
    
    def _is_current_page_valid(self) -> bool:
        """Check if current page is valid."""
        if 0 <= self.current_page < len(self.page_validators):
            return self.page_validators[self.current_page]()
        return True
    
    def _update_navigation(self):
        """Update navigation button states."""
        if not self.nav_frame:
            return
        
        # Progress page (last page) - hide navigation during execution
        is_progress_page = self.current_page == len(self.pages) - 1
        
        # Pages 2 and 3 (indices 1 and 2) should have navigation at bottom
        is_page_2_or_3 = self.current_page in [1, 2]
        
        if is_progress_page and self.is_executing:
            # Hide navigation during execution
            self.nav_frame.pack_forget()
        elif is_progress_page and not self.is_executing:
            # Show navigation on the progress page when idle so the user can go
            # back and change settings after a completed run.
            self.nav_frame.pack(fill="x", side="bottom", anchor="s", pady=(SPACING["card_gap"], 0))
            if hasattr(self.nav_frame, 'set_back_enabled'):
                self.nav_frame.set_back_enabled(True)
            if hasattr(self.nav_frame, 'set_next_enabled'):
                self.nav_frame.set_next_enabled(False)
        elif is_page_2_or_3:
            # Pages 2 and 3: navigation at bottom
            # Pack nav at bottom FIRST (this reserves space at bottom)
            self.nav_frame.pack_forget()  # Unpack first to change position
            self.nav_frame.pack(fill="x", side="bottom", anchor="s", pady=(SPACING["card_gap"], 0))
            # Then pack container at top to fill remaining space above nav
            self.container.pack_forget()
            self.container.pack(fill="both", expand=True, side="top", anchor="n")
            if hasattr(self.nav_frame, 'set_back_enabled'):
                self.nav_frame.set_back_enabled(self.current_page > 0 and not self.is_executing)
            
            if hasattr(self.nav_frame, 'set_next_enabled'):
                is_valid = self._is_current_page_valid()
                self.nav_frame.set_next_enabled(is_valid and not self.is_executing)
            
            if hasattr(self.nav_frame, 'set_next_text'):
                self.nav_frame.set_next_text(self.get_next_button_text())
        else:
            # Page 1: navigation at top
            # Pack nav first at top
            self.nav_frame.pack_forget()  # Unpack first to change position
            self.nav_frame.pack(fill="x", side="top", anchor="n", pady=(0, SPACING["element_gap"]))
            # Then pack container below nav
            self.container.pack_forget()
            self.container.pack(fill="both", expand=True, side="top", anchor="n", after=self.nav_frame)
            if hasattr(self.nav_frame, 'set_back_enabled'):
                self.nav_frame.set_back_enabled(self.current_page > 0 and not self.is_executing)
            
            if hasattr(self.nav_frame, 'set_next_enabled'):
                is_valid = self._is_current_page_valid()
                self.nav_frame.set_next_enabled(is_valid and not self.is_executing)
            
            if hasattr(self.nav_frame, 'set_next_text'):
                self.nav_frame.set_next_text(self.get_next_button_text())
    
    def start(self):
        """Start the wizard on page 0."""
        if self.pages:
            self.go_to_page(0)
    
    def set_executing(self, executing: bool):
        """Set execution state (locks navigation)."""
        self.is_executing = executing
        self._update_navigation()

