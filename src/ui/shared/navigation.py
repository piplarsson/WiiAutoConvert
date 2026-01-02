"""
Navigation Bar Component
Back/Next buttons for wizard navigation.
"""

import customtkinter as ctk
from typing import Callable, Optional
from ..theme import COLORS, SPACING, FONTS


class NavigationBar(ctk.CTkFrame):
    """Navigation bar with Back/Next buttons."""
    
    def __init__(
        self,
        parent,
        on_back: Callable = None,
        on_next: Callable = None,
        next_text: str = "Next",
        show_watch: bool = False,
        on_watch: Callable = None
    ):
        """
        Initialize navigation bar.
        
        Args:
            parent: Parent widget
            on_back: Back button callback
            on_next: Next button callback
            next_text: Text for next button (default: "Next")
            show_watch: Show watch mode button
            on_watch: Watch mode button callback
        """
        super().__init__(
            parent,
            fg_color=COLORS["card"],
            border_color=COLORS["border"],
            border_width=SPACING["border_width"],
            corner_radius=SPACING["border_radius"]
        )
        
        # Internal padding (reduced vertical padding)
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="x", padx=SPACING["card_padding"], pady=(6, 6))
        
        # Left side: Back button
        left_frame = ctk.CTkFrame(content, fg_color="transparent")
        left_frame.pack(side="left")
        
        self.back_button = ctk.CTkButton(
            left_frame,
            text="← Back",
            command=on_back or (lambda: None),
            fg_color="transparent",
            border_color=COLORS["border"],
            border_width=1,
            hover_color=COLORS["border"],
            text_color=COLORS["text"],
            font=FONTS["body"],
            height=32,
            width=100,
            state="disabled"
        )
        self.back_button.pack(side="left")
        
        # Right side: Watch (if shown) and Next/Start
        right_frame = ctk.CTkFrame(content, fg_color="transparent")
        right_frame.pack(side="right")
        
        if show_watch and on_watch:
            self.watch_button = ctk.CTkButton(
                right_frame,
                text="▢ Watch Mode",
                command=on_watch or (lambda: None),
                fg_color="transparent",
                border_color=COLORS["border"],
                border_width=1,
                hover_color=COLORS["border"],
                text_color=COLORS["text"],
                font=FONTS["body"],
                height=32,
                width=120
            )
            self.watch_button.pack(side="left", padx=(0, SPACING["element_gap"]))
        else:
            self.watch_button = None
        
        self.next_button = ctk.CTkButton(
            right_frame,
            text=next_text,
            command=on_next or (lambda: None),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            text_color=COLORS["bg"],
            font=FONTS["body"],
            height=32,
            width=140,
            state="disabled"
        )
        self.next_button.pack(side="left")
    
    def set_back_enabled(self, enabled: bool):
        """Enable/disable back button."""
        self.back_button.configure(state="normal" if enabled else "disabled")
    
    def set_next_enabled(self, enabled: bool):
        """Enable/disable next button."""
        self.next_button.configure(state="normal" if enabled else "disabled")
    
    def set_next_text(self, text: str):
        """Change next button text."""
        self.next_button.configure(text=text)
    
    def set_watch_text(self, text: str, active: bool = False):
        """Update watch button text and state."""
        if self.watch_button:
            self.watch_button.configure(
                text=text,
                fg_color=COLORS["success"] if active else "transparent"
            )

