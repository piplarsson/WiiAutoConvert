#!/usr/bin/env python3
"""
CLI Entry Point
Direct CLI access without GUI.
"""

import sys
from pathlib import Path

# Add project root to path so we can import src as a package
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.cli import main

if __name__ == "__main__":
    main()

