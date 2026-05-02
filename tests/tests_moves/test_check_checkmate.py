from src.board import ChessBoard
from src.pieces import King, Rook, Bishop, Knight, Queen, Pawn

def test_check_detection():
    """Test the check detection logic for the chess board.

    Tests include:
    - Putting the opponent's king in check with different pieces (Rook, Bishop, Knight).
    - Preventing a player from putting their own king in check.
    """
    board = ChessBoard()
    success = True

    # --- Test 1: Put black king in check with a white rook ---
    print("\n--- Test 1: Black king in check (Rook attacks) ---")
    board = ChessBoard()
    square_black_king = board.squares[7][4]  # Black king at E8
    square_white_rook = board.squares[0][0]  # White rook at A1
    square_white_king = board.squares[0][7]  # White king at H1
    square_white_queen = board.squares[0][6]  # White queen at G1

    black_king = King('black', square_black_king)
    white_rook = Rook('white', square_white_rook)
    white_king = King('white', square_white_king)
    white_queen = Queen('white', square_white_queen)

    board.place_piece(black_king, square_black_king)
    board.place_piece(white_rook, square_white_rook)
    board.place_piece(white_king, square_white_king)
    board.place_piece(white_queen, square_white_queen)

    black_king.update_valid_moves(board)
    white_rook.update_valid_moves(board)

    print("Board before move:")
    board.display()

    try:
        # Move white rook to A8 to attack black king at E8
        target_square = board.squares[7][0]  # A8
        board.move_piece(white_rook, target_square)
        print("\nBoard after move:")
        board.display()

        if board.is_check and board.check_color == 'black':
            print("Test 1 passed: Black king is in check.")
        else:
            success = False
            print("Test 1 failed: Black king should be in check.")
    except ValueError as e:
        success = False
        print(f"Test 1 failed: {e}")

    # --- Test 2: Prevent putting own king in check ---
    print("\n--- Test 2: Cannot put own king in check ---")
    board = ChessBoard()
    square_white_king = board.squares[0][4]  # White king at E1
    square_white_rook = board.squares[0][0]  # White rook at A1
    square_black_rook = board.squares[0][7]  # Black rook at H1

    white_king = King('white', square_white_king)
    white_rook = Rook('white', square_white_rook)
    black_rook = Rook('black', square_black_rook)

    board.place_piece(white_king, square_white_king)
    board.place_piece(white_rook, square_white_rook)
    board.place_piece(black_rook, square_black_rook)

    white_king.update_valid_moves(board)
    white_rook.update_valid_moves(board)
    black_rook.update_valid_moves(board)

    print("Board before move:")
    board.display()

    try:
        # Try to move white rook to F1, which would expose white king at E1 to black rook at H1
        target_square = board.squares[0][5]  # F1
        board.move_piece(white_rook, target_square)
        print("\nBoard after move:")
        board.display()
        success = False
        print("Test 2 failed: Should not be able to put own king in check.")
    except ValueError as e:
        print(f"Test 2 passed: {e}")

    # --- Test 3: Put white king in check with a black bishop ---
    print("\n--- Test 3: White king in check (Bishop attacks) ---")
    board = ChessBoard()
    square_white_king = board.squares[0][4]  # White king at E1
    square_black_bishop = board.squares[5][5]  # Black bishop at F6

    white_king = King('white', square_white_king)
    black_bishop = Bishop('black', square_black_bishop)

    board.place_piece(white_king, square_white_king)
    board.place_piece(black_bishop, square_black_bishop)

    white_king.update_valid_moves(board)
    black_bishop.update_valid_moves(board)

    print("Board before move:")
    board.display()

    try:
        # Move black bishop to C3 to attack white king at E1
        target_square = board.squares[2][2]  # C3
        board.move_piece(black_bishop, target_square)
        print("\nBoard after move:")
        board.display()

        if board.is_check and board.check_color == 'white':
            print("Test 3 passed: White king is in check.")
        else:
            success = False
            print("Test 3 failed: White king should be in check.")
    except ValueError as e:
        success = False
        print(f"Test 3 failed: {e}")

    # --- Test 4: Put white king in check with a black knight ---
    print("\n--- Test 4: White king in check (Knight attacks) ---")
    board = ChessBoard()
    square_white_king = board.squares[0][4]  # White king at E1
    square_black_knight = board.squares[3][7]  # Black knight at H4

    white_king = King('white', square_white_king)
    black_knight = Knight('black', square_black_knight)

    board.place_piece(white_king, square_white_king)
    board.place_piece(black_knight, square_black_knight)

    white_king.update_valid_moves(board)
    black_knight.update_valid_moves(board)

    print("Board before move:")
    board.display()

    try:
        # Move black knight to F2 to attack white king at E1
        target_square = board.squares[1][6]  # G2
        board.move_piece(black_knight, target_square)
        print("\nBoard after move:")
        board.display()

        if board.is_check and board.check_color == 'white':
            print("Test 4 passed: White king is in check.")
        else:
            success = False
            print("Test 4 failed: White king should be in check.")
    except ValueError as e:
        success = False
        print(f"Test 4 failed: {e}")

    # --- Test 5: Prevent putting own king in check with a pawn ---
    print("\n--- Test 5: Cannot put own king in check (Pawn move) ---")
    board = ChessBoard()
    square_white_king = board.squares[1][4]  # White king at E2
    square_white_pawn = board.squares[1][3]  # White pawn at D2
    square_black_rook = board.squares[1][2]  # Black rook at C2

    white_king = King('white', square_white_king)
    white_pawn = Pawn('white', square_white_pawn)
    black_rook = Rook('black', square_black_rook)

    board.place_piece(white_king, square_white_king)
    board.place_piece(white_pawn, square_white_pawn)
    board.place_piece(black_rook, square_black_rook)

    white_king.update_valid_moves(board)
    white_pawn.update_valid_moves(board)
    black_rook.update_valid_moves(board)

    print("Board before move:")
    board.display()

    try:
        # Try to move white pawn to D3, which would expose white king at E2 to black rook at C2
        target_square = board.squares[2][3]  # D3
        board.move_piece(white_pawn, target_square)
        print("\nBoard after move:")
        board.display()
        success = False
        print("Test 5 failed: Should not be able to put own king in check.")
    except ValueError as e:
        print(f"Test 5 passed: {e}")

    if success:
        print("\n--- All check tests passed successfully! ---")
    else:
        print("\n--- Some tests failed. ---")

if __name__ == "__main__":
    test_check_detection()