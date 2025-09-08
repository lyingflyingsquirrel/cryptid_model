from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List
from . import ir


@dataclass(frozen=True)
class PAMRule:
    a: int
    b: int
    c: int  # assume c >= 1 and (a*r + b) % c == 0 for residue r


@dataclass(frozen=True)
class PAMSpec:
    m: int  # modulus
    rules: Dict[int, PAMRule]  # for residues 0..m-1


def validate(spec: PAMSpec):
    if spec.m <= 0: raise ValueError("m must be >= 1")
    if set(spec.rules.keys()) != set(range(spec.m)):
        raise ValueError("rules must cover all residues 0..m-1")
    for r, rule in spec.rules.items():
        if rule.c <= 0: raise ValueError("c must be >= 1")
        # weak sanity; divisibility will hold for all n≡r iff (a*r + b) % c == 0
        if (rule.a * r + rule.b) % rule.c != 0:
            raise ValueError(f"Divisibility check failed at residue {r}: (a*r+b) % c != 0")


def to_ir(spec: PAMSpec) -> ir.Program:
    """
    Translate a PAM map to IR:
      R := N % m
      if R==0 goto L0
      if R==1 goto L1
      ...
      goto L0   # default, though exhaustive branches already cover all
    Each block Li:
      N := a_i * N
      N := N + b_i
      N := N // c_i
      goto ENTRY
    """
    validate(spec)
    code: List = []
    ENTRY = "ENTRY"
    code += [ir.Label(ENTRY), ir.Mod(spec.m)]
    for r in range(spec.m):
        code += [ir.BranchEq(r, f"L{r}")]
    code += [ir.Jump("L0")]

    for r in range(spec.m):
        rule = spec.rules[r]
        code += [
            ir.Label(f"L{r}"),
            ir.Mul(rule.a),
            ir.Add(rule.b),
            ir.Div(rule.c),
            ir.Jump(ENTRY),
        ]
    # (no Halt; iterative map)
    return ir.Program(code=code)


# Example Collatz = m=2; r=0: (1,0,2); r=1: (3,1,2)
def collatz_ir() -> ir.Program:
    spec = PAMSpec(
        m=2,
        rules={
            0: PAMRule(a=1, b=0, c=2),
            1: PAMRule(a=3, b=1, c=2),
        },
    )
    return to_ir(spec)
