"""
Page 3: Network & Advanced Options
Optional settings for network move and cleanup behavior.
"""

import tkinter as tk
import customtkinter as ctk
from typing import Callable
from ..theme import COLORS, SPACING, FONTS
from .wizard_controller import ConversionConfig


class _Tooltip:
    """Simple hover tooltip for CustomTkinter widgets."""

    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self.tip_window = None

        widget.bind("<Enter>", self._show, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _show(self, _event=None):
        if self.tip_window or not self.text:
            return

        x = self.widget.winfo_pointerx() + 14
        y = self.widget.winfo_pointery() + 14

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        try:
            tw.attributes("-topmost", True)
        except Exception:
            pass
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            tw,
            text=self.text,
            justify="left",
            padx=8,
            pady=5,
            bg=COLORS["card"],
            fg=COLORS["text"],
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 9),
            wraplength=420,
        )
        label.pack()

    def _hide(self, _event=None):
        if self.tip_window is not None:
            self.tip_window.destroy()
            self.tip_window = None


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
        self._tooltips = []

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
            font=("Segoe UI", 11),
            text_color=COLORS["muted"],
            anchor="w"
        )
        section1_label.pack(fill="x", pady=(0, 4))

        section1_hint = ctk.CTkLabel(
            content,
            text="Network-only settings below unlock when 'Enable network move' is turned on.",
            font=FONTS["subtitle"],
            text_color=COLORS["muted"],
            anchor="w"
        )
        section1_hint.pack(fill="x", pady=(0, 6))

        # Enable network move
        self.enable_network_var = ctk.BooleanVar(value=self.config.enable_network_move)
        self.enable_network_cb = ctk.CTkCheckBox(
            content,
            text="Enable network move",
            variable=self.enable_network_var,
            command=self._on_network_toggle,
            font=("Segoe UI", 11),
            text_color=COLORS["text"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            checkbox_width=18,
            checkbox_height=18
        )
        self.enable_network_cb.pack(anchor="w", pady=(0, 4))

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
        self.keep_local_cb = ctk.CTkCheckBox(
            content,
            text="Keep local copy (copy instead of move)",
            variable=self.keep_local_var,
            command=self._on_option_change,
            font=("Segoe UI", 11),
            text_color=COLORS["text"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            checkbox_width=18,
            checkbox_height=18
        )
        self.keep_local_cb.pack(anchor="w", pady=(0, SPACING["element_gap"]))

        # Separator
        separator1 = ctk.CTkFrame(content, fg_color=COLORS["border"], height=1)
        separator1.pack(fill="x", pady=SPACING["element_gap"])

        # ====================================================================
        # Section 2: Transfer Behavior
        # ====================================================================

        section2_label = ctk.CTkLabel(
            content,
            text="Transfer Behavior:",
            font=("Segoe UI", 11),
            text_color=COLORS["muted"],
            anchor="w"
        )
        section2_label.pack(fill="x", pady=(SPACING["element_gap"], 4))

        # Overwrite
        overwrite_frame = ctk.CTkFrame(content, fg_color="transparent")
        overwrite_frame.pack(fill="x", pady=(0, 4))

        self.overwrite_label = ctk.CTkLabel(
            overwrite_frame,
            text="Overwrite:",
            font=("Segoe UI", 11),
            text_color=COLORS["text"],
            width=120
        )
        self.overwrite_label.pack(side="left", padx=(0, SPACING["element_gap"]))

        self.overwrite_var = ctk.StringVar(value=self.config.overwrite_mode)
        self.overwrite_combo = ctk.CTkComboBox(
            overwrite_frame,
            values=["skip", "append_timestamp", "append_version", "overwrite"],
            variable=self.overwrite_var,
            command=self._on_option_change,
            font=("Segoe UI", 11),
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
        self.overwrite_combo.pack(side="left", fill="x", expand=True)

        # Retries
        retries_frame = ctk.CTkFrame(content, fg_color="transparent")
        retries_frame.pack(fill="x", pady=(0, 4))

        self.retries_label = ctk.CTkLabel(
            retries_frame,
            text="Retries:",
            font=("Segoe UI", 11),
            text_color=COLORS["text"],
            width=120
        )
        self.retries_label.pack(side="left", padx=(0, SPACING["element_gap"]))

        self.retries_var = ctk.StringVar(value=str(self.config.retries))
        self.retries_entry = ctk.CTkEntry(
            retries_frame,
            textvariable=self.retries_var,
            width=100,
            fg_color=COLORS["bg"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            font=("Segoe UI", 11),
            height=28
        )
        self.retries_entry.pack(side="left")
        self.retries_entry.bind("<KeyRelease>", lambda e: self._on_option_change())

        # Max concurrent
        concurrent_frame = ctk.CTkFrame(content, fg_color="transparent")
        concurrent_frame.pack(fill="x", pady=(0, SPACING["element_gap"]))

        self.concurrent_label = ctk.CTkLabel(
            concurrent_frame,
            text="Max Concurrent:",
            font=("Segoe UI", 11),
            text_color=COLORS["text"],
            width=120
        )
        self.concurrent_label.pack(side="left", padx=(0, SPACING["element_gap"]))

        self.max_concurrent_var = ctk.StringVar(value=str(self.config.max_concurrent))
        self.concurrent_entry = ctk.CTkEntry(
            concurrent_frame,
            textvariable=self.max_concurrent_var,
            width=100,
            fg_color=COLORS["bg"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            font=("Segoe UI", 11),
            height=28
        )
        self.concurrent_entry.pack(side="left", padx=(0, SPACING["element_gap"]))
        self.concurrent_entry.bind("<KeyRelease>", lambda e: self._on_option_change())

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
            font=("Segoe UI", 11),
            text_color=COLORS["muted"],
            anchor="w"
        )
        section3_label.pack(fill="x", pady=(SPACING["element_gap"], 4))

        # Delete after network move
        self.delete_after_move_var = ctk.BooleanVar(value=self.config.cleanup.delete_after_network_move)
        self.delete_after_cb = ctk.CTkCheckBox(
            content,
            text="Delete local files (input ZIP and output WBFS) after successful network move",
            variable=self.delete_after_move_var,
            command=self._on_option_change,
            font=("Segoe UI", 11),
            text_color=COLORS["text"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            checkbox_width=18,
            checkbox_height=18
        )
        self.delete_after_cb.pack(anchor="w", pady=(0, 3))

        # Keep ISO
        self.keep_iso_var = ctk.BooleanVar(value=self.config.cleanup.keep_iso)
        self.keep_iso_cb = ctk.CTkCheckBox(
            content,
            text="Keep intermediate ISO files",
            variable=self.keep_iso_var,
            command=self._on_option_change,
            font=("Segoe UI", 11),
            text_color=COLORS["text"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            checkbox_width=18,
            checkbox_height=18
        )
        self.keep_iso_cb.pack(anchor="w", pady=(0, 3))

        # Preserve structure
        self.preserve_structure_var = ctk.BooleanVar(value=self.config.cleanup.preserve_structure)
        self.preserve_structure_cb = ctk.CTkCheckBox(
            content,
            text="Preserve directory structure",
            variable=self.preserve_structure_var,
            command=self._on_option_change,
            font=("Segoe UI", 11),
            text_color=COLORS["text"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            checkbox_width=18,
            checkbox_height=18
        )
        self.preserve_structure_cb.pack(anchor="w", pady=(0, 3))

        # Keep extracted
        self.keep_extracted_var = ctk.BooleanVar(value=self.config.cleanup.keep_extracted)
        self.keep_extracted_cb = ctk.CTkCheckBox(
            content,
            text="Keep extracted RVZ files from ZIP",
            variable=self.keep_extracted_var,
            command=self._on_option_change,
            font=("Segoe UI", 11),
            text_color=COLORS["text"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            checkbox_width=18,
            checkbox_height=18
        )
        self.keep_extracted_cb.pack(anchor="w", pady=(0, 3))

        # Delete ZIP
        self.delete_zip_var = ctk.BooleanVar(value=self.config.cleanup.delete_zip)
        self.delete_zip_cb = ctk.CTkCheckBox(
            content,
            text="Delete original ZIP files after conversion",
            variable=self.delete_zip_var,
            command=self._on_option_change,
            font=("Segoe UI", 11),
            text_color=COLORS["text"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            checkbox_width=18,
            checkbox_height=18
        )
        self.delete_zip_cb.pack(anchor="w")

        self._install_tooltips()
        self._sync_network_dependent_controls()
        self._on_option_change()

    def _attach_tooltip(self, widget, text: str):
        self._tooltips.append(_Tooltip(widget, text))

    def _install_tooltips(self):
        """Attach explanatory tooltips to options that can be misunderstood."""
        self._attach_tooltip(
            self.enable_network_cb,
            "After conversion, move or copy the finished WBFS files to another destination. "
            "This unlocks the network-only options below."
        )
        self._attach_tooltip(
            self.network_entry,
            "Target folder used for the final network transfer. Ignored for local-only conversions."
        )
        self._attach_tooltip(
            self.keep_local_cb,
            "When enabled, the app copies files to the network destination and keeps the local WBFS copy. "
            "This is disabled automatically when 'Delete local files after successful network move' is on."
        )
        self._attach_tooltip(
            self.overwrite_label,
            "Controls what happens if a file with the same name already exists at the network destination. "
            "Only applies when Network Move is enabled."
        )
        self._attach_tooltip(
            self.overwrite_combo,
            "Controls what happens if a file with the same name already exists at the network destination. "
            "Only applies when Network Move is enabled."
        )
        self._attach_tooltip(
            self.retries_label,
            "How many times the app retries a failed network transfer. Only applies when Network Move is enabled."
        )
        self._attach_tooltip(
            self.retries_entry,
            "How many times the app retries a failed network transfer. Only applies when Network Move is enabled."
        )
        self._attach_tooltip(
            self.concurrent_label,
            "Maximum number of conversions processed at once. This affects the conversion engine itself, "
            "not just network transfers."
        )
        self._attach_tooltip(
            self.concurrent_entry,
            "Maximum number of conversions processed at once. This affects the conversion engine itself, "
            "not just network transfers."
        )
        self._attach_tooltip(
            self.delete_after_cb,
            "After a successful network move, delete the local ZIP input and local WBFS output. "
            "When this is enabled, 'Keep local copy' is turned off because those options conflict."
        )
        self._attach_tooltip(
            self.keep_iso_cb,
            "Keep the temporary ISO created during RVZ conversion. If left off, the ISO is cleaned up automatically "
            "after a successful conversion."
        )
        self._attach_tooltip(
            self.preserve_structure_cb,
            "Keep the organized output folder layout, for example 'Game Title [GAMEID]\\GAMEID.wbfs'."
        )
        self._attach_tooltip(
            self.keep_extracted_cb,
            "If a ZIP archive contains RVZ files, keep the extracted RVZ files after conversion instead of cleaning them up."
        )
        self._attach_tooltip(
            self.delete_zip_cb,
            "For local conversions, original ZIP files are deleted automatically after a successful conversion. "
            "This checkbox only changes ZIP deletion behavior for network-move workflows."
        )

    def _set_widget_enabled(self, widget, enabled: bool):
        """Enable or disable a widget safely."""
        try:
            widget.configure(state="normal" if enabled else "disabled")
        except Exception:
            pass

    def _sync_network_dependent_controls(self):
        """Keep network-only widgets visually and functionally in sync."""
        network_enabled = self.enable_network_var.get()
        delete_after_enabled = network_enabled and self.delete_after_move_var.get()

        self._set_widget_enabled(self.network_entry, network_enabled)
        self._set_widget_enabled(self.overwrite_combo, network_enabled)
        self._set_widget_enabled(self.retries_entry, network_enabled)
        self._set_widget_enabled(self.delete_after_cb, network_enabled)
        self._set_widget_enabled(self.delete_zip_cb, network_enabled)

        if delete_after_enabled:
            self.keep_local_var.set(False)
        self._set_widget_enabled(self.keep_local_cb, network_enabled and not delete_after_enabled)

        active_label = COLORS["text"] if network_enabled else COLORS["muted"]
        self.overwrite_label.configure(text_color=active_label)
        self.retries_label.configure(text_color=active_label)

    def _on_network_toggle(self):
        """Handle network enable toggle."""
        enabled = self.enable_network_var.get()
        self.config.enable_network_move = enabled
        self._sync_network_dependent_controls()
        self._on_option_change()

    def _on_network_path_change(self):
        """Handle network path change."""
        self.config.network_path = self.network_path_var.get()
        self._on_option_change()

    def _on_option_change(self, *_args):
        """Update config from UI."""
        self._sync_network_dependent_controls()

        self.config.enable_network_move = self.enable_network_var.get()
        self.config.network_path = self.network_path_var.get()
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
