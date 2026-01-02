"""
Output Card Component
Output directory selection interface.
"""

import customtkinter as ctk
from typing import Callable
from .base_card import BaseCard
from ..theme import COLORS, SPACING, FONTS


class OutputCard(BaseCard):
    """Output card for selecting output directory."""
    
    def __init__(self, parent, on_browse: Callable = None):
        """Initialize the output card."""
        super().__init__(parent, "Output")
        
        # Label with folder icon
        label_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        label_frame.pack(fill="x", pady=(0, SPACING["element_gap"]))
        
        label = ctk.CTkLabel(
            label_frame,
            text="📁 Output Directory:",
            font=FONTS["body"],
            text_color=COLORS["text"],
            anchor="w"
        )
        label.pack(side="left")
        
        # Entry and button frame
        entry_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        entry_frame.pack(fill="x")
        
        # Output path entry (read-only display with folder icon prefix)
        self.output_var = ctk.StringVar(value="")
        self.output_entry = ctk.CTkEntry(
            entry_frame,
            textvariable=self.output_var,
            state="readonly",
            fg_color=COLORS["bg"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            font=FONTS["mono"],
            height=28,
            placeholder_text="No output directory selected"
        )
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, SPACING["element_gap"]))
        
        # Browse button - stronger visual
        browse_btn = ctk.CTkButton(
            entry_frame,
            text="📂 Browse",
            command=on_browse or (lambda: None),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            text_color=COLORS["bg"],
            font=FONTS["body"],
            height=28,
            width=100  # Fixed width for consistency
        )
        browse_btn.pack(side="left")
        
        # Free space label (will be updated when path is set)
        self.free_space_label = ctk.CTkLabel(
            self.content_frame,
            text="",
            font=FONTS["subtitle"],
            text_color=COLORS["muted"],
            anchor="w"
        )
        self.free_space_label.pack(fill="x", pady=(4, 0))
    
    def set_output_path(self, path: str):
        """Set the output path display."""
        self.output_var.set(path)
        # Update free space display (simplified - could add actual disk space check)
        if path:
            self.free_space_label.configure(text=f"Destination: {path}")
        else:
            self.free_space_label.configure(text="")

