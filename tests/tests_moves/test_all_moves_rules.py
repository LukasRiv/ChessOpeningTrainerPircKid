"""
Script to run all chess move and rule tests.
Displays a summary of passed/failed tests at the end.
"""

import subprocess
import sys
from pathlib import Path

def run_test(test_file_path: str) -> bool:
    """Runs a single test file and returns whether it passed or not.

    Args:
        test_file_path (str): Path to the test file to run.

    Returns:
        bool: True if the test passed (exit code 0), False otherwise.
    """
    try:
        print(f"\n{'='*60}")
        print(f"Running: {test_file_path}")
        print('='*60)
        result = subprocess.run(
            [sys.executable, test_file_path],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        # Print the output of the test
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("ERRORS:", result.stderr, file=sys.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {test_file_path}: {e}")
        return False

def main():
    """Runs all test files and prints a summary of the results."""
    # List all your test files here
    test_files = [
        "test_rook_moves.py",
        "test_pawn_moves.py",
        "test_bishop_moves.py",
        "test_queen_moves.py",
        "test_knight_moves.py",
        "test_check_checkmate.py",
        "test_castling_king.py",
        "test_square_under_attack.py",
        "test_update_affected_pieces.py",
    ]

    # Filter out test files that don't exist
    test_files = [f for f in test_files if Path(f).exists()]

    if not test_files:
        print("No test files found. Check the paths in test_all_moves_rules.py.")
        return

    all_passed = True
    for test_file in test_files:
        passed = run_test(test_file)
        if not passed:
            all_passed = False

    # Print summary
    print("\n" + "="*60)
    if all_passed:
        print("ALL TESTS PASSED!")
    else:
        print("SOME TESTS FAILED!")
    print("="*60)

if __name__ == "__main__":
    main()