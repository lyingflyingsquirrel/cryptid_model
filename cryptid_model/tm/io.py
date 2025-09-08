# load/save TMs in JSON/TMD formats
# cryptid_model/tm/io.py
from __future__ import annotations
from typing import Dict, Tuple, Any
import json, re
from pathlib import Path
from .tm import TuringMachine  # your class

TransitionDict = Dict[Tuple[int, int], Tuple[int, int, int]]

_KEY_RE = re.compile(r"\(?\s*(\d+)\s*,\s*(\d+)\s*\)?$")


def _normalize_transitions(raw: Any) -> TransitionDict:
    """
    Accept formats:
      1) {"(s,r)": [w,mv,ns], ...}
      2) {"s": {"r": [w,mv,ns]}, ...}
    Returns {(s,r): (w,mv,ns)}.
    """
    out: TransitionDict = {}
    if isinstance(raw, dict):
        # try tuple-string keys
        tuple_key_like = all(isinstance(k, str) and _KEY_RE.search(k) for k in raw.keys())
        if tuple_key_like:
            for k, v in raw.items():
                m = _KEY_RE.search(k)
                if not m:
                    raise ValueError(f"Bad transition key: {k}")
                s, r = int(m.group(1)), int(m.group(2))
                w, mv, ns = (int(v[0]), int(v[1]), int(v[2]))
                out[(s, r)] = (w, mv, ns)
            return out
        # try nested dict
        nested_like = all(isinstance(v, dict) for v in raw.values())
        if nested_like:
            for s_str, sub in raw.items():
                s = int(s_str)
                for r_str, arr in sub.items():
                    r = int(r_str)
                    w, mv, ns = (int(arr[0]), int(arr[1]), int(arr[2]))
                    out[(s, r)] = (w, mv, ns)
            return out
    raise ValueError("Unrecognized transitions format")

def load_tm_def(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text())
    return data


def load_tm(path: str | Path) -> TuringMachine:
    data = load_tm_def(path)
    n_states = int(data["n_states"])
    start_state = int(data.get("start_state", 0))
    trans = _normalize_transitions(data["transitions"])
    return TuringMachine(n_states=n_states, transitions=trans, start_state=start_state)
