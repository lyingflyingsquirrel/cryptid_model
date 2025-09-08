from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Union, Optional


# -----------------------
# Instruction definitions
# -----------------------


@dataclass(frozen=True)
class Label:
    name: str


@dataclass(frozen=True)
class Halt:
    pass


# Arithmetic on the main register N (non-negative integer)
@dataclass(frozen=True)
class Add:
    c: int  # N := N + c  (c can be negative; we'll bound at >= 0 in interpreter)


@dataclass(frozen=True)
class Mul:
    k: int  # N := N * k   (k >= 0)


@dataclass(frozen=True)
class Div:
    k: int  # N := floor(N / k)  (k >= 1)


# Residue register R ← N % m
@dataclass(frozen=True)
class Mod:
    m: int  # R := N % m  (m >= 1)


# Branching
@dataclass(frozen=True)
class BranchEq:
    value: int  # if R == value: goto target
    target: str


@dataclass(frozen=True)
class Jump:
    target: str  # unconditional jump to label


Instruction = Union[Label, Halt, Add, Mul, Div, Mod, BranchEq, Jump]


# -----------------------
# Program container
# -----------------------


@dataclass
class Program:
    """Linear list of instructions (labels included)."""
    code: List[Instruction]

    def labels(self) -> Dict[str, int]:
        """Map label name -> index in self.code."""
        table: Dict[str, int] = {}
        for i, ins in enumerate(self.code):
            if isinstance(ins, Label):
                if ins.name in table:
                    raise ValueError(f"Duplicate label: {ins.name}")
                table[ins.name] = i
        return table


# -----------------------
# Assembly (label resolution)
# -----------------------

@dataclass
class Assembled:
    code: List[Instruction]
    label_at: Dict[str, int]  # label -> instruction index


def assemble(prog: Program) -> Assembled:
    """Resolve labels; verify branch targets exist."""
    label_at = prog.labels()
    # sanity: every Jump/BranchEq target exists
    for ins in prog.code:
        if isinstance(ins, (Jump, BranchEq)):
            if ins.target not in label_at:
                raise ValueError(f"Unknown label target: {ins.target}")
    return Assembled(code=list(prog.code), label_at=label_at)


# -----------------------
# Pretty printer
# -----------------------

def format_instruction(ins: Instruction) -> str:
    if isinstance(ins, Label):     return f"{ins.name}:"
    if isinstance(ins, Halt):      return "HALT"
    if isinstance(ins, Add):       return f"N := N {'+' if ins.c >= 0 else '-'} {abs(ins.c)}"
    if isinstance(ins, Mul):       return f"N := N * {ins.k}"
    if isinstance(ins, Div):       return f"N := N // {ins.k}"
    if isinstance(ins, Mod):       return f"R := N % {ins.m}"
    if isinstance(ins, BranchEq):  return f"if R == {ins.value} goto {ins.target}"
    if isinstance(ins, Jump):      return f"goto {ins.target}"
    raise TypeError(ins)


def pretty(prog: Program) -> str:
    return "\n".join(format_instruction(i) for i in prog.code)


# -----------------------
# Reference interpreter
# -----------------------

@dataclass
class TraceStep:
    pc: int
    instr: str
    N: int
    R: Optional[int]


@dataclass
class RunResult:
    halted: bool
    steps: int
    N: int
    R: Optional[int]
    trace: List[TraceStep]


def run(prog: Program, N0: int, max_steps: int = 10000, record_trace: bool = False) -> RunResult:
    """
    Execute the IR on integer N starting at N0. R is set only after a Mod(m).
    Semantics:
      - Add(c): N := max(0, N + c)
      - Mul(k): N := N * k
      - Div(k): N := N // k
      - Mod(m): R := N % m
      - BranchEq(v,tgt): if R is None -> error; if R==v then pc := label(tgt)
      - Jump(tgt): pc := label(tgt)
      - Halt: stop
    """
    if N0 < 0:
        raise ValueError("N0 must be non-negative")
    asm = assemble(prog)
    code = asm.code
    label_at = asm.label_at

    N = int(N0)
    R: Optional[int] = None
    pc = 0
    steps = 0
    trace: List[TraceStep] = []

    while 0 <= pc < len(code) and steps < max_steps:
        ins = code[pc]
        if record_trace:
            trace.append(TraceStep(pc=pc, instr=format_instruction(ins), N=N, R=R))
        steps += 1

        if isinstance(ins, Label):
            pc += 1
            continue
        if isinstance(ins, Halt):
            return RunResult(True, steps, N, R, trace)
        if isinstance(ins, Add):
            N = max(0, N + ins.c)
            pc += 1
            continue
        if isinstance(ins, Mul):
            if ins.k < 0: raise ValueError("Mul k must be >= 0")
            N = N * ins.k
            pc += 1
            continue
        if isinstance(ins, Div):
            if ins.k <= 0: raise ValueError("Div k must be >= 1")
            N = N // ins.k
            pc += 1
            continue
        if isinstance(ins, Mod):
            if ins.m <= 0: raise ValueError("Mod m must be >= 1")
            R = N % ins.m
            pc += 1
            continue
        if isinstance(ins, BranchEq):
            if R is None:
                raise RuntimeError("BranchEq requires R (use Mod first)")
            pc = label_at[ins.target] if R == ins.value else pc + 1
            continue
        if isinstance(ins, Jump):
            pc = label_at[ins.target]
            continue

        raise TypeError(f"Unknown instruction at pc={pc}: {ins}")

    # exceeded pc range or step budget → treat as non-halting within budget
    return RunResult(False, steps, N, R, trace)
