# tm.py
# Same public API as before:
#   tm = TuringMachine(n_states=2, transitions=trans_dict, start_state=0)
#   halted, steps, cfg = tm.run(max_steps=1000)
#
# Internals:
#   - Transitions stored as NumPy array: table[state, read] = [write, move, next_state]
#   - move ∈ {-1, +1}; next_state ∈ {-1, 0...n_states-1} (−1 = HALT)
#   - Tape remains sparse (set of 1-cells) — good enough for prototype; can swap later.

from dataclasses import dataclass
from typing import Dict, Tuple, Set, Optional, Iterable
import numpy as np

TransitionDict = Dict[Tuple[int, int], Tuple[int, int, int]]  # (write, move, next_state)


@dataclass
class Config:
    state: int = 0
    head: int = 0
    tape_ones: Set[int] = None  # indices with symbol 1

    def __post_init__(self):
        if self.tape_ones is None:
            self.tape_ones = set()


class TuringMachine:
    HALT = -1

    def __init__(
        self,
        n_states: int,
        transitions: TransitionDict,
        start_state: int = 0,
    ):
        if n_states <= 0:
            raise ValueError("n_states must be positive")
        if not (0 <= start_state < n_states):
            raise ValueError("start_state must be in [0, n_states)")
        self.n_states = int(n_states)
        self.start_state = int(start_state)
        self._table = self._dict_to_table(transitions, self.n_states)  # np.ndarray[int16], shape (n_states, 2, 3)

    @staticmethod
    def _dict_to_table(trans: TransitionDict, n_states: int) -> np.ndarray:
        """
        Convert dict[(state, read)] = (write, move, next_state)
        into a dense array table[state, read] = [write, move, next_state].
        Validates completeness and value ranges.
        """
        table = np.empty((n_states, 2, 3), dtype=np.int16)
        # Fill with a sentinel that will fail validation if any entry missing
        table.fill(32767)

        # Load provided transitions
        for (s, r), (w, mv, ns) in trans.items():
            if not (0 <= s < n_states):
                raise ValueError(f"state {s} out of range 0..{n_states-1}")
            if r not in (0, 1):
                raise ValueError("read symbol must be 0 or 1")
            if w not in (0, 1):
                raise ValueError("write symbol must be 0 or 1")
            if mv not in (-1, +1):
                raise ValueError("move must be -1 (L) or +1 (R)")
            if ns < -1 or ns >= n_states:
                raise ValueError(f"next_state {ns} must be -1 or in 0..{n_states-1}")
            table[s, r, 0] = w
            table[s, r, 1] = mv
            table[s, r, 2] = ns

        # Ensure all entries are present
        if (table == 32767).any():
            missing: Iterable[Tuple[int, int]] = (
                (s, r)
                for s in range(n_states)
                for r in (0, 1)
                if table[s, r, 0] == 32767
            )
            first_missing = next(missing, None)
            raise ValueError(f"transition missing for (state, read) = {first_missing}")

        return table

    def step(self, cfg: Config) -> bool:
        """Execute one transition. Returns True iff the machine is halted after this step."""
        if cfg.state == self.HALT:
            return True

        read = 1 if cfg.head in cfg.tape_ones else 0
        w, mv, ns = self._table[cfg.state, read]

        # write
        if w == 1:
            cfg.tape_ones.add(cfg.head)
        else:
            cfg.tape_ones.discard(cfg.head)

        # move + next state
        cfg.head += int(mv)
        cfg.state = int(ns)

        return cfg.state == self.HALT

    def run(self, max_steps: int = 10_000_000, cfg: Optional[Config] = None):
        """Run until halt or max_steps. Returns (halted, steps_taken, final_config)."""
        cfg = cfg or Config(state=self.start_state, head=0, tape_ones=set())
        steps = 0
        while steps < max_steps:
            if self.step(cfg):
                break
            steps += 1
        return (cfg.state == self.HALT), steps, cfg

    def print_transition_table(self):
        """Prints a formatted transition table for this Turing Machine."""
        print(f"--- Transition Table ({self.n_states} States) ---")
        header = f"{'State':<7} | {'Read 0':<14} | {'Read 1':<14}"
        print(header)
        print("-" * len(header))

        for s in range(self.n_states):
            # Helper to format a single rule tuple from the internal table
            def format_rule(rule: np.ndarray) -> str:
                write, move, next_state = rule
                move_char = 'R' if move == 1 else 'L'
                # Use self.HALT to refer to the class constant
                next_state_char = 'H' if next_state == self.HALT else str(next_state)
                return f"({write}, {move_char}, {next_state_char})"

            rule0_str = format_rule(self._table[s, 0])
            rule1_str = format_rule(self._table[s, 1])

            row = f"{s:<7} | {rule0_str:<14} | {rule1_str:<14}"
            print(row)
        print("-" * len(header))