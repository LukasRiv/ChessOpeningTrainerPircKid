from src.board import ChessBoard
from src.pieces import Queen, Pawn

def test_queen_moves():
    board = ChessBoard()

    # Place queens and a pawn on the board
    square_white_queen = board.squares[0][3]
    square_black_queen = board.squares[3][3]
    square_black_pawn = board.squares[4][2]

    white_queen = Queen('white', square_white_queen)
    black_queen = Queen('black', square_black_queen)
    black_pawn = Pawn('black', square_black_pawn)

    success = True

    # Test valid queen move (white)
    try:
        target_square_white = board.squares[0][6]
        board.move_piece(white_queen, target_square_white)
        if target_square_white.piece != white_queen:
            success = False
            print("White queen was not moved correctly.")
        else:
            print("White queen was moved correctly.")
    except ValueError as e:
        success = False
        print(f"Error moving white queen: {e}")

    # Test valid queen move (black)
    try:
        target_square_black = board.squares[7][3]
        board.move_piece(black_queen, target_square_black)
        if target_square_black.piece != black_queen:
            success = False
            print("Black queen was not moved correctly.")
        else:
            print("Black queen was moved correctly.")
    except ValueError as e:
        success = False
        print(f"Error moving black queen: {e}")

    # Test capture by black queen
    try:
        board.move_piece(white_queen, square_black_pawn)
        if square_black_pawn.piece != white_queen:
            success = False
            print("White queen did not capture the black pawn correctly.")
        else:
            print("White queen captured the black pawn correctly.")
    except ValueError as e:
        success = False
        print(f"Error during black queen capture: {e}")

    if success:
        print("All queen move and capture tests passed successfully.")

if __name__ == "__main__":
    test_queen_moves()