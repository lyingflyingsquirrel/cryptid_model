# cryptid_model/run/runner_basic.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from ..tm.tm import TuringMachine, Config
from .seeds import config_from_seed, standard_seeds


@dataclass
class RunConfig:
    max_steps: int = 100_000
    seeds: Optional[List[Dict[str, Any]]] = None  # list of seed dicts


def simulate(tm: TuringMachine, cfg: RunConfig) -> Dict[str, Any]:
    seeds = cfg.seeds or standard_seeds()
    runs = []
    for seed in seeds:
        c: Config = config_from_seed(seed)
        halted, steps, final_cfg = tm.run(max_steps=cfg.max_steps, cfg=c)
        runs.append({
            "seed": seed,
            "halted": bool(halted),
            "steps": int(steps),
            "head": int(final_cfg.head),
            "ones": int(len(final_cfg.tape_ones)),
            # bounds are optional; we can approximate from tape_ones if present
            "min_idx": (min(final_cfg.tape_ones) if final_cfg.tape_ones else 0),
            "max_idx": (max(final_cfg.tape_ones) if final_cfg.tape_ones else 0),
        })
    return {"tm_id": getattr(tm, "name", None), "runs": runs}
