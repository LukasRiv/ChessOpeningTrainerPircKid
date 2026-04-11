from src.chessboard import ChessBoard
from src.pieces.pawn import Pawn
from src.pieces.rook import Rook
from src.pieces.bishop import Bishop
from src.pieces.knight import Knight

def main():
    board = ChessBoard()
    white_rook = Rook('white', (2, 3))
    black_knight = Knight('black', (4, 4))
    board.place_piece(white_rook)
    board.place_piece(black_knight)
    print("Initial position:")
    board.display()

    try:
        board.move_piece(black_knight, (2, 3))
        print("\nAfter moving the bishop:")
        board.display()
    except ValueError as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()

