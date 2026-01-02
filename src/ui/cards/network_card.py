"""
Network Card Component
Network move options and conversion settings with progressive disclosure.
"""

import customtkinter as ctk
from typing import Callable
from .base_card import BaseCard
from ..theme import COLORS, SPACING, FONTS


class NetworkCard(BaseCard):
    """Network card for network move options and conversion settings."""
    
    def __init__(self, parent):
        """Initialize the network card."""
        super().__init__(parent, "Network Move & Options")
        
        # ====================================================================
        # LAYER 1: Always Visible - Basic Network Options
        # ====================================================================
        
        # Enable network checkbox (primary toggle)
        self.enable_network_var = ctk.BooleanVar(value=False)
        enable_network_cb = ctk.CTkCheckBox(
            self.content_frame,
            text="Enable network move",
            variable=self.enable_network_var,
            font=FONTS["body"],
            text_color=COLORS["text"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            checkbox_width=18,
            checkbox_height=18
        )
        enable_network_cb.pack(anchor="w", pady=(0, 4))
        
        # Network path section
        network_label = ctk.CTkLabel(
            self.content_frame,
            text="Network Path:",
            font=FONTS["body"],
            text_color=COLORS["text"],
            anchor="w"
        )
        network_label.pack(fill="x", pady=(0, 4))
        
        self.network_path_var = ctk.StringVar(value="")
        network_entry = ctk.CTkEntry(
            self.content_frame,
            textvariable=self.network_path_var,
            fg_color=COLORS["bg"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            font=FONTS["mono"],
            height=28
        )
        network_entry.pack(fill="x", pady=(0, 4))
        
        # Keep local copy checkbox
        self.keep_local_var = ctk.BooleanVar(value=False)
        keep_local_cb = ctk.CTkCheckBox(
            self.content_frame,
            text="Keep local copy (copy instead of move)",
            variable=self.keep_local_var,
            font=FONTS["body"],
            text_color=COLORS["text"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            checkbox_width=18,
            checkbox_height=18
        )
        keep_local_cb.pack(anchor="w", pady=(0, 4))
        
        # ====================================================================
        # LAYER 2: Advanced Network Options (Collapsible)
        # ====================================================================
        
        # Advanced options toggle button
        self.advanced_expanded = False
        self.advanced_frame = None
        
        def toggle_advanced():
            self.advanced_expanded = not self.advanced_expanded
            if self.advanced_expanded:
                self.advanced_frame.pack(fill="x", pady=(4, 0))
                advanced_btn.configure(text="▾ Advanced Network Options")
            else:
                self.advanced_frame.pack_forget()
                advanced_btn.configure(text="▸ Advanced Network Options")
        
        advanced_btn = ctk.CTkButton(
            self.content_frame,
            text="▸ Advanced Network Options",
            command=toggle_advanced,
            fg_color="transparent",
            border_color=COLORS["border"],
            border_width=1,
            hover_color=COLORS["border"],
            text_color=COLORS["muted"],
            font=FONTS["subtitle"],
            height=24,
            anchor="w"
        )
        advanced_btn.pack(fill="x", pady=(4, 0))
        
        # Advanced options container (hidden by default)
        self.advanced_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        # Don't pack initially - starts collapsed
        
        # Overwrite behavior
        overwrite_frame = ctk.CTkFrame(self.advanced_frame, fg_color="transparent")
        overwrite_frame.pack(fill="x", pady=(4, 4))
        
        overwrite_label = ctk.CTkLabel(
            overwrite_frame,
            text="Overwrite:",
            font=FONTS["body"],
            text_color=COLORS["text"],
            width=100
        )
        overwrite_label.pack(side="left", padx=(0, SPACING["element_gap"]))
        
        self.network_overwrite_var = ctk.StringVar(value="skip")
        overwrite_combo = ctk.CTkComboBox(
            overwrite_frame,
            values=["skip", "append_timestamp", "append_version", "overwrite"],
            variable=self.network_overwrite_var,
            font=FONTS["body"],
            fg_color=COLORS["bg"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent"],
            dropdown_fg_color=COLORS["card"],
            dropdown_text_color=COLORS["text"],
            dropdown_hover_color=COLORS["border"],
            height=28
        )
        overwrite_combo.pack(side="left", fill="x", expand=True)
        
        # Retries
        retries_frame = ctk.CTkFrame(self.advanced_frame, fg_color="transparent")
        retries_frame.pack(fill="x", pady=(0, 4))
        
        retries_label = ctk.CTkLabel(
            retries_frame,
            text="Retries:",
            font=FONTS["body"],
            text_color=COLORS["text"],
            width=100
        )
        retries_label.pack(side="left", padx=(0, SPACING["element_gap"]))
        
        self.network_retries_var = ctk.StringVar(value="3")
        retries_entry = ctk.CTkEntry(
            retries_frame,
            textvariable=self.network_retries_var,
            width=100,
            fg_color=COLORS["bg"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            font=FONTS["body"],
            height=28
        )
        retries_entry.pack(side="left")
        
        # Delete after network move checkbox
        self.delete_after_network_move_var = ctk.BooleanVar(value=False)
        delete_after_cb = ctk.CTkCheckBox(
            self.advanced_frame,
            text="Delete local files (input ZIP and output WBFS) after successful network move",
            variable=self.delete_after_network_move_var,
            font=FONTS["body"],
            text_color=COLORS["text"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            checkbox_width=18,
            checkbox_height=18
        )
        delete_after_cb.pack(anchor="w", pady=(0, 4))
        
        # Max concurrent
        concurrent_frame = ctk.CTkFrame(self.advanced_frame, fg_color="transparent")
        concurrent_frame.pack(fill="x", pady=(0, 4))
        
        concurrent_label = ctk.CTkLabel(
            concurrent_frame,
            text="Max Concurrent:",
            font=FONTS["body"],
            text_color=COLORS["text"],
            width=100
        )
        concurrent_label.pack(side="left", padx=(0, SPACING["element_gap"]))
        
        self.max_concurrent_var = ctk.StringVar(value="1")
        concurrent_entry = ctk.CTkEntry(
            concurrent_frame,
            textvariable=self.max_concurrent_var,
            width=100,
            fg_color=COLORS["bg"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            font=FONTS["body"],
            height=28
        )
        concurrent_entry.pack(side="left", padx=(0, SPACING["element_gap"]))
        
        concurrent_hint = ctk.CTkLabel(
            concurrent_frame,
            text="(1 recommended for USB HDD)",
            font=FONTS["subtitle"],
            text_color=COLORS["muted"]
        )
        concurrent_hint.pack(side="left")
        
        # ====================================================================
        # Conversion Options Section (Separator)
        # ====================================================================
        
        separator = ctk.CTkFrame(
            self.content_frame,
            fg_color=COLORS["border"],
            height=1
        )
        separator.pack(fill="x", pady=6)
        
        # Group label for conversion options
        conversion_label = ctk.CTkLabel(
            self.content_frame,
            text="Conversion Options:",
            font=FONTS["body"],
            text_color=COLORS["muted"],
            anchor="w"
        )
        conversion_label.pack(fill="x", pady=(0, 4))
        
        # Keep ISO checkbox
        self.keep_iso_var = ctk.BooleanVar(value=False)
        keep_iso_cb = ctk.CTkCheckBox(
            self.content_frame,
            text="Keep intermediate ISO files",
            variable=self.keep_iso_var,
            font=FONTS["body"],
            text_color=COLORS["text"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            checkbox_width=18,
            checkbox_height=18
        )
        keep_iso_cb.pack(anchor="w", pady=(0, 3))
        
        # Preserve structure checkbox
        self.preserve_structure_var = ctk.BooleanVar(value=True)
        preserve_structure_cb = ctk.CTkCheckBox(
            self.content_frame,
            text="Preserve directory structure",
            variable=self.preserve_structure_var,
            font=FONTS["body"],
            text_color=COLORS["text"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            checkbox_width=18,
            checkbox_height=18
        )
        preserve_structure_cb.pack(anchor="w", pady=(0, 3))
        
        # Cleanup options group
        cleanup_separator = ctk.CTkFrame(
            self.content_frame,
            fg_color=COLORS["border"],
            height=1
        )
        cleanup_separator.pack(fill="x", pady=(4, 4))
        
        cleanup_label = ctk.CTkLabel(
            self.content_frame,
            text="Cleanup Options:",
            font=FONTS["body"],
            text_color=COLORS["muted"],
            anchor="w"
        )
        cleanup_label.pack(fill="x", pady=(0, 4))
        
        # Keep extracted checkbox
        self.keep_extracted_var = ctk.BooleanVar(value=False)
        keep_extracted_cb = ctk.CTkCheckBox(
            self.content_frame,
            text="Keep extracted RVZ files from ZIP",
            variable=self.keep_extracted_var,
            font=FONTS["body"],
            text_color=COLORS["text"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            checkbox_width=18,
            checkbox_height=18
        )
        keep_extracted_cb.pack(anchor="w", pady=(0, 3))
        
        # Delete ZIP checkbox
        self.delete_zip_var = ctk.BooleanVar(value=False)
        delete_zip_cb = ctk.CTkCheckBox(
            self.content_frame,
            text="Delete original ZIP files after conversion",
            variable=self.delete_zip_var,
            font=FONTS["body"],
            text_color=COLORS["text"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            checkbox_width=18,
            checkbox_height=18
        )
        delete_zip_cb.pack(anchor="w")
    
    # Getters for accessing values
    def is_network_enabled(self) -> bool:
        """Check if network move is enabled."""
        return self.enable_network_var.get()
    
    def get_network_path(self) -> str:
        """Get network path."""
        return self.network_path_var.get()
    
    def get_keep_local(self) -> bool:
        """Get keep local copy setting."""
        return self.keep_local_var.get()
    
    def get_overwrite_behavior(self) -> str:
        """Get overwrite behavior."""
        return self.network_overwrite_var.get()
    
    def get_retries(self) -> str:
        """Get retries count."""
        return self.network_retries_var.get()
    
    def get_delete_after_move(self) -> bool:
        """Get delete after network move setting."""
        return self.delete_after_network_move_var.get()
    
    def get_max_concurrent(self) -> str:
        """Get max concurrent setting."""
        return self.max_concurrent_var.get()
    
    def get_keep_iso(self) -> bool:
        """Get keep ISO setting."""
        return self.keep_iso_var.get()
    
    def get_preserve_structure(self) -> bool:
        """Get preserve structure setting."""
        return self.preserve_structure_var.get()
    
    def get_keep_extracted(self) -> bool:
        """Get keep extracted setting."""
        return self.keep_extracted_var.get()
    
    def get_delete_zip(self) -> bool:
        """Get delete ZIP setting."""
        return self.delete_zip_var.get()
