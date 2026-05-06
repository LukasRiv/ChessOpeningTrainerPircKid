import os
import pygame

# Initialize Pygame
pygame.init()

# --- DYNAMIC DIMENSIONS ---
# Get screen info to calculate responsive dimensions
screen_info = pygame.display.Info()
screen_height = screen_info.current_h

# Chess board dimensions (80% of screen height)
BOARD_SIZE = int(0.9 * screen_height)  # Total board size (8x8 squares)
SQUARE_SIZE = BOARD_SIZE // 8  # Size of a single square (BOARD_SIZE / 8)

# Sidebar dimensions (40% of screen height)
SIDEBAR_WIDTH = int(0.4 * screen_height)
WINDOW_WIDTH = BOARD_SIZE + SIDEBAR_WIDTH
WINDOW_HEIGHT = BOARD_SIZE

# Promotion window dimensions (proportional to SQUARE_SIZE)
PROMOTION_WINDOW_SIZE = int(BOARD_SIZE * 0.5)  # 50% of board size
PROMOTION_PIECE_SIZE = int(SQUARE_SIZE * 0.8)  # 80% of square size

# --- GAME CONSTANTS ---
FPS = 60  # Frames per second for the game loop
PROMOTION_PIECES = ["Queen", "Rook", "Bishop", "Knight"]  # Order for promotion window
DRAG_MOVE_THRESHOLD = 5  # Minimum pixels moved to consider it a drag

# --- COLORS ---
# Chess board colors
LIGHT_SQUARE = (240, 217, 181)  # Light brown for chess board
DARK_SQUARE = (181, 136, 99)    # Dark brown for chess board
HIGHLIGHT = (247, 247, 105, 128)  # Semi-transparent yellow for valid moves
SELECTED = (0, 255, 0, 128)      # Semi-transparent light green for selected piece
CAPTURE = (255, 0, 0, 128)       # Semi-transparent light red for capture moves

# Text and background colors
BLACK = (0, 0, 0)                # Black color for text
WHITE = (255, 255, 255)          # White color
SIDEBAR_BG = (40, 40, 40)        # Dark gray for sidebar background

# --- BUTTON STYLES (Chess.com-like) ---
# Button appearance
BUTTON_BG = (50, 50, 50)          # Dark gray background for buttons
BUTTON_BG_HOVER = (70, 70, 70)    # Lighter gray on hover
BUTTON_TEXT_COLOR = (220, 220, 220)  # Light gray text
BUTTON_BORDER_COLOR = (100, 100, 100)  # Border color
BUTTON_BORDER_RADIUS = 8          # Rounded corners for buttons
BUTTON_PADDING = 10               # Padding inside buttons
BUTTON_ICON_PADDING = 10          # Space between icon and text

# --- BUTTON POSITIONS ---
# Menu buttons dimensions and positions
MENU_BUTTON_WIDTH = SIDEBAR_WIDTH // 2  # Buttons width = half of sidebar width
MENU_BUTTON_X = BOARD_SIZE + (SIDEBAR_WIDTH - MENU_BUTTON_WIDTH) // 2  # Centered in sidebar
MENU_BUTTON_START_Y = 200  # Starting Y position for menu buttons

# Back button dimensions
BACK_BUTTON_WIDTH = 40  # Reduced width for Back button
BACK_BUTTON_HEIGHT = 40  # Square height for Back button

# Flip Board button dimensions and position
FLIP_BUTTON_SIZE = 40  # Square size for Flip Board button
FLIP_BUTTON_X = BOARD_SIZE + FLIP_BUTTON_SIZE - 20  # Right-aligned in sidebar
FLIP_BUTTON_Y = 20  # Top margin for Flip Board button
FLIP_BUTTON_ICON_PATH = "assets/icons/flip_board_icon.png"  # Use Unicode icon instead of image

# --- PGN DIRECTORY ---
# Path to the directory containing PGN files for openings
PGN_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "src", "trainers", "pgn")
# Debug: Print PGN directory path and existence
print(f"PGN_DIR: {PGN_DIR}, exists: {os.path.exists(PGN_DIR)}")

# Dropdown menu styles
DROPDOWN_BUTTON_HEIGHT = 30  # Height for dropdown buttons
DROPDOWN_SPACING = 5  # Vertical spacing between dropdown items

# --- HIERARCHICAL MENU STRUCTURE ---
# Tree structure for the hierarchical menu
MENU_TREE = {
    "Play": {
        "Free Play": None,
        "Game VS Bot": {
            "Home-Made AI": None,
            "Stockfish": None
        }
    },
    "Training": {
        "Opening Trainer": {
            "Random Opening": None,
            "Choose Opening": None  # PGN files will be loaded dynamically
        },
        "Analysis": {
            "Import ScreenShot": None,
            "Import PGN": None,
            "Import FEN": None
        },
    }
}