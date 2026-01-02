"""
Progress Card Component
Progress table and log output display.
"""

import customtkinter as ctk
from pathlib import Path
from typing import Dict
from .base_card import BaseCard
from ..theme import COLORS, SPACING, FONTS
from ...conversion_engine import ConversionStatus


class ProgressCard(BaseCard):
    """Progress card for displaying conversion progress and logs."""
    
    def __init__(self, parent):
        """Initialize the progress card."""
        super().__init__(parent, "Progress")
        
        # Progress table section
        progress_label = ctk.CTkLabel(
            self.content_frame,
            text="Conversion Progress:",
            font=FONTS["body"],
            text_color=COLORS["text"],
            anchor="w"
        )
        progress_label.pack(fill="x", pady=(0, SPACING["element_gap"]))
        
        # Progress table using scrollable frame with custom styling
        progress_table_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=COLORS["bg"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=6
        )
        progress_table_frame.pack(fill="both", expand=False, pady=(0, SPACING["element_gap"]), ipady=2)
        
        # Header row
        header_frame = ctk.CTkFrame(progress_table_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=3, pady=2)
        
        file_header = ctk.CTkLabel(
            header_frame,
            text="File",
            font=FONTS["body"],
            text_color=COLORS["muted"],
            anchor="w",
            width=300
        )
        file_header.pack(side="left", padx=4)
        
        status_header = ctk.CTkLabel(
            header_frame,
            text="Status",
            font=FONTS["body"],
            text_color=COLORS["muted"],
            anchor="w",
            width=100
        )
        status_header.pack(side="left", padx=4)
        
        progress_header = ctk.CTkLabel(
            header_frame,
            text="Progress",
            font=FONTS["body"],
            text_color=COLORS["muted"],
            anchor="w",
            width=200
        )
        progress_header.pack(side="left", padx=4, fill="x", expand=True)
        
        # Scrollable content area with fixed height
        self.progress_scroll = ctk.CTkScrollableFrame(
            progress_table_frame,
            fg_color="transparent",
            height=100  # Fixed height for progress table
        )
        self.progress_scroll.pack(fill="both", expand=False, padx=3, pady=(0, 2))
        
        # Store progress items
        self._progress_items: Dict[str, ctk.CTkFrame] = {}
        
        # Idle state overlay
        self.idle_state_label = ctk.CTkLabel(
            self.progress_scroll,
            text="Waiting for files…",
            font=FONTS["subtitle"],
            text_color=COLORS["muted"],
            anchor="center"
        )
        self.idle_state_label.pack(expand=True, fill="both", pady=20)
        
        # Log section
        log_label = ctk.CTkLabel(
            self.content_frame,
            text="Log Output:",
            font=FONTS["body"],
            text_color=COLORS["text"],
            anchor="w"
        )
        log_label.pack(fill="x", pady=(SPACING["element_gap"], SPACING["element_gap"]))
        
        # Log text area with fixed height
        log_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=COLORS["bg"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=6
        )
        log_frame.pack(fill="both", expand=True)
        
        # Use Text widget with custom styling (CTkTextbox not available in older versions)
        self.log_text = ctk.CTkTextbox(
            log_frame,
            fg_color=COLORS["bg"],
            border_color=COLORS["border"],
            border_width=0,
            text_color=COLORS["text"],
            font=FONTS["mono"],
            wrap="word",
            height=120  # Fixed height for log area
        )
        self.log_text.pack(fill="both", expand=False, padx=3, pady=3)
    
    def update_progress(self, file_path: Path, status: ConversionStatus, message: str):
        """Update progress display for a file."""
        # Hide idle state if visible
        if self.idle_state_label.winfo_viewable():
            self.idle_state_label.pack_forget()
        
        file_str = str(file_path)
        
        # Get or create progress item
        if file_str not in self._progress_items:
            # Create new row
            row_frame = ctk.CTkFrame(self.progress_scroll, fg_color="transparent")
            row_frame.pack(fill="x", padx=3, pady=1)
            
            # Use monospaced font for file paths and increase row height
            file_label = ctk.CTkLabel(
                row_frame,
                text=file_str,
                font=FONTS["mono"],
                text_color=COLORS["text"],
                anchor="w",
                width=300,
                height=24  # Increased row height
            )
            file_label.pack(side="left", padx=4, pady=2)
            
            status_label = ctk.CTkLabel(
                row_frame,
                text="",
                font=FONTS["body"],
                text_color=COLORS["text"],
                anchor="w",
                width=100
            )
            status_label.pack(side="left", padx=4)
            
            progress_label = ctk.CTkLabel(
                row_frame,
                text="",
                font=FONTS["body"],
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
    
    def clear_progress(self):
        """Clear all progress items."""
        for item in self._progress_items.values():
            item["frame"].destroy()
        self._progress_items.clear()
        # Show idle state
        self.idle_state_label.pack(expand=True, fill="both", pady=20)
    
    def log_message(self, message: str):
        """Add message to log display."""
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
    
    def clear_log(self):
        """Clear log output."""
        self.log_text.delete("1.0", "end")

