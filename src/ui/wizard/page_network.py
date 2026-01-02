"""
Page 3: Network & Advanced Options
Optional settings for network move and cleanup behavior.
"""

import customtkinter as ctk
from typing import Callable
from ..theme import COLORS, SPACING, FONTS
from .wizard_controller import ConversionConfig


class PageNetwork(ctk.CTkFrame):
    """Network and advanced options page."""
    
    def __init__(self, parent, config: ConversionConfig, on_update: Callable = None):
        """
        Initialize network page.
        
        Args:
            parent: Parent widget
            config: Conversion configuration state
            on_update: Callback when options change
        """
        super().__init__(parent, fg_color="transparent")
        
        self.config = config
        self.on_update = on_update
        
        # Page title - pack at top
        title = ctk.CTkLabel(
            self,
            text="Optional: What happens after conversion?",
            font=FONTS["title"],
            text_color=COLORS["text"],
            anchor="w"
        )
        title.pack(fill="x", side="top", anchor="n", pady=(0, SPACING["element_gap"]))
        
        # Options card - pack at top, don't expand vertically
        options_card = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            border_color=COLORS["border"],
            border_width=SPACING["border_width"],
            corner_radius=SPACING["border_radius"]
        )
        options_card.pack(fill="x", side="top", anchor="n")
        
        content = ctk.CTkFrame(options_card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=SPACING["card_padding"], pady=SPACING["card_padding"])
        
        # ====================================================================
        # Section 1: Network Move (Optional)
        # ====================================================================
        
        section1_label = ctk.CTkLabel(
            content,
            text="Network Move (Optional):",
            font=("Segoe UI", 11),  # Increased from FONTS["body"] (9) to 11 for better readability
            text_color=COLORS["muted"],
            anchor="w"
        )
        section1_label.pack(fill="x", pady=(0, 4))
        
        # Enable network move
        self.enable_network_var = ctk.BooleanVar(value=self.config.enable_network_move)
        enable_network_cb = ctk.CTkCheckBox(
            content,
            text="Enable network move",
            variable=self.enable_network_var,
            command=self._on_network_toggle,
            font=("Segoe UI", 11),  # Increased from FONTS["body"] (9) to 11 for better readability
            text_color=COLORS["text"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            checkbox_width=18,
            checkbox_height=18
        )
        enable_network_cb.pack(anchor="w", pady=(0, 4))
        
        # Network path (disabled unless enabled)
        self.network_path_var = ctk.StringVar(value=self.config.network_path)
        self.network_entry = ctk.CTkEntry(
            content,
            textvariable=self.network_path_var,
            fg_color=COLORS["bg"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            font=FONTS["mono"],
            height=28,
            state="disabled"
        )
        self.network_entry.pack(fill="x", pady=(0, 4))
        self.network_entry.bind("<KeyRelease>", lambda e: self._on_network_path_change())
        
        # Keep local copy
        self.keep_local_var = ctk.BooleanVar(value=self.config.keep_local_copy)
        keep_local_cb = ctk.CTkCheckBox(
            content,
            text="Keep local copy (copy instead of move)",
            variable=self.keep_local_var,
            command=self._on_option_change,
            font=("Segoe UI", 11),  # Increased from FONTS["body"] (9) to 11 for better readability
            text_color=COLORS["text"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            checkbox_width=18,
            checkbox_height=18
        )
        keep_local_cb.pack(anchor="w", pady=(0, SPACING["element_gap"]))
        
        # Separator
        separator1 = ctk.CTkFrame(content, fg_color=COLORS["border"], height=1)
        separator1.pack(fill="x", pady=SPACING["element_gap"])
        
        # ====================================================================
        # Section 2: Transfer Behavior
        # ====================================================================
        
        section2_label = ctk.CTkLabel(
            content,
            text="Transfer Behavior:",
            font=("Segoe UI", 11),  # Increased from FONTS["body"] (9) to 11 for better readability
            text_color=COLORS["muted"],
            anchor="w"
        )
        section2_label.pack(fill="x", pady=(SPACING["element_gap"], 4))
        
        # Overwrite
        overwrite_frame = ctk.CTkFrame(content, fg_color="transparent")
        overwrite_frame.pack(fill="x", pady=(0, 4))
        
        overwrite_label = ctk.CTkLabel(
            overwrite_frame,
            text="Overwrite:",
            font=("Segoe UI", 11),  # Increased from FONTS["body"] (9) to 11 for better readability
            text_color=COLORS["text"],
            width=120
        )
        overwrite_label.pack(side="left", padx=(0, SPACING["element_gap"]))
        
        self.overwrite_var = ctk.StringVar(value=self.config.overwrite_mode)
        overwrite_combo = ctk.CTkComboBox(
            overwrite_frame,
            values=["skip", "append_timestamp", "append_version", "overwrite"],
            variable=self.overwrite_var,
            command=self._on_option_change,
            font=("Segoe UI", 11),  # Increased from FONTS["body"] (9) to 11 for better readability
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
        retries_frame = ctk.CTkFrame(content, fg_color="transparent")
        retries_frame.pack(fill="x", pady=(0, 4))
        
        retries_label = ctk.CTkLabel(
            retries_frame,
            text="Retries:",
            font=("Segoe UI", 11),  # Increased from FONTS["body"] (9) to 11 for better readability
            text_color=COLORS["text"],
            width=120
        )
        retries_label.pack(side="left", padx=(0, SPACING["element_gap"]))
        
        self.retries_var = ctk.StringVar(value=str(self.config.retries))
        retries_entry = ctk.CTkEntry(
            retries_frame,
            textvariable=self.retries_var,
            width=100,
            fg_color=COLORS["bg"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            font=("Segoe UI", 11),  # Increased from FONTS["body"] (9) to 11 for better readability
            height=28
        )
        retries_entry.pack(side="left")
        retries_entry.bind("<KeyRelease>", lambda e: self._on_option_change())
        
        # Max concurrent
        concurrent_frame = ctk.CTkFrame(content, fg_color="transparent")
        concurrent_frame.pack(fill="x", pady=(0, SPACING["element_gap"]))
        
        concurrent_label = ctk.CTkLabel(
            concurrent_frame,
            text="Max Concurrent:",
            font=("Segoe UI", 11),  # Increased from FONTS["body"] (9) to 11 for better readability
            text_color=COLORS["text"],
            width=120
        )
        concurrent_label.pack(side="left", padx=(0, SPACING["element_gap"]))
        
        self.max_concurrent_var = ctk.StringVar(value=str(self.config.max_concurrent))
        concurrent_entry = ctk.CTkEntry(
            concurrent_frame,
            textvariable=self.max_concurrent_var,
            width=100,
            fg_color=COLORS["bg"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            font=("Segoe UI", 11),  # Increased from FONTS["body"] (9) to 11 for better readability
            height=28
        )
        concurrent_entry.pack(side="left", padx=(0, SPACING["element_gap"]))
        concurrent_entry.bind("<KeyRelease>", lambda e: self._on_option_change())
        
        concurrent_hint = ctk.CTkLabel(
            concurrent_frame,
            text="(1 recommended for USB HDD)",
            font=FONTS["subtitle"],
            text_color=COLORS["muted"]
        )
        concurrent_hint.pack(side="left")
        
        # Separator
        separator2 = ctk.CTkFrame(content, fg_color=COLORS["border"], height=1)
        separator2.pack(fill="x", pady=SPACING["element_gap"])
        
        # ====================================================================
        # Section 3: Cleanup Options
        # ====================================================================
        
        section3_label = ctk.CTkLabel(
            content,
            text="Cleanup Options:",
            font=("Segoe UI", 11),  # Increased from FONTS["body"] (9) to 11 for better readability
            text_color=COLORS["muted"],
            anchor="w"
        )
        section3_label.pack(fill="x", pady=(SPACING["element_gap"], 4))
        
        # Delete after network move
        self.delete_after_move_var = ctk.BooleanVar(value=self.config.cleanup.delete_after_network_move)
        delete_after_cb = ctk.CTkCheckBox(
            content,
            text="Delete local files (input ZIP and output WBFS) after successful network move",
            variable=self.delete_after_move_var,
            command=self._on_option_change,
            font=("Segoe UI", 11),  # Increased from FONTS["body"] (9) to 11 for better readability
            text_color=COLORS["text"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            checkbox_width=18,
            checkbox_height=18
        )
        delete_after_cb.pack(anchor="w", pady=(0, 3))
        
        # Keep ISO
        self.keep_iso_var = ctk.BooleanVar(value=self.config.cleanup.keep_iso)
        keep_iso_cb = ctk.CTkCheckBox(
            content,
            text="Keep intermediate ISO files",
            variable=self.keep_iso_var,
            command=self._on_option_change,
            font=("Segoe UI", 11),  # Increased from FONTS["body"] (9) to 11 for better readability
            text_color=COLORS["text"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            checkbox_width=18,
            checkbox_height=18
        )
        keep_iso_cb.pack(anchor="w", pady=(0, 3))
        
        # Preserve structure
        self.preserve_structure_var = ctk.BooleanVar(value=self.config.cleanup.preserve_structure)
        preserve_structure_cb = ctk.CTkCheckBox(
            content,
            text="Preserve directory structure",
            variable=self.preserve_structure_var,
            command=self._on_option_change,
            font=("Segoe UI", 11),  # Increased from FONTS["body"] (9) to 11 for better readability
            text_color=COLORS["text"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            checkbox_width=18,
            checkbox_height=18
        )
        preserve_structure_cb.pack(anchor="w", pady=(0, 3))
        
        # Keep extracted
        self.keep_extracted_var = ctk.BooleanVar(value=self.config.cleanup.keep_extracted)
        keep_extracted_cb = ctk.CTkCheckBox(
            content,
            text="Keep extracted RVZ files from ZIP",
            variable=self.keep_extracted_var,
            command=self._on_option_change,
            font=("Segoe UI", 11),  # Increased from FONTS["body"] (9) to 11 for better readability
            text_color=COLORS["text"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            checkbox_width=18,
            checkbox_height=18
        )
        keep_extracted_cb.pack(anchor="w", pady=(0, 3))
        
        # Delete ZIP
        self.delete_zip_var = ctk.BooleanVar(value=self.config.cleanup.delete_zip)
        delete_zip_cb = ctk.CTkCheckBox(
            content,
            text="Delete original ZIP files after conversion",
            variable=self.delete_zip_var,
            command=self._on_option_change,
            font=("Segoe UI", 11),  # Increased from FONTS["body"] (9) to 11 for better readability
            text_color=COLORS["text"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            checkbox_width=18,
            checkbox_height=18
        )
        delete_zip_cb.pack(anchor="w")
    
    def _on_network_toggle(self):
        """Handle network enable toggle."""
        enabled = self.enable_network_var.get()
        self.config.enable_network_move = enabled
        self.network_entry.configure(state="normal" if enabled else "disabled")
        self._on_option_change()
    
    def _on_network_path_change(self):
        """Handle network path change."""
        self.config.network_path = self.network_path_var.get()
        self._on_option_change()
    
    def _on_option_change(self):
        """Update config from UI."""
        self.config.keep_local_copy = self.keep_local_var.get()
        self.config.overwrite_mode = self.overwrite_var.get()
        try:
            self.config.retries = int(self.retries_var.get() or "3")
        except ValueError:
            self.config.retries = 3
        try:
            self.config.max_concurrent = int(self.max_concurrent_var.get() or "1")
        except ValueError:
            self.config.max_concurrent = 1
        
        self.config.cleanup.delete_after_network_move = self.delete_after_move_var.get()
        self.config.cleanup.keep_iso = self.keep_iso_var.get()
        self.config.cleanup.preserve_structure = self.preserve_structure_var.get()
        self.config.cleanup.keep_extracted = self.keep_extracted_var.get()
        self.config.cleanup.delete_zip = self.delete_zip_var.get()
        
        if self.on_update:
            self.on_update()
    
    def is_valid(self) -> bool:
        """Page is always valid (all options are optional)."""
        return True

