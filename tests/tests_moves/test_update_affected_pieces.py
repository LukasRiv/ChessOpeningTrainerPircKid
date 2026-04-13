from src.board import ChessBoard
from src.pieces import Rook, Bishop, Knight, Queen

def test_update_affected_pieces():
    board = ChessBoard()

    # Place pieces on the board
    square_white_rook = board.squares[2][0]  # White Rook on A3
    square_black_rook = board.squares[5][7]  # Black Rook H8
    square_white_bishop = board.squares[0][2]  # White Bishop on C1
    square_black_bishop = board.squares[7][6]  # Black Bishop on F8
    square_white_knight = board.squares[3][3]  # Cavalier en D4

    white_rook = Rook('white', square_white_rook)
    black_rook = Rook('black', square_black_rook)
    white_bishop = Bishop('white', square_white_bishop)
    black_bishop = Bishop('black', square_black_bishop)
    white_knight = Knight('white', square_white_knight)

    white_rook.update_valid_moves(board)
    black_rook.update_valid_moves(board)
    white_bishop.update_valid_moves(board)
    black_bishop.update_valid_moves(board)
    white_knight.update_valid_moves(board)


    # Move the White Rook to free up the diagonal for the White Bishop
    target_square = board.squares[5][0]  # Case A6
    board.move_piece(white_rook, target_square)

    # Expected White Bishop's valid moves updated after White Rook's move
    expected_valid_moves_white_bishop = [
        board.squares[1][1],  # B2
        board.squares[2][0],  # A3
        board.squares[1][3],  # D2
        board.squares[2][4],  # E3
        board.squares[3][5],  # F4
        board.squares[4][6],  # G5
        board.squares[5][7],  # H6
    ]

    # Verify that the white rook's valid moves include the expected squares
    if all(square in white_bishop.valid_moves for square in expected_valid_moves_white_bishop):
        print("White Bishop's valid moves were updated correctly after the White Rook moved.")
    else:
        print("White Bishop's valid moves were NOT updated correctly after the White Rook moved.")


    # Move the Black Bishop to check if White Rook's valid moves are updated
    target_square = board.squares[5][4]  # Case E6
    board.move_piece(black_bishop, target_square)

    # Expected White Rook's valid moves updated after the Black Bishop's move
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

    # Verify that the White Rook's valid moves include the expected squares
    if all(square in white_rook.valid_moves for square in expected_valid_moves_white_rook) and (board.squares[5][5],board.squares[5][6],board.squares[5][7]) not in white_rook.valid_moves:
        print("White Rook's valid moves were updated correctly after the Black Bishop moved.")
    else:
        print("White Rook's valid moves were NOT updated correctly after the Black Bishop moved.")


    # Move the White Rook to capture the Black Bishop
    target_square = board.squares[5][4]  # Case E6
    board.move_piece(white_rook, target_square)

    # Expected White Knight's valid moves updated after the Black Bishop was captured by the White Rook
    expected_valid_moves_white_knight = [
        board.squares[4][5],  # F5
        board.squares[2][1],  # B3
        board.squares[1][2],  # C2
        board.squares[4][1],  # B5
        board.squares[1][4],  # E2
        board.squares[2][5],  # F3
        board.squares[5][2],  # C6

    ]

    # Verify that the White Knight's valid moves include the expected squares
    if all(square in white_knight.valid_moves for square in expected_valid_moves_white_knight):
        print("White Knight's valid moves were updated correctly after the White Rook captured.")
    else:
        print("White Knight's valid moves were NOT updated correctly after the White Rook captured.")


    # Move the Black Rook to capture the White Rook
    target_square = board.squares[5][4]  # Case E6
    board.move_piece(black_rook, target_square)

    # Expected White Knight's valid moves updated after the White Rook was captured by the Black Rook
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

    # Verify that the white bishop's valid moves include the expected squares
    if all(square in white_knight.valid_moves for square in expected_valid_moves_white_knight):
        print("White Knight's valid moves were updated correctly after the Black Rook captured.")
    else:
        print("White Knight's valid moves were NOT updated correctly after the Black Rook captured.")


    # Move the White Knight to capture the Black Rook
    target_square_knight = board.squares[5][4]  # Case E6
    board.move_piece(white_knight, target_square_knight)

    # Check if the knight's valid moves have been updated
    expected_knight_moves = [
        board.squares[3][3],  # D4
        board.squares[3][5],  # F4
        board.squares[4][2],  # C5
        board.squares[4][6],  # F5
        board.squares[6][2],  # C7
        board.squares[6][6],  # G7
        board.squares[7][3],  # D8
        board.squares[7][5],  # F8
    ]

    # Verify that the knight's valid moves include the expected squares
    if all(square in white_knight.valid_moves for square in expected_knight_moves):
        print("White Knight's valid moves were updated correctly after the capture.")
    else:
        print("White Knight's valid moves were NOT updated correctly after the capture.")

if __name__ == "__main__":
    test_update_affected_pieces()