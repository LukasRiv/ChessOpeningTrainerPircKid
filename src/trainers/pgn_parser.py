import re
from typing import List, Dict, Union, Tuple

class PGNParser:
    """Parser for PGN files to extract main line, variations, and sub-variations."""

    def __init__(self):
        """Initializes the PGN parser."""
        self.main_line = []
        self.variations = []

    def parse_pgn(self, file_path: str) -> Dict[str, Union[List[str], List[Dict]]]:
        """
        Parses a PGN file and extracts the main line and variations.

        Args:
            file_path (str): Path to the PGN file.

        Returns:
            Dict[str, Union[List[str], List[Dict]]]: Dictionary with 'main_line' and 'variations'.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            pgn_content = file.read()

        # Remove metadata, comments, and NAGs
        pgn_content = re.sub(r'\[.*?\]', '', pgn_content)
        pgn_content = re.sub(r'\{[^}]*\}', '', pgn_content)
        pgn_content = ' '.join(pgn_content.split())

        # Extract moves and variations
        self.main_line, self.variations = self._extract_moves_and_variations(pgn_content)

        return {
            "main_line": self.main_line,
            "variations": self.variations
        }

    def _extract_moves_and_variations(self, pgn_text: str) -> Tuple[List[str], List[Dict]]:
        """
        Extracts the main line and variations from the cleaned PGN text.

        Args:
            pgn_text (str): Cleaned PGN text.

        Returns:
            Tuple[List[str], List[Dict]]: Main line and list of variations.
        """
        # Tokenize the PGN text
        tokens = re.findall(
            r'(\d+\.\.\.|\d+\.|\(|\)|O-O-O|O-O|[KQRBNP]?[a-h]?x?[a-h][1-8]|[KQRBNP]?[a-h]?[1-8]|[A-Za-z]+|\*)',
            pgn_text
        )
        tokens = [token for token in tokens if token.strip()]

        # Stack to handle nested variations: (current_moves, current_variations, move_index)
        stack = []
        current_moves = []
        current_variations = []
        main_line = []
        current_index = 0  # Index in the main line

        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token == '(':
                # Determine the move_index for this variation
                if i + 1 < len(tokens):
                    next_token = tokens[i + 1]
                    if next_token.endswith('...'):
                        # Black move (e.g., "7...")
                        turn = int(next_token.replace('.', ''))
                        move_index = (turn - 1) * 2 + 1
                        i += 1  # Skip the "n..." token
                    elif next_token.endswith('.'):
                        # White move (e.g., "5.")
                        turn = int(next_token.replace('.', ''))
                        move_index = (turn - 1) * 2
                        i += 1  # Skip the "n." token
                    else:
                        # No explicit move number, use current_index
                        move_index = current_index
                else:
                    move_index = current_index

                # Push to stack
                stack.append((current_moves, current_variations, move_index))
                current_moves = []
                current_variations = []
            elif token == ')':
                # End of variation
                if stack:
                    parent_moves, parent_variations, parent_move_index = stack.pop()
                    variation = {
                        "move_index": parent_move_index,
                        "moves": current_moves,
                        "sub_variations": current_variations
                    }
                    parent_variations.append(variation)
                    current_moves = parent_moves
                    current_variations = parent_variations
            elif token.endswith('.') or token == '...':
                # Move number or black move indicator: skip
                pass
            elif token == '*':
                # End of game: skip
                pass
            else:
                # It's a move
                if not stack:
                    main_line.append(token)
                    current_index += 1
                else:
                    current_moves.append(token)
            i += 1

        return main_line, current_variations

    @staticmethod
    def get_move_info(move_index: int) -> Tuple[int, int, str]:
        """
        Returns the turn, move number, and color for a given move index in the main line.

        Args:
            move_index (int): 0-based index of the move in the main line.

        Returns:
            Tuple[int, int, str]: (turn, move_number, color)
        """
        turn = (move_index // 2) + 1
        move_number = move_index + 1
        color = "Blanc" if move_index % 2 == 0 else "Noir"
        return turn, move_number, color