from src.board import ChessBoard
from src.pieces import Bishop, Pawn

def test_bishop_moves():
    board = ChessBoard()

    # Place pieces on the board
    square_white_bishop = board.squares[0][2]  # White Bishop on C1
    square_black_bishop = board.squares[4][2]  # Black Bishop on C5
    square_black_pawn = board.squares[7][5]    # Black Pawn on F8

    white_bishop = Bishop('white', square_white_bishop)
    black_bishop = Bishop('black', square_black_bishop)
    black_pawn = Pawn('black', square_black_pawn)

    board.place_piece(white_bishop, square_white_bishop)
    board.place_piece(black_bishop, square_black_bishop)
    board.place_piece(black_pawn, square_black_pawn)

    white_bishop.update_valid_moves(board)
    black_bishop.update_valid_moves(board)
    black_pawn.update_valid_moves(board)

    success = True

    # --- Test 1: Valid bishop move (white) ---
    print("\n--- Test 1: Valid bishop move (white) ---")
    print("Board before move:")
    board.display()
    try:
        target_square_white = board.squares[2][0]  # Square A3
        board.move_piece(white_bishop, target_square_white)
        print("\nBoard after move:")
        board.display()
        if target_square_white.piece != white_bishop:
            success = False
            print("Test 1 failed: White bishop was not moved correctly.")
        else:
            print("Test 1 passed: White bishop was moved correctly.")
    except ValueError as e:
        success = False
        print(f"Test 1 failed: Error moving white bishop: {e}")


    # --- Test 2: Valid bishop move (black) ---
    print("\n--- Test 2: Valid bishop move (black) ---")
    print("Board before move:")
    board.display()
    try:
        target_square_black = board.squares[3][3]  # Square D4
        board.move_piece(black_bishop, target_square_black)
        print("\nBoard after move:")
        board.display()
        if target_square_black.piece != black_bishop:
            success = False
            print("Test 2 failed: Black bishop was not moved correctly.")
        else:
            print("Test 2 passed: Black bishop was moved correctly.")
    except ValueError as e:
        success = False
        print(f"Test 2 failed: Error moving black bishop: {e}")


    # --- Test 3: Capture by white bishop ---
    print("\n--- Test 3: Capture by white bishop ---")
    print("Board before move:")
    board.display()
    try:
        board.move_piece(white_bishop, square_black_pawn)
        print("\nBoard after move:")
        board.display()
        if square_black_pawn.piece != white_bishop:
            success = False
            print("Test 3 failed: White bishop did not capture the black pawn correctly.")
        else:
            print("Test 3 passed: White bishop captured the black pawn correctly.")
    except ValueError as e:
        success = False
        print(f"Test 3 failed: Error during white bishop capture: {e}")

    if success:
        print("\n--- All bishop move and capture tests passed successfully. ---")
    else:
        print("\n--- Some tests failed. ---")

if __name__ == "__main__":
    test_bishop_moves()