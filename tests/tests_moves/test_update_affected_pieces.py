from src.board import ChessBoard
from src.pieces import Rook, Bishop, Knight, Pawn

def test_update_affected_pieces():
    board = ChessBoard()
    success = True

    # Place pieces on the board
    square_white_rook = board.squares[2][0]  # White Rook on A3
    square_black_rook = board.squares[5][7]  # Black Rook on H8
    square_white_bishop = board.squares[0][2]  # White Bishop on C1
    square_black_bishop = board.squares[7][6]  # Black Bishop on F8
    square_white_knight = board.squares[3][3]  # Knight on D4
    square_black_pawn = board.squares[6][1]  # Pawn on B5

    white_rook = Rook('white', square_white_rook)
    black_rook = Rook('black', square_black_rook)
    white_bishop = Bishop('white', square_white_bishop)
    black_bishop = Bishop('black', square_black_bishop)
    white_knight = Knight('white', square_white_knight)
    black_pawn = Pawn('black', square_black_pawn)

    white_rook.update_valid_moves(board)
    black_rook.update_valid_moves(board)
    white_bishop.update_valid_moves(board)
    black_bishop.update_valid_moves(board)
    white_knight.update_valid_moves(board)
    black_pawn.update_valid_moves(board)


    # --- Test 1: White Rook moved to free up diagonal for White Bishop ---
    # Move the White Rook to free up the diagonal for the White Bishop
    target_square = board.squares[5][0]  # Square A6
    board.move_piece(white_rook, target_square)

    # Check if White Bishop's valid moves are updated correctly
    expected_valid_moves_white_bishop = [
        board.squares[1][1],  # B2
        board.squares[2][0],  # A3
        board.squares[1][3],  # D2
        board.squares[2][4],  # E3
        board.squares[3][5],  # F4
        board.squares[4][6],  # G5
        board.squares[5][7],  # H6
    ]
    if all(square in white_bishop.valid_moves for square in expected_valid_moves_white_bishop):
        print("Test 1 passed: White Bishop's valid moves were updated correctly after the White Rook moved.")
    else:
        success = False
        print("Test 1 failed: White Bishop's valid moves were NOT updated correctly after the White Rook moved.")


    # --- Test 2: Black Pawn's valid moves updated after White Rook moved ---
    # Check if Black Pawn's valid moves are updated correctly
    expected_valid_moves_black_pawn = [
        board.squares[5][1],  # B4
        board.squares[4][1],  # A3
        board.squares[5][0],  # A6
    ]
    if all(square in black_pawn.valid_moves for square in expected_valid_moves_black_pawn):
        print("Test 2 passed: Black Pawn's valid moves were updated correctly after the White Rook moved.")
    else:
        success = False
        print("Test 2 failed: Black Pawn's valid moves were NOT updated correctly after the White Rook moved.")


    # --- Test 3: Black Bishop moved to check White Rook's valid moves ---
    # Move the Black Bishop to check if White Rook's valid moves are updated
    target_square = board.squares[5][4]  # Square E6
    board.move_piece(black_bishop, target_square)

    # Check if White Rook's valid moves are updated correctly
    expected_valid_moves_white_rook = [
        board.squares[0][0],  # A1
        board.squares[1][0],  # A2
        board.squares[2][0],  # A3
        board.squares[3][0],  # A4
        board.squares[4][0],  # A5
        board.squares[6][0],  # A7
        board.squares[7][0],  # A8
        board.squares[5][1],  # B6
        board.squares[5][2],  # C6
        board.squares[5][3],  # D6
        board.squares[5][4],  # E6
    ]
    if all(square in white_rook.valid_moves for square in expected_valid_moves_white_rook) and not any(
        square in white_rook.valid_moves for square in [board.squares[5][5], board.squares[5][6], board.squares[5][7]]
    ):
        print("Test 3 passed: White Rook's valid moves were updated correctly after the Black Bishop moved.")
    else:
        success = False
        print("Test 3 failed: White Rook's valid moves were NOT updated correctly after the Black Bishop moved.")


    # --- Test 4: White Rook captures Black Bishop ---
    # Move the White Rook to capture the Black Bishop
    target_square = board.squares[5][4]  # Square E6
    board.move_piece(white_rook, target_square)

    # Check if White Knight's valid moves are updated correctly
    expected_valid_moves_white_knight = [
        board.squares[4][5],  # F5
        board.squares[2][1],  # B3
        board.squares[1][2],  # C2
        board.squares[4][1],  # B5
        board.squares[1][4],  # E2
        board.squares[2][5],  # F3
        board.squares[5][2],  # C6
    ]
    if all(square in white_knight.valid_moves for square in expected_valid_moves_white_knight):
        print("Test 4 passed: White Knight's valid moves were updated correctly after the White Rook captured the Black Bishop.")
    else:
        success = False
        print("Test 4 failed: White Knight's valid moves were NOT updated correctly after the White Rook captured the Black Bishop.")


    # --- Test 5: Black Rook captures White Rook ---
    # Move the Black Rook to capture the White Rook
    target_square = board.squares[5][4]  # Square E6
    board.move_piece(black_rook, target_square)

    # Check if White Knight's valid moves are updated correctly
    expected_valid_moves_white_knight = [
        board.squares[4][5],  # F5
        board.squares[5][4],  # E6
        board.squares[2][1],  # B3
        board.squares[1][2],  # C2
        board.squares[4][1],  # B5
        board.squares[1][4],  # E2
        board.squares[2][5],  # F3
        board.squares[5][2],  # C6
    ]
    if all(square in white_knight.valid_moves for square in expected_valid_moves_white_knight):
        print("Test 5 passed: White Knight's valid moves were updated correctly after the Black Rook captured the White Rook.")
    else:
        success = False
        print("Test 5 failed: White Knight's valid moves were NOT updated correctly after the Black Rook captured the White Rook.")


    # --- Test 6: White Knight captures Black Rook ---
    # Move the White Knight to capture the Black Rook
    target_square_knight = board.squares[5][4]  # Square E6
    board.move_piece(white_knight, target_square_knight)

    # Check if White Knight's valid moves are updated correctly
    expected_valid_moves_white_knight = [
        board.squares[3][3],  # D4
        board.squares[3][5],  # F4
        board.squares[4][2],  # C5
        board.squares[4][6],  # F5
        board.squares[6][2],  # C7
        board.squares[6][6],  # G7
        board.squares[7][3],  # D8
        board.squares[7][5],  # F8
    ]
    if all(square in white_knight.valid_moves for square in expected_valid_moves_white_knight):
        print("Test 6 passed: White Knight's valid moves were updated correctly after the capture of the Black Rook.")
    else:
        success = False
        print("Test 6 failed: White Knight's valid moves were NOT updated correctly after the capture of the Black Rook.")


    if success:
        print("\nAll tests passed successfully!")
    else:
        print("\nSome tests failed.")


if __name__ == "__main__":
    test_update_affected_pieces()