from src.board import ChessBoard
from src.pieces import Rook, Pawn

def test_rook_moves():
    board = ChessBoard()

    # Place rooks and a pawn on the board
    square_white_rook = board.squares[0][0]
    square_black_rook = board.squares[5][3]
    square_black_pawn = board.squares[7][3]

    white_rook = Rook('white', square_white_rook)
    black_rook = Rook('black', square_black_rook)
    black_pawn = Pawn('black', square_black_pawn)

    success = True

    # Test valid rook move (white)
    try:
        target_square_white = board.squares[0][3]
        board.move_piece(white_rook, target_square_white)
        if target_square_white.piece != white_rook:
            success = False
            print("White rook was not moved correctly.")
        else:
            print("White rook was moved correctly.")
    except ValueError as e:
        success = False
        print(f"Error moving white rook: {e}")

    # Test valid rook move (black)
    try:
        target_square_black = board.squares[5][1]
        board.move_piece(black_rook, target_square_black)
        if target_square_black.piece != black_rook:
            success = False
            print("Black rook was not moved correctly.")
        else:
            print("Black rook was moved correctly.")
    except ValueError as e:
        success = False
        print(f"Error moving black rook: {e}")

    # Test capture by black rook
    try:
        board.move_piece(white_rook, square_black_pawn)
        if square_black_pawn.piece != white_rook:
            success = False
            print("White rook did not capture the black pawn correctly.")
        else:
            print("White rook captured the black pawn correctly.")
    except ValueError as e:
        success = False
        print(f"Error during black rook capture: {e}")

    if success:
        print("All rook move and capture tests passed successfully.")

if __name__ == "__main__":
    test_rook_moves()