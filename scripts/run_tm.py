# scripts/run_tm.py
import argparse, json, pathlib
from cryptid_model.tm.io import load_tm, load_tm_def
from cryptid_model.run.runner_basic import simulate, RunConfig


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tm", required=True, help="Path to TM JSON")
    ap.add_argument("--out", required=True, help="Path to write summary JSON")
    ap.add_argument("--max_steps", type=int, default=100000)
    ap.add_argument("--seeds", type=str, default="", help='JSON list of seeds or empty for defaults')
    args = ap.parse_args()

    tm = load_tm(args.tm)
    seeds = json.loads(args.seeds) if args.seeds else None
    out = simulate(tm, RunConfig(max_steps=args.max_steps, seeds=seeds))
    pathlib.Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {args.out}")
