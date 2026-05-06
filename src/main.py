import sys
import os
from ui.old_chess_ui_pygame import ChessUI
from board.chessboard import ChessBoard

def main():
    """Main function to launch the Chess UI application."""
    # Initialize the chess board
    board = ChessBoard()
    board.setup_initial_position()

    # Create and run the UI
    ui = ChessUI(board)
    ui.run()

if __name__ == "__main__":
    # Add the project root to the Python path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    main()