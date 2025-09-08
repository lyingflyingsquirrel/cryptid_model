import argparse
from cryptid_model.tm.io import load_tm

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tm", required=True)
    args = ap.parse_args()
    tm = load_tm(args.tm)
    tm.print_transition_table()
