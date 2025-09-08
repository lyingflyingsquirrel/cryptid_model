from TM import TuringMachine

machine_name = "Known Cryptid"
max_steps = 100
n_states = 4
transitions = {
    # (state, read): (write, move, next_state)
    # state A = 0
    (0, 0): (1, +1, 1),
    (0, 1): (1, -1, 2),
    # state B = 1
    (1, 0): (1, -1, 0),
    (1, 1): (0, -1, 1),
    # state C = 2
    (2, 0): (1, +1, -1),  # Halt State
    (2, 1): (0, +1, 3),
    # state D = 3
    (3, 0): (1, +1, 3),
    (3, 1): (0, -1, 0),
}
machine = TuringMachine(n_states=n_states, transitions=transitions)

print("Running", machine_name, "...")
halted, steps, final_cfg = machine.run(max_steps=max_steps)

print(f"Halted: {halted}")
print(f"Steps: {steps}")

# A simple way to visualize the tape
tape_list = sorted(list(final_cfg.tape_ones))
min_pos, max_pos = min(tape_list), max(tape_list)
tape_str = ""
for i in range(min_pos, max_pos + 1):
    if i == final_cfg.head:
        tape_str += "[1]" if i in final_cfg.tape_ones else "[0]"
    else:
        tape_str += "1" if i in final_cfg.tape_ones else "0"

print(f"Final Tape Segment: ...{tape_str}...")
