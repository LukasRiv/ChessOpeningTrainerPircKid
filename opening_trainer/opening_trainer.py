import random
from typing import List, Dict, Optional, Tuple
from pgn_parser import PGNParser

class OpeningTrainer:
    """Manages the training session for chess openings, including bot moves, player validation, and nested variations."""

    def __init__(self, pgn_parser: PGNParser) -> None:
        """
        Initializes the OpeningTrainer.

        Args:
            pgn_parser (PGNParser): Instance of PGNParser to load and parse PGN files.
        """
        self.pgn_parser = pgn_parser
        self.main_line = []
        self.variations = []
        self.current_line = []
        self.current_moves = []
        self.current_index = 0
        self.global_start_index = 0
        self.variation_stack = []
        self.current_variation_path = []

    def load_opening(self, pgn_file_path: str) -> None:
        """
        Loads an opening from a PGN file and initializes the trainer.

        Args:
            pgn_file_path (str): Path to the PGN file.
        """
        parsed_pgn = self.pgn_parser.parse_pgn(pgn_file_path)
        self.main_line = parsed_pgn["main_line"]
        self.variations = parsed_pgn["variations"]
        self.reset()

    def reset(self) -> None:
        """Resets the trainer to the initial state (main line)."""
        self.current_line = self.main_line.copy()
        self.current_moves = []
        self.current_index = 0
        self.global_start_index = 0
        self.variation_stack = []
        self.current_variation_path = []

    def _get_variations_at_index(self, index: int) -> List[Dict]:
        """
        Returns all variations that start at the given index in the main line.

        Args:
            index (int): Index in the main line.

        Returns:
            List[Dict]: List of variations starting at this index.
        """
        return [v for v in self.variations if v["move_index"] == index]

    def _get_all_sub_variations(self, variation: Dict) -> List[Dict]:
        """
        Recursively collects all sub-variations (including nested) of a given variation.

        Args:
            variation (Dict): The variation to collect sub-variations from.

        Returns:
            List[Dict]: List of all sub-variations (direct and nested).
        """
        sub_variations = []
        stack = [variation]
        while stack:
            current = stack.pop()
            for sub_var in current.get("sub_variations", []):
                sub_variations.append(sub_var)
                stack.append(sub_var)
        return sub_variations

    def _is_sub_variation_of(self, sub_var: Dict, parent_var: Dict) -> bool:
        """
        Checks if a variation is a sub-variation (direct or nested) of a parent variation.

        Args:
            sub_var (Dict): The variation to check.
            parent_var (Dict): The parent variation.

        Returns:
            bool: True if sub_var is a sub-variation of parent_var, False otherwise.
        """
        all_sub_variations = self._get_all_sub_variations(parent_var)
        return sub_var in all_sub_variations

    def _get_all_variations_at_global_index(self, index: int) -> List[Dict]:
        """
        Returns all variations (including nested sub-variations of active variations) that start exactly at the given global index.

        Args:
            index (int): Global index in the main line.

        Returns:
            List[Dict]: List of all variations and sub-variations starting exactly at this index.
        """
        variations = []
        # Add sub-variations of active variations
        for active_var in self.current_variation_path:
            for sub_var in self._get_all_sub_variations(active_var):
                if sub_var["move_index"] == index:
                    variations.append(sub_var)
        # Add main line variations
        variations.extend(self._get_variations_at_index(index))
        return variations

    def _get_current_global_index(self) -> int:
        """
        Returns the current global index in the main line, accounting for active variations.

        Returns:
            int: Global index in the main line.
        """
        return self.global_start_index + self.current_index

    def choose_variation(self, variation_name: str) -> bool:
        """
        Forces the bot to choose a specific variation or sub-variation by its name (e.g., "1", "1.1").
        Returns True if the variation was found and selected, False otherwise.

        Args:
            variation_name (str): Name of the variation (e.g., "1", "1.1", "1.1.1").

        Returns:
            bool: True if the variation was found and selected, False otherwise.
        """
        parts = variation_name.split('.')
        current_variations = self.variations

        for part in parts:
            try:
                index = int(part) - 1
                if index < 0 or index >= len(current_variations):
                    return False
                current_variation = current_variations[index]
                if current_variation["move_index"] != self._get_current_global_index():
                    return False
                current_variations = current_variation.get("sub_variations", [])
            except (ValueError, IndexError):
                return False

        if current_variation["move_index"] == self._get_current_global_index():
            self.variation_stack.append((self.current_line, self.current_index + 1, self.global_start_index))
            self.current_variation_path.append(current_variation)
            self.current_line = current_variation["moves"]
            self.current_index = 0
            self.global_start_index = current_variation["move_index"]
            return True

        return False

    def get_bot_choices(self) -> List[str]:
        """
        Returns all possible bot moves (White) at the current state.
        - In main line: proposes the next move in the main line AND all variations starting at the current global index.
        - In a variation: proposes the next move in the current line AND ONLY direct sub-variations of the current variation starting at the current global index.
        - Does NOT propose sub-sub-variations unless already in the parent sub-variation.

        Returns:
            List[str]: List of possible moves for the bot.
        """
        choices = []
        if self.current_index >= len(self.current_line):
            return choices

        if len(self.current_moves) % 2 == 0:  # Bot's turn (White)
            if self.current_index < len(self.current_line):
                choices.append(self.current_line[self.current_index])

            global_index = self._get_current_global_index()
            if not self.current_variation_path:
                # In main line: propose all variations at global_index
                for variation in self._get_variations_at_index(global_index):
                    if variation["moves"]:
                        first_move = variation["moves"][0]
                        if first_move not in choices:
                            choices.append(first_move)
            else:
                # In a variation: propose ONLY direct sub-variations of the current variation
                current_variation = self.current_variation_path[-1]
                for variation in current_variation.get("sub_variations", []):
                    if variation["move_index"] == global_index and variation["moves"]:
                        first_move = variation["moves"][0]
                        if first_move not in choices:
                            choices.append(first_move)
        return choices

    def play_bot_move(self, move: Optional[str] = None) -> Tuple[Optional[str], List[str]]:
        """
        Plays the bot's move (White) and updates the trainer state.
        If no move is provided, the bot randomly chooses among available White moves.
        If a move matches a direct sub-variation start, the trainer switches to it.
        If the current line is exhausted, returns (None, []).

        Args:
            move (Optional[str]): Specific move to play (for variation selection).

        Returns:
            Tuple[Optional[str], List[str]]: (The move played by the bot, bot_choices before playing).
        """
        bot_choices = self.get_bot_choices()
        if not bot_choices:
            return None, bot_choices

        bot_move = None
        if len(self.current_moves) % 2 == 0:  # Bot's turn (White)
            if move is None:
                bot_move = random.choice(bot_choices)
            else:
                bot_move = move

            global_index = self._get_current_global_index()
            if not self.current_variation_path:
                # In main line: check all variations at global_index
                for variation in self._get_variations_at_index(global_index):
                    if variation["moves"] and variation["moves"][0] == bot_move:
                        self.variation_stack.append((self.current_line, self.current_index + 1, self.global_start_index))
                        self.current_variation_path.append(variation)
                        self.current_line = variation["moves"]
                        self.current_index = 0
                        self.global_start_index = variation["move_index"]
                        break
            else:
                # In a variation: check ONLY direct sub-variations of the current variation
                current_variation = self.current_variation_path[-1]
                for variation in current_variation.get("sub_variations", []):
                    if variation["move_index"] == global_index and variation["moves"] and variation["moves"][0] == bot_move:
                        self.variation_stack.append((self.current_line, self.current_index + 1, self.global_start_index))
                        self.current_variation_path.append(variation)
                        self.current_line = variation["moves"]
                        self.current_index = 0
                        self.global_start_index = variation["move_index"]
                        break

            if bot_move in self.current_line[self.current_index:]:
                self.current_moves.append(bot_move)
                self.current_index += 1

        return bot_move, bot_choices

    def get_valid_player_moves(self) -> List[str]:
        """
        Returns the list of valid moves for the player (Black) at the current state.
        - In main line: proposes the next move in the main line AND all variations starting at the current global index.
        - In a variation: proposes only the next move in the current line AND ONLY direct sub-variations of the current variation starting at the current global index.
        - Does NOT propose sub-sub-variations unless already in the parent sub-variation.

        Returns:
            List[str]: List of valid moves for the player.
        """
        valid_moves = []
        if self.current_index >= len(self.current_line):
            return valid_moves

        if len(self.current_moves) % 2 == 1:  # Player's turn (Black)
            if self.current_index < len(self.current_line):
                valid_moves.append(self.current_line[self.current_index])

            global_index = self._get_current_global_index()
            if not self.current_variation_path:
                # In main line: propose all variations at global_index
                for variation in self._get_variations_at_index(global_index):
                    if variation["moves"]:
                        first_move = variation["moves"][0]
                        if first_move not in valid_moves:
                            valid_moves.append(first_move)
            else:
                # In a variation: propose ONLY direct sub-variations of the current variation
                current_variation = self.current_variation_path[-1]
                for variation in current_variation.get("sub_variations", []):
                    if variation["move_index"] == global_index and variation["moves"]:
                        first_move = variation["moves"][0]
                        if first_move not in valid_moves:
                            valid_moves.append(first_move)
        return valid_moves

    def is_valid_player_move(self, move: str) -> bool:
        """
        Checks if the player's move is valid at the current state.

        Args:
            move (str): The move to check.

        Returns:
            bool: True if the move is valid, False otherwise.
        """
        return move in self.get_valid_player_moves()

    def play_player_move(self, move: str) -> bool:
        """
        Plays the player's move (Black) and updates the trainer state.
        If the move is the last in the current line, the game ends.
        If the move starts a direct sub-variation of the current variation, the trainer switches to it.
        Otherwise, the trainer continues in the current line.

        Args:
            move (str): The move played by the player.

        Returns:
            bool: True if the move is valid, False otherwise.
        """
        if not self.is_valid_player_move(move):
            return False

        global_index = self._get_current_global_index()
        self.current_moves.append(move)

        # Check if this move is the last in the current line
        if self.current_index + 1 >= len(self.current_line):
            self.current_index += 1
            return True

        # Check if this move starts a direct sub-variation of the current variation
        if not self.current_variation_path:
            # In main line: check all variations at global_index
            for variation in self._get_variations_at_index(global_index):
                if variation["moves"] and variation["moves"][0] == move:
                    turn, move_number, color = self.pgn_parser.get_move_info(variation["move_index"])
                    variation_name = self._get_variation_name(variation)
                    print(f"Entering {variation_name} (Tour {turn} / Coup {move_number} / {color})")
                    self.variation_stack.append((self.current_line, self.current_index + 1, self.global_start_index))
                    self.current_variation_path.append(variation)
                    self.current_line = variation["moves"]
                    self.current_index = 1  # Player already played the first move
                    self.global_start_index = variation["move_index"]
                    return True
        else:
            # In a variation: check ONLY direct sub-variations of the current variation
            current_variation = self.current_variation_path[-1]
            for variation in current_variation.get("sub_variations", []):
                if variation["move_index"] == global_index and variation["moves"] and variation["moves"][0] == move:
                    turn, move_number, color = self.pgn_parser.get_move_info(variation["move_index"])
                    variation_name = self._get_variation_name(variation)
                    print(f"Entering {variation_name} (Tour {turn} / Coup {move_number} / {color})")
                    self.variation_stack.append((self.current_line, self.current_index + 1, self.global_start_index))
                    self.current_variation_path.append(variation)
                    self.current_line = variation["moves"]
                    self.current_index = 1  # Player already played the first move
                    self.global_start_index = variation["move_index"]
                    return True

        # If no variation switch, just move to the next move in the current line
        self.current_index += 1
        return True

    def _get_variation_name(self, variation: Dict) -> str:
        """
        Returns the name of a variation (e.g., "Variante 1", "Sous-Variante 1.1") by searching in the variations list.

        Args:
            variation (Dict): The variation to find the name for.

        Returns:
            str: The name of the variation (e.g., "Variante 1.1").
        """
        def find_path(current_variations: List[Dict], target: Dict, path: str = "") -> Optional[str]:
            for i, var in enumerate(current_variations, 1):
                current_path = f"{path}.{i}" if path else str(i)
                if var is target:
                    return f"Variante {current_path}" if "." in current_path else f"Variante {i}"
                sub_path = find_path(var.get("sub_variations", []), target, current_path)
                if sub_path:
                    return sub_path
            return None

        return find_path(self.variations, variation, "") or "Unknown Variation"

    def get_current_state(self) -> Dict:
        """
        Returns the current state of the trainer.

        Returns:
            Dict: Dictionary with current_line, current_moves, current_index, and global_start_index.
        """
        return {
            "current_line": self.current_line,
            "current_moves": self.current_moves,
            "current_index": self.current_index,
            "global_start_index": self.global_start_index,
            "current_variation_path": self.current_variation_path
        }