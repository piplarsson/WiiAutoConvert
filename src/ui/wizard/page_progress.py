"""
Page 4: Conversion Progress
Execution dashboard with progress tracking and logs.
"""

import customtkinter as ctk
from pathlib import Path
from typing import Dict, Callable
from ..theme import COLORS, SPACING, FONTS
from ...conversion_engine import ConversionStatus


class PageProgress(ctk.CTkFrame):
    """Conversion progress page - execution dashboard."""
    
    def __init__(self, parent, on_cancel: Callable = None, on_watch: Callable = None):
        """
        Initialize progress page.
        
        Args:
            parent: Parent widget
            on_cancel: Cancel button callback
            on_watch: Watch mode button callback
        """
        super().__init__(parent, fg_color="transparent")
        
        # Status indicator - pack at top
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.pack(fill="x", side="top", anchor="n", pady=(0, SPACING["element_gap"]))
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Status: Idle",
            font=("Segoe UI", 20, "bold"),  # Increased from FONTS["title"] (18) to 20 for better visibility
            text_color=COLORS["text"],
            anchor="w"
        )
        self.status_label.pack(side="left", fill="x", expand=True)
        
        # Overall progress bar
        self.progress_bar = ctk.CTkProgressBar(
            status_frame,
            fg_color=COLORS["bg"],
            progress_color=COLORS["accent"],
            height=8
        )
        self.progress_bar.pack(side="right", padx=(SPACING["element_gap"], 0), fill="x", expand=False, ipadx=100)
        self.progress_bar.set(0)
        
        # Progress table card - pack at top with fixed height (reduced by half)
        table_card = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            border_color=COLORS["border"],
            border_width=SPACING["border_width"],
            corner_radius=SPACING["border_radius"]
        )
        table_card.pack(fill="x", side="top", anchor="n", pady=(0, SPACING["card_gap"]), ipady=60)
        
        table_content = ctk.CTkFrame(table_card, fg_color="transparent")
        table_content.pack(fill="both", expand=True, padx=SPACING["card_padding"], pady=SPACING["card_padding"])
        
        # Table label
        table_label = ctk.CTkLabel(
            table_content,
            text="File Progress:",
            font=("Segoe UI", 11),  # Increased from FONTS["body"] (9) to 11 for better readability
            text_color=COLORS["text"],
            anchor="w"
        )
        table_label.pack(fill="x", pady=(0, SPACING["element_gap"]))
        
        # Progress table
        table_frame = ctk.CTkFrame(
            table_content,
            fg_color=COLORS["bg"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=6
        )
        table_frame.pack(fill="both", expand=True)
        
        # Header row
        header_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=4, pady=4)
        
        file_header = ctk.CTkLabel(
            header_frame,
            text="File",
            font=("Segoe UI", 11),  # Increased from FONTS["body"] (9) to 11 for better readability
            text_color=COLORS["muted"],
            anchor="w",
            width=300
        )
        file_header.pack(side="left", padx=4)
        
        status_header = ctk.CTkLabel(
            header_frame,
            text="Status",
            font=("Segoe UI", 11),  # Increased from FONTS["body"] (9) to 11 for better readability
            text_color=COLORS["muted"],
            anchor="w",
            width=100
        )
        status_header.pack(side="left", padx=4)
        
        progress_header = ctk.CTkLabel(
            header_frame,
            text="Progress",
            font=("Segoe UI", 11),  # Increased from FONTS["body"] (9) to 11 for better readability
            text_color=COLORS["muted"],
            anchor="w"
        )
        progress_header.pack(side="left", padx=4, fill="x", expand=True)
        
        # Scrollable content
        self.progress_scroll = ctk.CTkScrollableFrame(
            table_frame,
            fg_color="transparent"
        )
        self.progress_scroll.pack(fill="both", expand=True, padx=4, pady=(0, 4))
        
        # Store progress items
        self._progress_items: Dict[str, Dict] = {}
        
        # Idle state
        self.idle_state = ctk.CTkLabel(
            self.progress_scroll,
            text="Waiting for files…",
            font=("Segoe UI", 11),  # Increased from FONTS["subtitle"] (9) to 11 for better readability
            text_color=COLORS["muted"],
            anchor="center"
        )
        self.idle_state.pack(expand=True, fill="both", pady=20)
        
        # Log card - pack at top with fixed height (reduced by half)
        log_card = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            border_color=COLORS["border"],
            border_width=SPACING["border_width"],
            corner_radius=SPACING["border_radius"]
        )
        log_card.pack(fill="x", side="top", anchor="n", ipady=75)
        
        log_content = ctk.CTkFrame(log_card, fg_color="transparent")
        log_content.pack(fill="both", expand=True, padx=SPACING["card_padding"], pady=SPACING["card_padding"])
        
        log_label = ctk.CTkLabel(
            log_content,
            text="Log Output:",
            font=("Segoe UI", 11),  # Increased from FONTS["body"] (9) to 11 for better readability
            text_color=COLORS["text"],
            anchor="w"
        )
        log_label.pack(fill="x", pady=(0, SPACING["element_gap"]))
        
        # Log text area (reduced height by half)
        self.log_text = ctk.CTkTextbox(
            log_content,
            fg_color=COLORS["bg"],
            border_color=COLORS["border"],
            border_width=0,
            text_color=COLORS["text"],
            font=("Consolas", 10),  # Increased from FONTS["mono"] (8) to 10 for better readability
            wrap="word",
            height=75
        )
        self.log_text.pack(fill="both", expand=True)
        
        # Action buttons (bottom)
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(fill="x", pady=(SPACING["card_gap"], 0))
        
        # Cancel button
        self.cancel_button = ctk.CTkButton(
            actions_frame,
            text="Cancel",
            command=on_cancel or (lambda: None),
            fg_color=COLORS["error"],
            hover_color=COLORS["error"],
            text_color=COLORS["text"],
            font=("Segoe UI", 11),  # Increased from FONTS["body"] (9) to 11 for better readability
            height=32,
            width=100,
            state="disabled"
        )
        self.cancel_button.pack(side="left")
        
        # Watch mode button
        if on_watch:
            self.watch_button = ctk.CTkButton(
                actions_frame,
                text="▢ Start Watch Mode",
                command=on_watch or (lambda: None),
                fg_color="transparent",
                border_color=COLORS["border"],
                border_width=1,
                hover_color=COLORS["border"],
                text_color=COLORS["text"],
                font=("Segoe UI", 11),  # Increased from FONTS["body"] (9) to 11 for better readability
                height=32,
                width=140
            )
            self.watch_button.pack(side="right")
        else:
            self.watch_button = None
    
    def update_progress(self, file_path: Path, status: ConversionStatus, message: str):
        """Update progress for a file."""
        if self.idle_state.winfo_viewable():
            self.idle_state.pack_forget()
        
        file_str = str(file_path)
        
        if file_str not in self._progress_items:
            # Create new row
            row_frame = ctk.CTkFrame(self.progress_scroll, fg_color="transparent")
            row_frame.pack(fill="x", padx=4, pady=2)
            
            file_label = ctk.CTkLabel(
                row_frame,
                text=file_str,
                font=("Consolas", 10),  # Increased from FONTS["mono"] (8) to 10 for better readability
                text_color=COLORS["text"],
                anchor="w",
                width=300,
                height=24
            )
            file_label.pack(side="left", padx=4, pady=2)
            
            status_label = ctk.CTkLabel(
                row_frame,
                text="",
                font=("Segoe UI", 11),  # Increased from FONTS["body"] (9) to 11 for better readability
                text_color=COLORS["text"],
                anchor="w",
                width=100
            )
            status_label.pack(side="left", padx=4)
            
            progress_label = ctk.CTkLabel(
                row_frame,
                text="",
                font=("Segoe UI", 11),  # Increased from FONTS["body"] (9) to 11 for better readability
                text_color=COLORS["text"],
                anchor="w"
            )
            progress_label.pack(side="left", padx=4, fill="x", expand=True)
            
            self._progress_items[file_str] = {
                "frame": row_frame,
                "status": status_label,
                "progress": progress_label
            }
        
        # Update status and progress
        item = self._progress_items[file_str]
        status_text = status.value if hasattr(status, 'value') else str(status)
        
        # Color code status
        if status == ConversionStatus.SUCCESS:
            status_color = COLORS["success"]
        elif status == ConversionStatus.FAILED:
            status_color = COLORS["error"]
        elif status == ConversionStatus.SKIPPED:
            status_color = COLORS["warning"]
        else:
            status_color = COLORS["text"]
        
        item["status"].configure(text=status_text, text_color=status_color)
        item["progress"].configure(text=message)
    
    def set_status(self, status: str, color: str = None):
        """Update status indicator."""
        if color is None:
            if status == "Converting":
                color = COLORS["accent"]
            elif status == "Watching":
                color = COLORS["success"]
            else:
                color = COLORS["text"]
        
        self.status_label.configure(text=f"Status: {status}", text_color=color)
    
    def set_progress(self, value: float):
        """Set overall progress (0.0 to 1.0)."""
        self.progress_bar.set(value)
    
    def log_message(self, message: str):
        """Add message to log."""
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
    
    def clear_progress(self):
        """Clear all progress items."""
        for item in self._progress_items.values():
            item["frame"].destroy()
        self._progress_items.clear()
        self.idle_state.pack(expand=True, fill="both", pady=20)
        self.progress_bar.set(0)
    
    def clear_log(self):
        """Clear log output."""
        self.log_text.delete("1.0", "end")
    
    def set_cancel_enabled(self, enabled: bool):
        """Enable/disable cancel button."""
        self.cancel_button.configure(state="normal" if enabled else "disabled")
    
    def set_watch_text(self, text: str, active: bool = False):
        """Update watch button."""
        if self.watch_button:
            self.watch_button.configure(
                text=text,
                fg_color=COLORS["success"] if active else "transparent"
            )

