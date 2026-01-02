"""
Base Card Component
Common functionality for all card components.
"""

import customtkinter as ctk
from ..theme import COLORS, SPACING


class BaseCard(ctk.CTkFrame):
    """
    Base class for all card components.
    Provides consistent styling and structure.
    """
    
    def __init__(self, parent, title: str = None):
        """
        Initialize the base card.
        
        Args:
            parent: Parent widget
            title: Optional card title (not used in modern design, kept for compatibility)
        """
        super().__init__(
            parent,
            fg_color=COLORS["card"],
            border_color=COLORS["border"],
            border_width=SPACING["border_width"],
            corner_radius=SPACING["border_radius"]
        )
        
        # Internal padding - content frame for child widgets
        self.content_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.content_frame.pack(fill="both", expand=True, padx=SPACING["card_padding"], pady=SPACING["card_padding"])

