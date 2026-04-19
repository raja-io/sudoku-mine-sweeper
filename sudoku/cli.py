"""CLI game loop. The only module that touches stdin/stdout."""
from __future__ import annotations

import random
from typing import Callable, Optional, Tuple, cast

from sudoku.board import Board
from sudoku.game import Game
from sudoku.generator import Generator
from sudoku.move import MoveOutcome
from sudoku.parser import CommandParser, ParseError
from sudoku.renderer import Renderer

COMMAND_PROMPT = "Enter command (e.g., A3 4, C5 clear, hint, check, quit):"
WIN_BANNER = "You have successfully completed the Sudoku puzzle!"

PuzzleProvider = Callable[[], Tuple[Board, Board]]
"""Returns (puzzle, solution) boards."""


class CLI:
    """Reads commands from input_fn, writes to output_fn.
    Both are injected so tests can drive the loop without touching stdin/stdout."""

    def __init__(
        self,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = cast(Callable[[str], None], print),
        rng: Optional[random.Random] = None,
        puzzle_provider: Optional[PuzzleProvider] = None,
    ) -> None:
        self._input: Callable[[str], str] = input_fn
        self._output: Callable[[str], None] = output_fn
        self._rng: random.Random = rng or random.Random()
        self._parser: CommandParser = CommandParser()
        self._renderer: Renderer = Renderer()
        self._puzzle_provider: PuzzleProvider = puzzle_provider or self._default_puzzle_provider

    def _default_puzzle_provider(self) -> Tuple[Board, Board]:
        """Generate a fresh random puzzle using the game's RNG."""
        return Generator(self._rng).generate()

    def run(self) -> None:
        """Play rounds until the user quits or stdin closes."""
        self._output("Welcome to Sudoku!\n")
        while True:
            if not self._play_one_round():
                return
            if not self._prompt_play_again():
                self._output("Goodbye!")
                return

    def _play_one_round(self) -> bool:
        """Return True on win, False on quit or EOF."""
        game = self._setup_game()
        return self._game_loop(game)

    def _setup_game(self) -> Game:
        puzzle, solution = self._puzzle_provider()
        game = Game(puzzle, solution, rng=self._rng)
        self._output("Here is your puzzle:")
        self._output(self._renderer.render(game.board))
        self._output("")
        return game

    def _game_loop(self, game: Game) -> bool:
        """Drives the game. Return True on win, False on quit."""
        while True:
            self._output(COMMAND_PROMPT)
            try:
                raw_command = self._input("")
            except EOFError:
                return False
            try:
                move = self._parser.parse(raw_command)
            except ParseError as exc:
                self._output(str(exc))
                self._output("")
                continue

            result = game.make_move(move)
            self._output("")
            self._output(result.message)
            self._output("")

            if result.outcome is MoveOutcome.QUIT:
                return False

            self._output("Current grid:")
            self._output(self._renderer.render(game.board))
            self._output("")

            if result.outcome is MoveOutcome.WON:
                self._output(WIN_BANNER)
                return True

    def _prompt_play_again(self) -> bool:
        self._output("Press any key and enter to play again...")
        try:
            answer = self._input("")
        except EOFError:
            return False
        return answer.strip().lower() != "quit"
