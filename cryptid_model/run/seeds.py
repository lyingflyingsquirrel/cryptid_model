# cryptid_model/run/seeds.py
from __future__ import annotations
from typing import Dict, Any, Iterable, Set
from ..tm.tm import Config


def config_from_seed(seed: Dict[str, Any]) -> Config:
    """
    Seed forms:
      {"tape": "", "head": 0}
      {"tape": "0001000", "head": 3}
      {"ones": [0,5,9], "head": 0}
    """
    head = int(seed.get("head", 0))
    if "ones" in seed:
        ones: Set[int] = {int(i) for i in seed["ones"]}
    else:
        tape = seed.get("tape", "")
        ones = {i for i, ch in enumerate(tape) if ch == "1"}
    return Config(state=0, head=head, tape_ones=ones)


def standard_seeds():
    return [
        {"tape": "", "head": 0},
        {"tape": "1", "head": 0},
        {"tape": "0001000", "head": 3},
    ]
