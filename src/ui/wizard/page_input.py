"""
Page 1: Input Selection
Large drag-and-drop area for selecting files/folders.
"""

import customtkinter as ctk
from pathlib import Path
from typing import List, Callable
from ..theme import COLORS, SPACING, FONTS
from .wizard_controller import ConversionConfig


class PageInput(ctk.CTkFrame):
    """Input selection page with large drag-drop area."""
    
    def __init__(self, parent, config: ConversionConfig, on_update: Callable = None):
        """
        Initialize input page.
        
        Args:
            parent: Parent widget
            config: Conversion configuration state
            on_update: Callback when input changes (for validation)
        """
        super().__init__(parent, fg_color="transparent")
        
        self.config = config
        self.on_update = on_update
        
        # Page title - pack at top with no top padding
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", side="top", anchor="n", pady=(0, SPACING["element_gap"]))
        
        title = ctk.CTkLabel(
            title_frame,
            text="What do you want to convert?",
            font=FONTS["title"],
            text_color=COLORS["text"],
            anchor="w"
        )
        title.pack(side="left")
        
        # Large drag-and-drop area - pack at top with fixed height
        drop_area = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            border_color=COLORS["border"],
            border_width=2,
            corner_radius=SPACING["border_radius"]
        )
        drop_area.pack(fill="x", side="top", anchor="n", pady=(0, SPACING["card_gap"]), ipady=80)
        
        # Drop area content
        drop_content = ctk.CTkFrame(drop_area, fg_color="transparent")
        drop_content.pack(expand=True, fill="both", padx=SPACING["card_padding"], pady=SPACING["card_padding"])
        
        # Large icon/text
        drop_icon = ctk.CTkLabel(
            drop_content,
            text="📁",
            font=("Segoe UI", 48),
            text_color=COLORS["muted"]
        )
        drop_icon.pack(pady=(20, 10))
        
        drop_text = ctk.CTkLabel(
            drop_content,
            text="Drop RVZ / ZIP files or folders here",
            font=FONTS["body"],
            text_color=COLORS["muted"]
        )
        drop_text.pack(pady=(0, 20))
        
        # Action buttons
        buttons_frame = ctk.CTkFrame(drop_content, fg_color="transparent")
        buttons_frame.pack()
        
        add_files_btn = ctk.CTkButton(
            buttons_frame,
            text="Add Files",
            command=self._add_files,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent"],
            text_color=COLORS["bg"],
            font=FONTS["body"],
            height=36,
            width=140
        )
        add_files_btn.pack(side="left", padx=SPACING["element_gap"])
        
        add_folder_btn = ctk.CTkButton(
            buttons_frame,
            text="Add Folder",
            command=self._add_folder,
            fg_color="#1a8fa3",  # Muted accent
            hover_color=COLORS["accent"],
            text_color=COLORS["bg"],
            font=FONTS["body"],
            height=36,
            width=140
        )
        add_folder_btn.pack(side="left", padx=SPACING["element_gap"])
        
        # File list below - pack at top
        list_label = ctk.CTkLabel(
            self,
            text="Selected Files:",
            font=FONTS["title"],  # Increased from "body" to "title" for bigger text
            text_color=COLORS["text"],
            anchor="w"
        )
        list_label.pack(fill="x", side="top", anchor="n", pady=(0, SPACING["element_gap"]))
        
        # File list container - pack at top
        list_container = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=SPACING["border_radius"]
        )
        list_container.pack(fill="x", side="top", anchor="n", pady=(0, SPACING["card_gap"]))
        
        # Scrollable file list
        self.file_list = ctk.CTkScrollableFrame(
            list_container,
            fg_color=COLORS["bg"],
            height=150
        )
        self.file_list.pack(fill="both", expand=True, padx=4, pady=4)
        
        # Store file labels
        self._file_labels: List[ctk.CTkLabel] = []
        self._selected_indices: List[int] = []
        
        # Empty state
        self.empty_state = ctk.CTkLabel(
            self.file_list,
            text="No files selected",
            font=FONTS["subtitle"],
            text_color=COLORS["muted"],
            anchor="center"
        )
        self.empty_state.pack(expand=True, fill="both", pady=20)
        
        # List actions
        list_actions = ctk.CTkFrame(list_container, fg_color="transparent")
        list_actions.pack(fill="x", padx=4, pady=4)
        
        remove_btn = ctk.CTkButton(
            list_actions,
            text="Remove Selected",
            command=self._remove_selected,
            fg_color="transparent",
            border_color=COLORS["border"],
            border_width=1,
            hover_color=COLORS["border"],
            text_color=COLORS["text"],
            font=FONTS["body"],
            height=28
        )
        remove_btn.pack(side="left", padx=(0, SPACING["element_gap"]))
        
        clear_btn = ctk.CTkButton(
            list_actions,
            text="Clear All",
            command=self._clear_all,
            fg_color="transparent",
            border_color=COLORS["border"],
            border_width=1,
            hover_color=COLORS["error"],
            text_color=COLORS["text"],
            font=FONTS["body"],
            height=28
        )
        clear_btn.pack(side="left")
    
    def _add_files(self):
        """Add files via file dialog."""
        from tkinter import filedialog
        
        files = filedialog.askopenfilenames(
            title="Select RVZ or ZIP Files",
            filetypes=[
                ("RVZ and ZIP files", "*.rvz *.RVZ *.zip *.ZIP"),
                ("RVZ files", "*.rvz *.RVZ"),
                ("ZIP files", "*.zip *.ZIP"),
                ("All files", "*.*")
            ]
        )
        
        for file_path in files:
            path = Path(file_path)
            if path not in self.config.input_items:
                self.config.input_items.append(path)
                self._add_file_to_list(str(path))
        
        self._update_validation()
    
    def _add_folder(self):
        """Add folder via directory dialog."""
        from tkinter import filedialog
        
        folder = filedialog.askdirectory(title="Select Folder with RVZ Files")
        if folder:
            path = Path(folder)
            if path not in self.config.input_items:
                self.config.input_items.append(path)
                self._add_file_to_list(str(path))
        
        self._update_validation()
    
    def _add_file_to_list(self, file_path: str):
        """Add a file to the list display."""
        if self.empty_state.winfo_viewable():
            self.empty_state.pack_forget()
        
        file_label = ctk.CTkLabel(
            self.file_list,
            text=file_path,
            font=FONTS["mono"],
            text_color=COLORS["text"],
            anchor="w",
            cursor="hand2"
        )
        file_label.pack(fill="x", padx=4, pady=2)
        
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
    
    def _remove_selected(self):
        """Remove selected items."""
        for idx in reversed(sorted(self._selected_indices)):
            if 0 <= idx < len(self._file_labels):
                self._file_labels[idx].destroy()
                self._file_labels.pop(idx)
                if idx < len(self.config.input_items):
                    self.config.input_items.pop(idx)
        
        self._selected_indices.clear()
        self._rebind_labels()
        
        if not self._file_labels:
            self.empty_state.pack(expand=True, fill="both", pady=20)
        
        self._update_validation()
    
    def _clear_all(self):
        """Clear all items."""
        for label in self._file_labels:
            label.destroy()
        self._file_labels.clear()
        self._selected_indices.clear()
        self.config.input_items.clear()
        self.empty_state.pack(expand=True, fill="both", pady=20)
        self._update_validation()
    
    def _rebind_labels(self):
        """Rebind click handlers after removal."""
        for i, label in enumerate(self._file_labels):
            label.unbind("<Button-1>")
            label.bind("<Button-1>", lambda e, idx=i: self._toggle_selection(idx))
    
    def _update_validation(self):
        """Update validation state."""
        if self.on_update:
            self.on_update()
    
    def is_valid(self) -> bool:
        """Check if page is valid (has at least one input)."""
        return len(self.config.input_items) > 0

