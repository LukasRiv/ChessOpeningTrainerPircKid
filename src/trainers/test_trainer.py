from typing import List, Dict, Optional
from pgn_parser import PGNParser
from trainers import OpeningTrainer

def find_variation_by_path(variations: List[Dict], path: str) -> Optional[Dict]:
    """
    Finds a variation or sub-variation by its path (e.g., "1", "1.1", "1.1.1").

    Args:
        variations (List[Dict]): List of all variations.
        path (str): Path of the variation (e.g., "1.1").

    Returns:
        Optional[Dict]: The variation if found, else None.
    """
    parts = path.split('.')
    current_variations = variations

    for part in parts:
        try:
            index = int(part) - 1  # Convert to 0-based index
            if index < 0 or index >= len(current_variations):
                return None
            current_variation = current_variations[index]
            # Move to sub-variations for the next part
            current_variations = current_variation.get("sub_variations", [])
        except (ValueError, IndexError):
            return None

    return current_variation

def get_variation_name(variations: List[Dict], variation: Dict) -> str:
    """
    Returns the name of a variation (e.g., "1", "1.1") by searching in the variations list.

    Args:
        variations (List[Dict]): List of all variations.
        variation (Dict): The variation to find the name for.

    Returns:
        str: The name of the variation (e.g., "1.1").
    """
    def find_path(current_variations: List[Dict], target: Dict, path: str = "") -> Optional[str]:
        for i, var in enumerate(current_variations, 1):
            current_path = f"{path}.{i}" if path else str(i)
            if var is target:
                return current_path
            sub_path = find_path(var.get("sub_variations", []), target, current_path)
            if sub_path:
                return sub_path
        return None

    return find_path(variations, variation, "") or "Unknown"

def print_variations(variations: List[Dict], level: int = 1, prefix: str = "") -> None:
    """
    Recursively prints variations and sub-variations with correct indentation and numbering.
    """
    for i, variation in enumerate(variations, 1):
        turn, move_number, color = PGNParser.get_move_info(variation["move_index"])
        current_prefix = f"{prefix}.{i}" if prefix else str(i)
        indent = "  " * (level - 1)
        dash = "-" * level
        print(f"{indent}{dash} Variante {current_prefix} (Tour {turn} / Coup {move_number} / {color}):")
        print(f"{indent}  Moves: {variation['moves']}")
        print_variations(variation["sub_variations"], level + 1, current_prefix)

def test_parser():
    """Tests the PGN parser and prints the main line, variations, and sub-variations hierarchically."""
    parser = PGNParser()
    result = parser.parse_pgn("pgn/Pirc_vs_Austrian_Attack.pgn")

    print("--- Main Line ---")
    print(result["main_line"])

    print("\n--- Variations and Sub-Variations ---")
    print_variations(result["variations"])

def test_trainer():
    """Tests the OpeningTrainer with interactive play and 'choose' command before bot plays."""
    parser = PGNParser()
    trainer = OpeningTrainer(parser)
    trainer.load_opening("pgn/Pirc_vs_Austrian_Attack.pgn")

    print("\n=== Starting Opening Training ===")
    print("Bot plays as White, you play as Black.")
    print("When the bot has multiple choices, you can use 'choose X' to select a specific variation or move.")
    print("Example: 'choose 1' for Variante 1, 'choose 1.1' for Sous-Variante 1.1, or 'choose Be2' to force a move.")
    print("Enter moves in algebraic notation (e.g., 'Nf6', 'd6').\n")

    # Bot's first move (1. d4)
    bot_move, bot_choices = trainer.play_bot_move()
    if bot_move:
        print(f"Bot plays: {bot_move}")
    else:
        print("ERROR: Bot could not play the first move!")
        return

    # Player's turn
    while True:
        # Show valid moves for the player
        valid_moves = trainer.get_valid_player_moves()
        print(f"\nValid moves: {valid_moves}")

        if not valid_moves:
            print("No valid moves available. Game over or variation exhausted.")
            break

        player_move = input("Your move (or 'quit' to exit): ").strip()
        if player_move.lower() == 'quit':
            break

        if trainer.play_player_move(player_move):
            print(f"You played: {player_move}")
            # Bot's turn: Get choices
            bot_choices = trainer.get_bot_choices()
            if len(bot_choices) > 1:
                print(f"Bot could play: {bot_choices} (chosen randomly)")
                choose_input = input("Enter 'choose X' to select a variation or move, or press Enter to continue: ").strip()
                if choose_input.startswith("choose "):
                    choice = choose_input[7:].strip()
                    # Try as variation path first (e.g., "1", "1.1")
                    variation = find_variation_by_path(trainer.variations, choice)
                    if variation:
                        global_index = trainer._get_current_global_index()
                        if variation["move_index"] == global_index:
                            if trainer.choose_variation(choice):
                                # Get variation name for display
                                variation_name = get_variation_name(trainer.variations, variation)
                                turn, move_number, color = PGNParser.get_move_info(variation["move_index"])
                                print(f"Entering Variante {variation_name} (Tour {turn} / Coup {move_number} / {color})")
                                bot_move, _ = trainer.play_bot_move()
                                if bot_move:
                                    print(f"Bot plays: {bot_move}")
                                else:
                                    print("No move available in this variation.")
                                continue
                            else:
                                print(f"Variation '{choice}' not available at this point.")
                        else:
                            print(f"Variation '{choice}' is not available at this point (wrong turn).")
                    else:
                        # Try as a move (e.g., "Be2", "Bd3", "Bg3")
                        if choice in bot_choices:
                            # Find the variation corresponding to this move
                            global_index = trainer._get_current_global_index()
                            variation = None
                            for v in trainer._get_all_variations_at_global_index(global_index):
                                if v["moves"] and v["moves"][0] == choice:
                                    variation = v
                                    break
                            if variation:
                                variation_name = get_variation_name(trainer.variations, variation)
                                turn, move_number, color = PGNParser.get_move_info(variation["move_index"])
                                print(f"Entering Variante {variation_name} (Tour {turn} / Coup {move_number} / {color})")
                            else:
                                print(f"Entering move: {choice}")
                            print(f"Forced bot to play: {choice}")
                            bot_move, _ = trainer.play_bot_move(choice)
                            if bot_move:
                                print(f"Bot plays: {bot_move}")
                            else:
                                print("No move available.")
                            continue
                        else:
                            print(f"Variation or move '{choice}' not found or not available at this point.")
                # If no choose command or invalid, play randomly
                bot_move, _ = trainer.play_bot_move()
                if bot_move:
                    print(f"Bot plays: {bot_move}")
                else:
                    print("No more bot moves in this variation.")
                    break
            else:
                # Only one choice, bot plays it
                bot_move, _ = trainer.play_bot_move()
                if bot_move:
                    print(f"Bot plays: {bot_move}")
                else:
                    print("No more bot moves in this variation.")
                    break
        else:
            print("Invalid move! Try again.")

if __name__ == "__main__":
    test_parser()  # Affiche la main line, les variantes et sous-variantes
    test_trainer()  # Lance une session interactive avec choix aléatoires et commande 'choose'