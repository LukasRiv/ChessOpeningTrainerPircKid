from src.board import Square, ChessBoard
from src.pieces import Piece, Pawn, Rook, Bishop, Knight, Queen, King

def main():
    """
    board = ChessBoard()

    # Récupère les objets Square pour les positions initiales
    square_white_rook = board.squares[2][3]  # Case (2, 3)
    square_black_queen = board.squares[5][3]  # Case (5, 3)

    # Crée les pièces en passant les objets Square
    white_rook = Rook('white', square_white_rook)
    black_queen = Queen('black', square_black_queen)

    print("Initial position:")
    board.display()

    try:
        # Récupère la case cible pour le déplacement
        target_square = board.squares[2][3]  # Case (4, 3)
        board.move_piece(black_queen, target_square)
        print("\nAfter moving the piece:")
        board.display()
    except ValueError as e:
        print(f"\nError: {e}")
    """

if __name__ == "__main__":
    main()