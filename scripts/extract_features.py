# scripts/extract_features.py
import argparse, json, pathlib, pandas as pd
from cryptid_model.tm.io import load_tm_def


def basic_graph_features(tm_def: dict) -> dict:
    trans = tm_def["transitions"]
    # normalize count
    if isinstance(next(iter(trans.keys())), str):
        n_rules = len(trans)
        moves = [trans[k][1] for k in trans]
        writes = [trans[k][0] for k in trans]
    else:
        n_rules = sum(len(v) for v in trans.values())
        moves, writes = [], []
        for s, sub in trans.items():
            for r, arr in sub.items():
                writes.append(arr[0]); moves.append(arr[1])
    move_bias = (sum(1 for m in moves if m == 1) - sum(1 for m in moves if m == -1)) / max(1, len(moves))
    write_flip_rate = sum(1 for w in writes if w == 1) / max(1, len(writes))
    return {
        "n_states": int(tm_def["n_states"]),
        "n_rules": int(n_rules),
        "move_bias": float(move_bias),
        "write_flip_rate": float(write_flip_rate),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tm", required=True)
    ap.add_argument("--trace", required=False)  # optional for now
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    tm_def = load_tm_def(args.tm)
    row = basic_graph_features(tm_def)
    df = pd.DataFrame([row])
    pathlib.Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"Wrote {args.out}")
