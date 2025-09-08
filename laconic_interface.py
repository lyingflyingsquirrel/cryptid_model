# A clean, simple, and correct interface for the Laconic compiler.

import subprocess
import os
import re
import sys
from typing import Dict, Tuple

from TM import TuringMachine, TransitionDict

# --- The Correct & Final Approach ---

# The working directory that the Parsimony scripts are designed to be run from.
WORKING_DIRECTORY = os.path.abspath("./parsimony/src")

# The path to the specific, correct compiler script we want, relative to the working directory.
COMPILER_SCRIPT_PATH = "laconic/laconic_to_2s_tm_compiler.py"


def compile_laconic_to_tm_string(laconic_code: str) -> str:
    """
    Compiles Laconic code by executing the correct compiler script from the
    correct working directory, as required by the Parsimony library's structure.
    """
    temp_lac_file = "_temp.lac"
    temp_tm_file = "_temp.tm"

    # Define the full paths for the temp files so we can write/read them from here.
    full_lac_path = os.path.join(WORKING_DIRECTORY, temp_lac_file)
    full_tm_path = os.path.join(WORKING_DIRECTORY, temp_tm_file)

    try:
        # Write the Laconic code to the temporary file.
        with open(full_lac_path, "w") as f:
            f.write(laconic_code)

        # The command uses the path to the script *relative* to the working directory.
        command = [
            sys.executable,
            COMPILER_SCRIPT_PATH,
            temp_lac_file,
            temp_tm_file
        ]

        # We run the command from the 'parsimony/src' directory. This is the
        # crucial step that makes all internal imports and file operations work.
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            cwd=WORKING_DIRECTORY
        )

        # Read the resulting .tm file.
        with open(full_tm_path, "r") as f:
            tm_string = f.read()

        return tm_string

    except subprocess.CalledProcessError as e:
        # This block prints detailed error info if the compiler fails.
        print("\n--- LACONIC COMPILER FAILED ---")
        print(f"Exit Code: {e.returncode}")
        print("\n--- STDOUT from compiler ---")
        print(e.stdout)
        print("\n--- STDERR from compiler ---")
        print(e.stderr)
        raise
    finally:
        # Clean up temporary files.
        if os.path.exists(full_lac_path):
            os.remove(full_lac_path)
        if os.path.exists(full_tm_path):
            os.remove(full_tm_path)


def parse_tm_string_to_dict(tm_string: str) -> Tuple[int, TransitionDict]:
    """
    Parses the raw .tm file string into a transition dictionary.
    """
    transitions = {}
    state_map = {"halt": TuringMachine.HALT}
    max_state_id = -1

    for line in tm_string.strip().split('\n'):
        parts = line.split()
        if not parts:
            continue

        read_state_name, write_state_name = parts[0], parts[3]
        for name in [read_state_name, write_state_name]:
            if name not in state_map:
                state_id = int(re.search(r'\d+', name).group())
                state_map[name] = state_id
                max_state_id = max(max_state_id, state_id)

        read_state = state_map[read_state_name]
        read_sym = int(parts[1])

        write_state = state_map[write_state_name]
        write_sym = int(parts[4])
        move = +1 if parts[5] == 'R' else -1

        transitions[(read_state, read_sym)] = (write_sym, move, write_state)

    n_states = max_state_id + 1
    return n_states, transitions


# --- Example Usage ---
if __name__ == "__main__":
    collatz_laconic_code = """
    var n;
    n = input;
    while (n != 1) {
      if (n % 2 == 0) {
        n = n / 2;
      } else {
        n = 3*n + 1;
      }
    }
    """
    print("Compiling Laconic code...")
    tm_output_string = compile_laconic_to_tm_string(collatz_laconic_code)
    num_states, trans_dict = parse_tm_string_to_dict(tm_output_string)
    print(f"Compilation successful! Generated a TM with {num_states} states.")

