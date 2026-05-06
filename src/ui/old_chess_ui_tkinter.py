import tkinter as tk
from src.board.chessboard import ChessBoard

class ChessUI:
    """UI for the chess application using Tkinter."""

    def __init__(self, root, chessboard):
        self.root = root
        self.chessboard = chessboard
        self.selected_piece = None
        self.selected_square = None
        self.square_size = 100

        self.root.title("Chess Opening Trainer - Pirc/KID")
        self.canvas = tk.Canvas(root, width=800, height=800)
        self.canvas.pack()

        self.piece_symbols = {
            'white_pawn': '♙', 'black_pawn': '♟',
            'white_rook': '♖', 'black_rook': '♜',
            'white_knight': '♘', 'black_knight': '♞',
            'white_bishop': '♗', 'black_bishop': '♝',
            'white_queen': '♕', 'black_queen': '♛',
            'white_king': '♔', 'black_king': '♚',
        }

        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_click)

    def draw_board(self):
        """Draw the chess board and pieces on the canvas."""
        self.canvas.delete("all")
        for row in reversed(range(8)):  # Inverse l'ordre des rangées
            for col in range(8):
                x1 = col * self.square_size
                y1 = (7 - row) * self.square_size  # Ajuste la position Y
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                color = "white" if (row + col) % 2 == 0 else "gray"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags=f"square_{row}_{col}")

                square = self.chessboard.squares[row][col]
                piece = square.piece
                if piece:
                    symbol = self._get_piece_symbol(piece)
                    self.canvas.create_text(
                        x1 + self.square_size // 2, y1 + self.square_size // 2,
                        text=symbol, font=("Arial", 60), tags=f"piece_{row}_{col}"
                    )

    def _get_piece_symbol(self, piece):
        """Return the Unicode symbol for the given piece."""
        color = "white" if piece.color == "white" else "black"
        piece_type = piece.__class__.__name__.lower()
        return self.piece_symbols.get(f"{color}_{piece_type}", "?")

    def on_click(self, event):
        """Handle click events on the chess board."""
        col = event.x // self.square_size
        row = 7 - (event.y // self.square_size)  # Inverse la rangée

        if 0 <= row < 8 and 0 <= col < 8:
            square = self.chessboard.squares[row][col]
            piece = square.piece

            if self.selected_square is None:
                if piece:
                    self.selected_square = square
                    self.selected_piece = piece
                    print(f"Selected: {piece} at ({row}, {col})")
            else:
                if square == self.selected_square:
                    self.selected_square = None
                    self.selected_piece = None
                else:
                    try:
                        self.chessboard.move_piece(self.selected_piece, square)
                        print(f"Moved {self.selected_piece} to ({row}, {col})")
                        self.selected_square = None
                        self.selected_piece = None
                        self.draw_board()
                    except ValueError as e:
                        print(f"Invalid move: {e}")
                        self.selected_square = None
                        self.selected_piece = None

if __name__ == "__main__":
    root = tk.Tk()
    chessboard = ChessBoard()
    chessboard.setup_initial_position()
    app = ChessUI(root, chessboard)
    root.mainloop()