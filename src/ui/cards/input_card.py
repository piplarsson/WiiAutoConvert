"""
Input Card Component
File and folder selection interface.
"""

import customtkinter as ctk
from typing import List, Callable
from .base_card import BaseCard
from ..theme import COLORS, SPACING, FONTS


class InputCard(BaseCard):
    """Input card for selecting RVZ files, ZIP files, and folders."""
    
    def __init__(
        self,
        parent,
        on_add_files: Callable = None,
        on_add_folder: Callable = None,
        on_remove_selected: Callable = None,
        on_clear_all: Callable = None
    ):
        """Initialize the input card."""
        super().__init__(parent, "Input Files")
        
        # Label
        label = ctk.CTkLabel(
            self.content_frame,
            text="RVZ Files / ZIP Files / Folders:",
            font=FONTS["body"],
            text_color=COLORS["text"],
            anchor="w"
        )
        label.pack(fill="x", pady=(0, SPACING["element_gap"]))
        
        # Listbox frame with scrollbar
        listbox_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        listbox_frame.pack(fill="both", expand=False, pady=(0, SPACING["element_gap"]))
        
        # Scrollable listbox using CTkScrollableFrame with fixed height
        self.listbox = ctk.CTkScrollableFrame(
            listbox_frame,
            fg_color=COLORS["bg"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=6,
            height=80  # Reduced height for file list (from 120)
        )
        self.listbox.pack(fill="both", expand=False)
        
        # Store file labels for selection tracking
        self._file_labels: List[ctk.CTkLabel] = []
        self._selected_indices: List[int] = []
        
        # Empty state label
        self.empty_state_label = ctk.CTkLabel(
            self.listbox,
            text="Drop RVZ / ZIP files here",
            font=FONTS["subtitle"],
            text_color=COLORS["muted"],
            anchor="center"
        )
        self.empty_state_label.pack(expand=True, fill="both", pady=20)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        buttons_frame.pack(fill="x")
        
        # Add Files button - PRIMARY (accent color)
        add_files_btn = ctk.CTkButton(
            buttons_frame,
            text="Add Files",
            command=on_add_files or (lambda: None),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            text_color=COLORS["bg"],
            font=FONTS["body"],
            height=28
        )
        add_files_btn.pack(side="left", padx=(0, SPACING["element_gap"]))
        
        # Add Folder button - SECONDARY (muted accent)
        muted_accent = "#1a8fa3"  # Slightly muted accent
        add_folder_btn = ctk.CTkButton(
            buttons_frame,
            text="Add Folder",
            command=on_add_folder or (lambda: None),
            fg_color=muted_accent,
            hover_color=COLORS["accent"],
            text_color=COLORS["bg"],
            font=FONTS["body"],
            height=28
        )
        add_folder_btn.pack(side="left", padx=(0, SPACING["element_gap"]))
        
        # Remove Selected button - OUTLINE
        remove_btn = ctk.CTkButton(
            buttons_frame,
            text="Remove Selected",
            command=on_remove_selected or (lambda: None),
            fg_color="transparent",
            border_color=COLORS["border"],
            border_width=1,
            hover_color=COLORS["border"],
            text_color=COLORS["text"],
            font=FONTS["body"],
            height=28
        )
        remove_btn.pack(side="left", padx=(0, SPACING["element_gap"]))
        
        # Clear All button - OUTLINE + RED HOVER
        clear_btn = ctk.CTkButton(
            buttons_frame,
            text="Clear All",
            command=on_clear_all or (lambda: None),
            fg_color="transparent",
            border_color=COLORS["border"],
            border_width=1,
            hover_color=COLORS["error"],
            text_color=COLORS["text"],
            font=FONTS["body"],
            height=28
        )
        clear_btn.pack(side="left")
    
    def add_file(self, file_path: str):
        """Add a file to the list."""
        # Hide empty state if visible
        if self.empty_state_label.winfo_viewable():
            self.empty_state_label.pack_forget()
        
        # Create label for file
        file_label = ctk.CTkLabel(
            self.listbox,
            text=file_path,
            font=FONTS["mono"],
            text_color=COLORS["text"],
            anchor="w",
            cursor="hand2"
        )
        file_label.pack(fill="x", padx=4, pady=1)
        
        # Bind click for selection
        def on_click(event, idx=len(self._file_labels)):
            self._toggle_selection(idx)
        
        file_label.bind("<Button-1>", on_click)
        self._file_labels.append(file_label)
    
    def _toggle_selection(self, idx: int):
        """Toggle selection of an item."""
        if idx in self._selected_indices:
            self._selected_indices.remove(idx)
            self._file_labels[idx].configure(text_color=COLORS["text"])
        else:
            self._selected_indices.append(idx)
            self._file_labels[idx].configure(text_color=COLORS["accent"])
    
    def get_selected_indices(self) -> List[int]:
        """Get list of selected indices."""
        return self._selected_indices.copy()
    
    def remove_item(self, idx: int):
        """Remove an item from the list."""
        if 0 <= idx < len(self._file_labels):
            self._file_labels[idx].destroy()
            self._file_labels.pop(idx)
            # Update selected indices
            self._selected_indices = [i if i < idx else i - 1 for i in self._selected_indices if i != idx]
            # Rebind all labels with updated indices
            for i, label in enumerate(self._file_labels):
                label.unbind("<Button-1>")
                label.bind("<Button-1>", lambda e, idx=i: self._toggle_selection(idx))
    
    def clear_all(self):
        """Clear all items from the list."""
        for label in self._file_labels:
            label.destroy()
        self._file_labels.clear()
        self._selected_indices.clear()
        # Show empty state
        self.empty_state_label.pack(expand=True, fill="both", pady=20)

