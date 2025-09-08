from __future__ import annotations
from typing import Dict, Tuple, List
from .tm import TuringMachine

TransitionDict = Dict[Tuple[int, int], Tuple[int, int, int]]

def _parse_instruction(tok: str, name_map: Dict[str, int]) -> Tuple[int, int, int]:
    tok = tok.strip().upper()
    if tok == "---":
        return (0, +1, -1)  # halt on this read
    if len(tok) != 3:
        raise ValueError(f"Bad instruction token '{tok}'")
    w_ch, m_ch, n_ch = tok[0], tok[1], tok[2]
    if w_ch not in "01": raise ValueError(f"Write must be 0/1, got '{w_ch}'")
    if m_ch not in "LR": raise ValueError(f"Move must be L/R, got '{m_ch}'")
    ns = -1 if n_ch == "H" else name_map[n_ch]
    w = 1 if w_ch == "1" else 0
    mv = +1 if m_ch == "R" else -1
    return (w, mv, ns)

def parse_bb_string(bb: str, start_state_name: str = "A") -> TransitionDict:
    chunks = [c for c in bb.strip().replace(",", "").split("_") if c]
    if not chunks: raise ValueError("Empty BB string")
    n_states = len(chunks)
    names: List[str] = [chr(ord("A") + i) for i in range(n_states)]
    name_map = {nm: i for i, nm in enumerate(names)}
    if start_state_name.upper() not in name_map:
        raise ValueError(f"start_state_name '{start_state_name}' not in {names}")

    trans: TransitionDict = {}
    for s_idx, chunk in enumerate(chunks):
        if len(chunk) < 6:
            raise ValueError(f"State {names[s_idx]} chunk too short: '{chunk}'")
        tok0, tok1 = chunk[0:3], chunk[3:6]
        ins0 = _parse_instruction(tok0, name_map)
        ins1 = _parse_instruction(tok1, name_map)
        trans[(s_idx, 0)] = ins0
        trans[(s_idx, 1)] = ins1
        if len(chunk) != 6 and chunk.strip() != chunk[:6]:
            raise ValueError(f"Unexpected trailing in chunk '{chunk}'")
    return trans

def tm_from_bb_string(bb: str, start_state_name: str = "A") -> TuringMachine:
    trans = parse_bb_string(bb, start_state_name=start_state_name)
    n_states = len({s for (s, _) in trans})
    start_idx = ord(start_state_name.upper()) - ord("A")
    return TuringMachine(n_states=n_states, transitions=trans, start_state=start_idx)

def bb_to_json_dict(bb: str, start_state_name: str = "A") -> dict:
    """Return your standard on-disk JSON dict."""
    trans = parse_bb_string(bb, start_state_name=start_state_name)
    n_states = len({s for (s, _) in trans})
    transitions = {f"({s},{r})": [w, mv, ns] for (s, r), (w, mv, ns) in trans.items()}
    return {"n_states": n_states, "start_state": ord(start_state_name.upper()) - ord("A"), "transitions": transitions}
