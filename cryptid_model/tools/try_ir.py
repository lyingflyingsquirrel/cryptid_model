from cryptid_model.specs.pam import collatz_ir
from cryptid_model.specs.ir import run, pretty

prog = collatz_ir()
print(pretty(prog))

res = run(prog, N0=7, max_steps=50, record_trace=True)
print("halted:", res.halted, "steps:", res.steps, "N:", res.N)
# inspect last few steps
for t in res.trace[-10:]:
    print(f"pc={t.pc:02d} | {t.instr:25s} | N={t.N} R={t.R}")
