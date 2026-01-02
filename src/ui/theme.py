"""
Theme Configuration
Centralized colors, spacing, and styling constants for the modern UI.
"""

# ============================================================================
# COLOR PALETTE
# ============================================================================

COLORS = {
    "bg": "#0e1117",           # Root window background (darkest)
    "card": "#161b22",         # Card background (slightly lighter)
    "border": "#2a2f3a",       # Border color (soft contrast)
    "accent": "#22d3ee",       # Teal/cyan accent color
    "text": "#e5e7eb",         # Primary text color
    "muted": "#9ca3af",        # Muted/secondary text
    "success": "#10b981",      # Success state (green)
    "error": "#ef4444",        # Error state (red)
    "warning": "#f59e0b",      # Warning state (orange)
}

# ============================================================================
# SPACING & SIZING
# ============================================================================

SPACING = {
    "card_padding": 10,        # Internal padding for cards (reduced from 16)
    "card_gap": 8,             # Gap between cards (reduced from 12)
    "element_gap": 6,          # Gap between elements within cards (reduced from 8)
    "border_radius": 8,        # Rounded corner radius (reduced from 12)
    "border_width": 1,         # Border width
}

# ============================================================================
# TYPOGRAPHY
# ============================================================================

FONTS = {
    "title": ("Segoe UI", 18, "bold"),    # Increased from 16 for better weight
    "subtitle": ("Segoe UI", 9),          # Reduced from 11
    "body": ("Segoe UI", 9),              # Reduced from 10
    "mono": ("Consolas", 8),              # Reduced from 9
    "badge": ("Segoe UI", 8, "bold"),    # For status badges
}

# ============================================================================
# CUSTOMTKINTER THEME CONFIGURATION
# ============================================================================

def configure_theme():
    """
    Configure customtkinter theme settings.
    Must be called before creating any customtkinter widgets.
    """
    import customtkinter as ctk
    
    # Set appearance mode (dark only)
    ctk.set_appearance_mode("dark")
    
    # Set color theme (we'll use custom colors via widget configuration)
    ctk.set_default_color_theme("blue")  # Base theme, we override colors
    
    # Configure default widget colors
    ctk.set_widget_scaling(1.0)
    ctk.set_window_scaling(1.0)

