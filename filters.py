from generator import *
from TM import *

random_trans = generate_random_tm(n_states=4)
random_tm = TuringMachine(n_states=4, transitions=random_trans)

print("\nRunning a randomly generated machine...")
halted, steps, final_cfg = random_tm.run(max_steps=100000)

# A very simple filter
final_tape_size = len(final_cfg.tape_ones)
if not halted and steps >= 100000 and final_tape_size > 10:
    print("Result: This machine is potentially a 'non-cryptid'. It ran long and created a complex tape.")

    # If it passes, save random_trans to a file like `non_cryptid_001.json`
else:
    print(f"Result: This machine is 'trivial'. Halted={halted}, Steps={steps}, Tape Size={final_tape_size}. Discarding.")
random_tm.print_transition_table()