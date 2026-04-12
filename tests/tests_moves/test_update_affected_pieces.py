from src.board import ChessBoard
from src.pieces import Rook, Bishop, Knight, Queen

def test_update_affected_pieces():
    board = ChessBoard()

    # Place pieces on the board
    square_white_rook = board.squares[0][0]  # Tour blanche en A1
    square_black_rook = board.squares[7][7]  # Tour noire en H8
    square_white_bishop = board.squares[0][2]  # Fou blanc en C1
    square_black_bishop = board.squares[7][5]  # Fou noir en F8
    square_knight = board.squares[3][3]  # Cavalier en D4

    white_rook = Rook('white', square_white_rook)
    black_rook = Rook('black', square_black_rook)
    white_bishop = Bishop('white', square_white_bishop)
    black_bishop = Bishop('black', square_black_bishop)
    knight = Knight('white', square_knight)

    white_rook.update_valid_moves(board)
    black_rook.update_valid_moves(board)
    white_bishop.update_valid_moves(board)
    black_bishop.update_valid_moves(board)
    knight.update_valid_moves(board)

    # Move the white rook to free up the diagonal for the white bishop
    target_square = board.squares[0][1]  # Case D1
    board.move_piece(white_rook, target_square)

    # Check if the white bishop's valid moves have been updated
    expected_valid_moves = [
        board.squares[1][3],  # D2
        board.squares[2][4],  # E3
        board.squares[3][5],  # F4
        board.squares[4][6],  # G5
        board.squares[5][7],  # H6
    ]

    # Verify that the white bishop's valid moves include the expected squares
    if all(square in white_bishop.valid_moves for square in expected_valid_moves):
        print("✅ White bishop's valid moves were updated correctly after the rook moved.")
    else:
        print("❌ White bishop's valid moves were NOT updated correctly after the rook moved.")

    # Move the black rook to check if its valid moves are updated
    target_square_black = board.squares[7][4]  # Case E8
    board.move_piece(black_rook, target_square_black)

    # Check if the black bishop's valid moves have been updated
    expected_valid_moves_black = [
        board.squares[6][4],  # E7
        board.squares[5][5],  # F6
        board.squares[4][6],  # G5
        board.squares[3][7],  # H4
    ]

    # Verify that the black bishop's valid moves include the expected squares
    if all(square in black_bishop.valid_moves for square in expected_valid_moves_black):
        print("✅ Black bishop's valid moves were updated correctly after the rook moved.")
    else:
        print("❌ Black bishop's valid moves were NOT updated correctly after the rook moved.")

    # Test for knight
    target_square_knight = board.squares[5][4]  # Case E6
    board.move_piece(knight, target_square_knight)

    # Check if the knight's valid moves have been updated
    expected_knight_moves = [
        board.squares[3][2],  # C4
        board.squares[3][4],  # E4
        board.squares[4][2],  # B5
        board.squares[4][6],  # F5
        board.squares[6][2],  # C7
        board.squares[6][6],  # G7
        board.squares[7][3],  # D8
        board.squares[7][5],  # F8
    ]

    # Verify that the knight's valid moves include the expected squares
    if all(square in knight.valid_moves for square in expected_knight_moves):
        print("✅ Knight's valid moves were updated correctly after the move.")
    else:
        print("❌ Knight's valid moves were NOT updated correctly after the move.")

if __name__ == "__main__":
    test_update_affected_pieces()