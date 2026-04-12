from src.board import ChessBoard
from src.pieces import Pawn, Rook

def test_pawn_moves():
    board = ChessBoard()

    # Place pawns and a rook on the board
    square_white_pawn = board.squares[1][0]
    square_black_pawn = board.squares[3][1]
    square_white_rook = board.squares[1][1]

    white_pawn = Pawn('white', square_white_pawn)
    black_pawn = Pawn('black', square_black_pawn)
    white_rook = Rook('white', square_white_rook)

    success = True

    # Test valid pawn move (white)
    try:
        target_square_white = board.squares[3][0]
        board.move_piece(white_pawn, target_square_white)
        if target_square_white.piece != white_pawn:
            success = False
            print("White pawn was not moved correctly.")
        else:
            print("White pawn was moved correctly.")
    except ValueError as e:
        success = False
        print(f"Error moving white pawn: {e}")

    # Test valid pawn move (black)
    try:
        target_square_black = board.squares[2][0]
        board.move_piece(black_pawn, target_square_black)
        if target_square_black.piece != black_pawn:
            success = False
            print("Black pawn was not moved correctly.")
        else:
            print("Black pawn captured the white pawn en passant correctly.")
    except ValueError as e:
        success = False
        print(f"Error moving black pawn: {e}")

    # Test capture by black pawn
    try:
        board.move_piece(black_pawn, square_white_rook)
        if square_white_rook.piece != black_pawn:
            success = False
            print("Black pawn did not capture the white rook correctly.")
        else:
            print("Black pawn captured the white rook correctly.")
    except ValueError as e:
        success = False
        print(f"Error during black pawn capture: {e}")

    if success:
        print("All pawn move and capture tests passed successfully.")

if __name__ == "__main__":
    test_pawn_moves()