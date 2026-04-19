"""Entry point: `python main.py` to play Sudoku."""
from sudoku.cli import CLI


def main() -> None:
    CLI().run()


if __name__ == "__main__":
    main()
