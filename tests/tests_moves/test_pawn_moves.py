from src.board import ChessBoard
from src.pieces import Pawn, Rook

def test_pawn_moves():
    board = ChessBoard()

    # Place pieces on the board
    square_white_pawn = board.squares[1][0]  # White Pawn on A2
    square_black_pawn = board.squares[3][1]  # Black Pawn on B4
    square_white_rook = board.squares[1][1]  # White Rook on B2

    white_pawn = Pawn('white', square_white_pawn)
    black_pawn = Pawn('black', square_black_pawn)
    white_rook = Rook('white', square_white_rook)

    board.place_piece(white_pawn, square_white_pawn)
    board.place_piece(black_pawn, square_black_pawn)
    board.place_piece(white_rook, square_white_rook)

    white_pawn.update_valid_moves(board)
    black_pawn.update_valid_moves(board)
    white_rook.update_valid_moves(board)

    success = True

    # --- Test 1: Valid pawn move (white) ---
    print("\n--- Test 1: Valid pawn move (white) ---")
    print("Board before move:")
    board.display()
    try:
        target_square_white = board.squares[3][0]  # Square A4
        board.move_piece(white_pawn, target_square_white)
        print("\nBoard after move:")
        board.display()
        if target_square_white.piece != white_pawn:
            success = False
            print("Test 1 failed: White pawn was not moved correctly.")
        else:
            print("Test 1 passed: White pawn was moved correctly.")
    except ValueError as e:
        success = False
        print(f"Test 1 failed: Error moving white pawn: {e}")


    # --- Test 2: Valid pawn move (black) ---
    print("\n--- Test 2: Valid pawn move (black) ---")
    print("Board before move:")
    board.display()
    try:
        black_pawn.update_valid_moves(board)
        target_square_black = board.squares[2][0]  # Square A3
        board.move_piece(black_pawn, target_square_black)
        print("\nBoard after move:")
        board.display()
        if target_square_black.piece != black_pawn:
            success = False
            print("Test 2 failed: Black pawn was not moved correctly.")
        else:
            print("Test 2 passed: Black pawn was moved correctly.")
    except ValueError as e:
        success = False
        print(f"Test 2 failed: Error moving black pawn: {e}")


    # --- Test 3: Capture by black pawn ---
    print("\n--- Test 3: Capture by black pawn ---")
    print("Board before move:")
    board.display()
    try:
        board.move_piece(black_pawn, square_white_rook)
        print("\nBoard after move:")
        board.display()
        if square_white_rook.piece != black_pawn:
            success = False
            print("Test 3 failed: Black pawn did not capture the white rook correctly.")
        else:
            print("Test 3 passed: Black pawn captured the white rook correctly.")
    except ValueError as e:
        success = False
        print(f"Test 3 failed: Error during black pawn capture: {e}")

    if success:
        print("\n--- All pawn move and capture tests passed successfully. ---")
    else:
        print("\n--- Some tests failed. ---")

if __name__ == "__main__":
    test_pawn_moves()