# constants.py
"""
Game constants for the Snake project.

This module defines basic configuration values used throughout the game.
It intentionally avoids importing optional dependencies such as pygame
to keep the import lightweight and allow unit tests to run in environments
without a graphical subsystem.
"""

# Screen dimensions
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600

# Game update frequency (frames per second)
FPS: int = 30

# Additional constants can be added here as needed
# e.g., colors, initial snake length, food size, etc.