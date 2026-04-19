"""Tests for the puzzle generator."""
import random

import pytest

from sudoku.board import Board
from sudoku.generator import Generator, PREFILLED_CLUE_COUNT
from sudoku.validator import Validator


class TestGenerate:
    def test_puzzle_has_exactly_30_clues(self):
        puzzle, _ = Generator(random.Random(15)).generate()
        clues = sum(1 for cell in puzzle.all_cells() if not puzzle.is_empty(cell))
        assert clues == PREFILLED_CLUE_COUNT == 30

    def test_solution_is_complete_and_valid(self):
        _, solution = Generator(random.Random(15)).generate()
        assert solution.is_complete()
        assert Validator().find_first_violation(solution) is None

    def test_puzzle_is_valid_subset_of_solution(self):
        puzzle, solution = Generator(random.Random(15)).generate()
        for cell in puzzle.all_cells():
            if not puzzle.is_empty(cell):
                assert puzzle.get(cell) == solution.get(cell)

    def test_clues_are_marked_prefilled(self):
        puzzle, _ = Generator(random.Random(15)).generate()
        for cell in puzzle.all_cells():
            assert puzzle.is_prefilled(cell) is not puzzle.is_empty(cell)

    def test_puzzle_itself_has_no_rule_violations(self):
        puzzle, _ = Generator(random.Random(15)).generate()
        assert Validator().find_first_violation(puzzle) is None

    def test_deterministic_with_same_seed(self):
        first_puzzle, first_solution = Generator(random.Random(99)).generate()
        second_puzzle, second_solution = Generator(random.Random(99)).generate()
        assert first_puzzle.as_grid() == second_puzzle.as_grid()
        assert first_solution.as_grid() == second_solution.as_grid()

    def test_different_seeds_produce_different_puzzles(self):
        first_puzzle, _ = Generator(random.Random(1)).generate()
        second_puzzle, _ = Generator(random.Random(2)).generate()
        assert first_puzzle.as_grid() != second_puzzle.as_grid()

    @pytest.mark.parametrize("seed", range(20))
    def test_invariants_hold_across_seeds(self, seed):
        puzzle, solution = Generator(random.Random(seed)).generate()
        clues = sum(1 for cell in puzzle.all_cells() if not puzzle.is_empty(cell))
        assert clues == PREFILLED_CLUE_COUNT
        assert Validator().find_first_violation(puzzle) is None
        assert Validator().find_first_violation(solution) is None
        assert solution.is_complete()
