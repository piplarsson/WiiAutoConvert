"""
Action Bar Component
Start, cancel, and watch mode controls.
"""

import customtkinter as ctk
from typing import Callable
from .base_card import BaseCard
from ..theme import COLORS, SPACING, FONTS


class ActionBar(BaseCard):
    """Action bar with conversion control buttons."""
    
    def __init__(
        self,
        parent,
        on_start: Callable = None,
        on_cancel: Callable = None,
        on_watch: Callable = None
    ):
        """Initialize the action bar."""
        super().__init__(parent, "Actions")
        
        # Buttons frame with better layout
        buttons_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        buttons_frame.pack(fill="x")
        
        # Left side: Start Conversion (dominant)
        left_frame = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="x", expand=True)
        
        # Start button - DOMINANT (wider, stronger)
        self.start_button = ctk.CTkButton(
            left_frame,
            text="Start Conversion",
            command=on_start or (lambda: None),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            text_color=COLORS["bg"],
            font=FONTS["body"],
            height=32,  # Slightly taller for dominance
            width=180  # Fixed wider width
        )
        self.start_button.pack(side="left")
        
        # Right side: Watch Mode toggle and Cancel
        right_frame = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        right_frame.pack(side="right")
        
        # Watch mode button - toggle style
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
            height=28,
            width=120
        )
        self.watch_button.pack(side="left", padx=(0, SPACING["element_gap"]))
        
        # Cancel button - disabled until active
        self.cancel_button = ctk.CTkButton(
            right_frame,
            text="Cancel",
            command=on_cancel or (lambda: None),
            fg_color=COLORS["border"],
            hover_color=COLORS["error"],
            text_color=COLORS["text"],
            font=FONTS["body"],
            height=28,
            width=80,
            state="disabled"
        )
        self.cancel_button.pack(side="left")
    
    def set_converting(self, is_converting: bool):
        """Update button states for conversion."""
        if is_converting:
            self.start_button.configure(state="disabled")
            self.cancel_button.configure(state="normal")
        else:
            self.start_button.configure(state="normal")
            self.cancel_button.configure(state="disabled")
    
    def set_watch_mode(self, is_watching: bool):
        """Update button states for watch mode."""
        if is_watching:
            self.watch_button.configure(text="▣ Watch Mode", fg_color=COLORS["success"])
            self.start_button.configure(state="disabled")
        else:
            self.watch_button.configure(text="▢ Watch Mode", fg_color="transparent")
            self.start_button.configure(state="normal")

