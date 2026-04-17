from src.board import ChessBoard
from src.pieces import Rook, Pawn, Bishop

def test_rook_moves():
    board = ChessBoard()

    # Place pieces on the board
    square_white_rook = board.squares[0][0]    # White Rook on A1
    square_white_bishop = board.squares[6][2]  # White Bishop on C7
    square_black_rook = board.squares[5][3]    # Black Rook on D6
    square_black_pawn = board.squares[7][3]    # Black Pawn on D8

    white_rook = Rook('white', square_white_rook)
    white_bishop = Bishop('white', square_white_bishop)
    black_rook = Rook('black', square_black_rook)
    black_pawn = Pawn('black', square_black_pawn)

    board.place_piece(white_rook, square_white_rook)
    board.place_piece(white_bishop, square_white_bishop)
    board.place_piece(black_rook, square_black_rook)
    board.place_piece(black_pawn, square_black_pawn)

    white_rook.update_valid_moves(board)
    white_bishop.update_valid_moves(board)
    black_rook.update_valid_moves(board)
    black_pawn.update_valid_moves(board)

    success = True

    # --- Test 1: Valid rook move (white) ---
    print("\n--- Test 1: Valid rook move (white) ---")
    print("Board before move:")
    board.display()
    try:
        target_square_white = board.squares[0][3]  # Square D1
        board.move_piece(white_rook, target_square_white)
        print("\nBoard after move:")
        board.display()
        if target_square_white.piece != white_rook:
            success = False
            print("Test 1 failed: White rook was not moved correctly.")
        else:
            print("Test 1 passed: White rook was moved correctly.")
    except ValueError as e:
        success = False
        print(f"Test 1 failed: Error moving white rook: {e}")


    # --- Test 2: Valid rook move (black) ---
    print("\n--- Test 2: Valid rook move (black) ---")
    print("Board before move:")
    board.display()
    try:
        target_square_black = board.squares[5][1]  # Square B6
        board.move_piece(black_rook, target_square_black)
        print("\nBoard after move:")
        board.display()
        if target_square_black.piece != black_rook:
            success = False
            print("Test 2 failed: Black rook was not moved correctly.")
        else:
            print("Test 2 passed: Black rook was moved correctly.")
    except ValueError as e:
        success = False
        print(f"Test 2 failed: Error moving black rook: {e}")


    # --- Test 3: Capture by white rook ---
    print("\n--- Test 3: Capture by white rook ---")
    print("Board before move:")
    board.display()
    try:
        board.move_piece(white_rook, square_black_pawn)
        print("\nBoard after move:")
        board.display()
        if square_black_pawn.piece != white_rook:
            success = False
            print("Test 3 failed: White rook did not capture the black pawn correctly.")
        else:
            print("Test 3 passed: White rook captured the black pawn correctly.")
    except ValueError as e:
        success = False
        print(f"Test 3 failed: Error during white rook capture: {e}")

    if success:
        print("\n--- All rook move and capture tests passed successfully. ---")
    else:
        print("\n--- Some tests failed. ---")

if __name__ == "__main__":
    test_rook_moves()