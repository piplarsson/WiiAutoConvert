"""
Header Card Component
Title and subtitle display at the top of the application.
"""

import customtkinter as ctk
from .base_card import BaseCard
from ..theme import COLORS, SPACING, FONTS


class HeaderCard(BaseCard):
    """Header card with title, subtitle, and status badge."""
    
    def __init__(self, parent):
        """Initialize the header card."""
        super().__init__(parent, "Header")
        
        # Reduce padding for header (12px instead of default ~24px)
        # Repack content frame with reduced padding
        self.content_frame.pack_forget()
        self.content_frame.pack(fill="both", expand=True, padx=SPACING["card_padding"], pady=6)
        
        # Top row: Title and Status badge
        top_row = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 2))
        
        # Title
        title_label = ctk.CTkLabel(
            top_row,
            text="WiiAutoConvert",
            font=FONTS["title"],
            text_color=COLORS["text"],
            anchor="w"
        )
        title_label.pack(side="left", fill="x", expand=True)
        
        # Status badge
        self.status_badge = ctk.CTkLabel(
            top_row,
            text="Idle",
            font=FONTS["badge"],
            text_color=COLORS["muted"],
            fg_color=COLORS["border"],
            corner_radius=4,
            padx=8,
            pady=2
        )
        self.status_badge.pack(side="right")
        
        # Subtitle with higher contrast (muted * 0.85)
        subtitle_color = "#b0b5ba"  # Higher contrast than muted
        subtitle_label = ctk.CTkLabel(
            self.content_frame,
            text="RVZ to WBFS Converter",
            font=FONTS["subtitle"],
            text_color=subtitle_color,
            anchor="w"
        )
        subtitle_label.pack(fill="x")
        
        # Subtle divider glow under header
        divider = ctk.CTkFrame(
            self.content_frame,
            fg_color=COLORS["border"],
            height=1
        )
        divider.pack(fill="x", pady=(6, 0))
    
    def set_status(self, status: str, color: str = None):
        """Update the status badge."""
        if color is None:
            if status == "Converting":
                color = COLORS["accent"]
            elif status == "Watching":
                color = COLORS["success"]
            else:
                color = COLORS["muted"]
        
        self.status_badge.configure(text=status, fg_color=color)

