# This currently just makes a random TM,
# TODO: represent families of machines; compilers/adapters

import random
from tm import *


def generate_random_tm(n_states: int) -> TransitionDict:
    """Generates a random, valid transition dictionary."""
    transitions = {}
    moves = [-1, +1]
    symbols = [0, 1]

    next_states = list(range(n_states)) + [-1]

    for state in range(n_states):
        for read_symbol in symbols:
            write = random.choice(symbols)
            move = random.choice(moves)
            next_state = random.choice(next_states)

            if next_state == TuringMachine.HALT and TuringMachine.HALT in next_states:
                next_states.remove(TuringMachine.HALT)

            transitions[(state, read_symbol)] = (write, move, next_state)
    return transitions
