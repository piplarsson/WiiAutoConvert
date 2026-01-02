"""
Page 2: Output Directory
Destination selection for WBFS files.
"""

import customtkinter as ctk
from pathlib import Path
from typing import Callable
from ..theme import COLORS, SPACING, FONTS
from .wizard_controller import ConversionConfig


class PageOutput(ctk.CTkFrame):
    """Output directory selection page."""
    
    def __init__(self, parent, config: ConversionConfig, on_update: Callable = None):
        """
        Initialize output page.
        
        Args:
            parent: Parent widget
            config: Conversion configuration state
            on_update: Callback when output changes (for validation)
        """
        super().__init__(parent, fg_color="transparent")
        
        self.config = config
        self.on_update = on_update
        
        # Page title - pack at top
        title = ctk.CTkLabel(
            self,
            text="Where should the WBFS files go?",
            font=FONTS["title"],
            text_color=COLORS["text"],
            anchor="w"
        )
        title.pack(fill="x", side="top", anchor="n", pady=(0, SPACING["element_gap"]))
        
        # Output card - pack at top, don't expand vertically
        output_card = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            border_color=COLORS["border"],
            border_width=SPACING["border_width"],
            corner_radius=SPACING["border_radius"]
        )
        output_card.pack(fill="x", side="top", anchor="n", pady=(0, SPACING["card_gap"]))
        
        content = ctk.CTkFrame(output_card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=SPACING["card_padding"], pady=SPACING["card_padding"])
        
        # Label with folder icon
        label = ctk.CTkLabel(
            content,
            text="📁 Output Directory:",
            font=FONTS["body"],
            text_color=COLORS["text"],
            anchor="w"
        )
        label.pack(fill="x", pady=(0, SPACING["element_gap"]))
        
        # Entry and button frame
        entry_frame = ctk.CTkFrame(content, fg_color="transparent")
        entry_frame.pack(fill="x", pady=(0, SPACING["element_gap"]))
        
        # Output path entry (read-only styled)
        self.output_var = ctk.StringVar(value="")
        if self.config.output_dir:
            self.output_var.set(str(self.config.output_dir))
        
        self.output_entry = ctk.CTkEntry(
            entry_frame,
            textvariable=self.output_var,
            state="readonly",
            fg_color=COLORS["bg"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            font=FONTS["mono"],
            height=36
        )
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, SPACING["element_gap"]))
        
        # Browse button (primary, stronger)
        browse_btn = ctk.CTkButton(
            entry_frame,
            text="📂 Browse",
            command=self._browse_output,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            text_color=COLORS["bg"],
            font=FONTS["body"],
            height=36,
            width=140
        )
        browse_btn.pack(side="left")
        
        # Helper text
        helper_text = ctk.CTkLabel(
            content,
            text="WBFS files will be created here before any network move",
            font=FONTS["subtitle"],
            text_color=COLORS["muted"],
            anchor="w",
            wraplength=600
        )
        helper_text.pack(fill="x", pady=(SPACING["element_gap"], 0))
    
    def _browse_output(self):
        """Browse for output directory."""
        from tkinter import filedialog
        
        folder = filedialog.askdirectory(title="Select Output Directory")
        if folder:
            self.config.output_dir = Path(folder)
            self.output_var.set(str(self.config.output_dir))
            self._update_validation()
    
    def _update_validation(self):
        """Update validation state."""
        if self.on_update:
            self.on_update()
    
    def is_valid(self) -> bool:
        """Check if page is valid (has output directory)."""
        return self.config.output_dir is not None and self.config.output_dir.exists()

