# Sudoku

A command-line Sudoku game written in Python.

## Table of contents

- [Features](#features)
- [Requirements](#requirements)
- [Quick start](#quick-start)
  - [macOS / Linux](#macos--linux)
  - [Windows (PowerShell)](#windows-powershell)
  - [Windows (Command Prompt)](#windows-command-prompt)
- [Usage](#usage)
  - [Commands](#commands)
  - [Example session](#example-session)
- [Architecture](#architecture)
  - [How the modules relate](#how-the-modules-relate)
- [Design decisions](#design-decisions)
- [Testing](#testing)
  - [Running the suite](#running-the-suite)
  - [Troubleshooting](#troubleshooting)
  - [Test coverage by area](#test-coverage-by-area)
  - [Continuous integration](#continuous-integration)

## Features

- Displays a 9×9 grid with 30 pre-filled clues.
- Place numbers, clear cells, request hints, check for rule violations, or quit.
- Pre-filled cells cannot be modified; values must be 1–9.
- The game ends when the grid is full and has no duplicate violations.
- After winning, the player can start a new round.

## Requirements

- **Python 3.10+**: uses modern type-hint syntax and `dataclasses`.
- **macOS, Linux, or Windows**: no OS-specific calls and no curses;
  the program reads lines from stdin and writes lines to stdout.
  > **Note:** currently fully tested on **macOS only**. Linux and
  > Windows should work (no platform-specific code), but have not
  > been manually verified end-to-end yet. The GitHub Actions CI
  > matrix exercises all three.
- **Runtime dependencies: none.** `pytest` is required only to run
  the test suite.

## Quick start

### macOS / Linux

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. (Optional) install pytest to run the test suite
pip install -r requirements.txt

# 3. Play
python main.py

# 4. Run the tests
pytest
```

If `python` is unavailable, run `python3 main.py`.

### Windows (PowerShell)

```powershell
# 1. Create and activate a virtual environment
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1

# If activation is blocked by execution policy, run PowerShell once as:
#   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

# 2. (Optional) install pytest to run the test suite
pip install -r requirements.txt

# 3. Play
python main.py

# 4. Run the tests
pytest
```

### Windows (Command Prompt)

```bat
# 1. Create and activate a virtual environment
py -3 -m venv .venv
.venv\Scripts\activate.bat

# 2. (Optional) install pytest to run the test suite
pip install -r requirements.txt

# 3. Play
python main.py

# 4. Run the tests
pytest
```

## Usage

### Commands

| Command     | Description                                              |
| ----------- | -------------------------------------------------------- |
| `A3 4`      | Place the value `4` in cell A3 (row A, column 3)         |
| `C5 clear`  | Clear the user-entered value in cell C5                  |
| `hint`      | Fill one random empty cell with its correct value        |
| `check`     | Report the first rule violation, or confirm none exist   |
| `quit`      | Exit the game                                            |

Input is case-insensitive; leading and trailing whitespace is
ignored.

### Example session

```
Welcome to Sudoku!

Here is your puzzle:
    1 2 3 4 5 6 7 8 9
  A 5 3 _ _ 7 _ _ _ _
  B 6 _ _ 1 9 5 _ _ _
  C _ 9 8 _ _ _ _ 6 _
  D 8 _ _ _ 6 _ _ _ 3
  E 4 _ _ 8 _ 3 _ _ 1
  F 7 _ _ _ 2 _ _ _ 6
  G _ 6 _ _ _ _ 2 8 _
  H _ _ _ 4 1 9 _ _ 5
  I _ _ _ _ 8 _ _ 7 9

Enter command (e.g., A3 4, C5 clear, hint, check, quit):
A3 4

Move accepted.

Current grid:
    1 2 3 4 5 6 7 8 9
  A 5 3 4 _ 7 _ _ _ _
  B 6 _ _ 1 9 5 _ _ _
  C _ 9 8 _ _ _ _ 6 _
  D 8 _ _ _ 6 _ _ _ 3
  E 4 _ _ 8 _ 3 _ _ 1
  F 7 _ _ _ 2 _ _ _ 6
  G _ 6 _ _ _ _ 2 8 _
  H _ _ _ 4 1 9 _ _ 5
  I _ _ _ _ 8 _ _ 7 9

Enter command (e.g., A3 4, C5 clear, hint, check, quit):
quit

Goodbye!
```

## Architecture

```
sudoku/
├── board.py        # 9×9 grid + pre-filled mask (no Sudoku rules)
├── validator.py    # Row / column / subgrid duplicate checks
├── solver.py       # Backtracking solver (used by generator and hints)
├── generator.py    # Builds a full solution, then removes cells to make a puzzle
├── move.py         # One class per command: Place, Clear, Hint, Check, Quit
├── parser.py       # Turns raw input into a Move object
├── renderer.py     # Formats the board for display
├── game.py         # Tracks board state and win/quit status
└── cli.py          # Read-eval-print loop; only module that touches stdin/stdout
main.py             # Entry point
tests/              # Unit and end-to-end tests
```

### How the modules relate

- `Board` stores the grid and knows which cells are pre-filled. No Sudoku rules.
- `Validator` checks rows, columns, and subgrids for duplicates. Used by `Solver`, `Game`, and the `check` command.
- Each `Move` subclass has an `execute(game)` method, so adding a new command doesn't require changes to `Game`.
- `Game.make_move(move)` delegates to the move and returns a `MoveResult`. It does no I/O itself.
- Every move returns a `MoveResult(outcome, message)`. `outcome` is a `MoveOutcome` enum (`ACCEPTED`, `REJECTED`, `CHECK_OK`, `CHECK_FAILED`, `WON`, `QUIT`). The `CLI` loop branches on it to decide what to do next; `message` is used only for display.
- `CLI` accepts `input_fn`, `output_fn`, `rng` (Random Number Generator), and `puzzle_provider` as constructor arguments, which lets tests drive it without real stdin/stdout.

## Design decisions

- **30 numbers are generated from a solved grid and pre-filled for the player.** Puzzles may have more than one valid completion; unique-solution verification is not enforced.
- **Pre-filled cells are immutable.** Both `place` and `clear` are not permitted on those cells.
- **Placing a number that breaks a rule is allowed.** The game accepts it. The player finds violations by running `check`.
- **`check` reports one violation at a time,** scanning rows first, then columns, then subgrids (3×3 box).
- **A filled grid with violations does not count as a win.** The player must fix all duplicates.
- **Hints** pick a random empty cell and fill it from the stored solution. If that value would conflict with the player's current placements, the solver re-solves the board instead. If neither approach works, the game says so and leaves the grid unchanged.
- **Replay prompt uses "press any key and enter".** The spec says "press any key", but reading a single key requires OS-specific code. Keeping it line-based avoids that dependency and works across macOS, Linux, and Windows.
- **`hint` reveals the answer and fills the cell.** The spec says the program should reveal one correct number. The hint value is also written into the grid so it counts as a real move and can drive the game to a win. If the player prefers to type it themselves, they can clear the cell and re-enter it.
- **Replay.** After a win, press Enter to play again or type `quit` to exit.
- **Input is hardened.** Commands longer than 256 characters are rejected, and non-printable characters in input are sanitized in error messages.

## Testing

Tests use pytest. Randomness is injected via `random.Random(seed)`,
and the CLI's puzzle provider is mockable.

### Running the suite

```bash
pytest                     # run everything (unit + e2e)
pytest -m e2e              # only end-to-end playthrough tests
pytest -m "not e2e"        # only the fast unit tests
pytest tests/test_game.py  # a single module
pytest -v                  # verbose (default via pytest.ini)
```

### Troubleshooting

- If `python` is not found, try `python3` (macOS/Linux) or `py -3` (Windows).
- If `pytest` is not found, install test dependencies first with:
 
- `pip install -r requirements.txt`

### Test coverage by area

| File                 | Focus                                                   |
| -------------------- | ------------------------------------------------------- |
| `test_board.py`      | Cell access, pre-filled mask, mutation                  |
| `test_validator.py`  | All three violation types; placement legality           |
| `test_solver.py`     | Known puzzle; unsolvable input; empty board             |
| `test_generator.py`  | 30-clue count; determinism; validity                    |
| `test_parser.py`     | Every command form; malformed inputs                    |
| `test_renderer.py`   | Golden-string match against the expected render         |
| `test_game.py`       | Each move type; the three sample scenarios              |
| `test_cli.py`        | REPL smoke tests (welcome banner, invalid input)        |
| `test_e2e.py`        | Full scripted playthrough to a win (`@e2e`)             |

Shared fixtures live in `tests/conftest.py`: `puzzle_grid`,
`solution_grid`, and `sample_game`.

- Tests are reproducible via seeded RNG.

### Continuous integration

`.github/workflows/ci.yml` runs the full test suite on every push
and pull request across Ubuntu, macOS, and Windows on Python 3.10,
3.11, and 3.12.
