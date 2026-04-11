from src.chessboard import ChessBoard
from src.pieces.pawn import Pawn
from src.pieces.rook import Rook
from src.pieces.knight import Knight
from src.pieces.bishop import Bishop
from src.pieces.queen import Queen
from src.pieces.king import King

def main():
    board = ChessBoard()
    white_rook = Rook('white', (2, 3))
    black_queen = Queen('black', (5, 3))
    board.place_piece(white_rook)
    board.place_piece(black_queen)
    print("Initial position:")
    board.display()

    try:
        board.move_piece(black_queen, (4, 2))
        print("\nAfter moving the piece:")
        board.display()
    except ValueError as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()

