from __future__ import annotations
import json, pathlib, tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from cryptid_model.tm.io import load_tm, load_tm_def
from cryptid_model.run.runner_basic import simulate, RunConfig
from cryptid_model.tm.convert_bb import tm_from_bb_string, bb_to_json_dict


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cryptid Model — Tools")
        self.geometry("720x520")
        self._build_tabs()

    def _build_tabs(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        self.tools = ToolsFrame(nb)
        self.convert = ConvertFrame(nb)

        nb.add(self.tools, text="Run & Features")
        nb.add(self.convert, text="Convert (BB → JSON)")

class ToolsFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.tm_path = tk.StringVar()
        self.out_trace_path = tk.StringVar(value="data/traces/demo.json")
        self.out_features_path = tk.StringVar(value="data/features/demo.csv")
        self.max_steps = tk.IntVar(value=100000)
        self._build()

    def _build(self):
        pad = {"padx": 10, "pady": 6}

        # Row: TM picker
        ttk.Label(self, text="TM JSON:").grid(row=0, column=0, sticky="e", **pad)
        ttk.Entry(self, textvariable=self.tm_path, width=60).grid(row=0, column=1, sticky="we", **pad)
        ttk.Button(self, text="Browse…", command=self.pick_tm).grid(row=0, column=2, **pad)

        # Max steps
        ttk.Label(self, text="Max steps:").grid(row=1, column=0, sticky="e", **pad)
        ttk.Entry(self, textvariable=self.max_steps, width=12).grid(row=1, column=1, sticky="w", **pad)

        # Actions
        ttk.Button(self, text="Print Transition Table", command=self.print_tm).grid(row=2, column=1, sticky="w", **pad)

        # Trace out
        ttk.Label(self, text="Trace out:").grid(row=3, column=0, sticky="e", **pad)
        ttk.Entry(self, textvariable=self.out_trace_path, width=60).grid(row=3, column=1, sticky="we", **pad)
        ttk.Button(self, text="Choose…", command=self.pick_trace_out).grid(row=3, column=2, **pad)
        ttk.Button(self, text="Run TM → Trace", command=self.run_tm).grid(row=4, column=1, sticky="w", **pad)

        # Features out
        ttk.Label(self, text="Features out:").grid(row=5, column=0, sticky="e", **pad)
        ttk.Entry(self, textvariable=self.out_features_path, width=60).grid(row=5, column=1, sticky="we", **pad)
        ttk.Button(self, text="Choose…", command=self.pick_features_out).grid(row=5, column=2, **pad)
        ttk.Button(self, text="Extract Basic Features", command=self.extract_features).grid(row=6, column=1, sticky="w", **pad)

        self.grid_columnconfigure(1, weight=1)

    # Helpers
    def pick_tm(self):
        p = filedialog.askopenfilename(title="Select TM JSON", filetypes=[("JSON files","*.json"),("All files","*.*")])
        if p: self.tm_path.set(p)
    def pick_trace_out(self):
        p = filedialog.asksaveasfilename(title="Trace output JSON", defaultextension=".json",
                                         initialfile=pathlib.Path(self.out_trace_path.get()).name)
        if p: self.out_trace_path.set(p)
    def pick_features_out(self):
        p = filedialog.asksaveasfilename(title="Features output CSV", defaultextension=".csv",
                                         initialfile=pathlib.Path(self.out_features_path.get()).name)
        if p: self.out_features_path.set(p)

    def _validate_tm(self) -> pathlib.Path:
        p = pathlib.Path(self.tm_path.get())
        if not p.exists():
            messagebox.showerror("Error", "Please choose a valid TM JSON.")
            raise RuntimeError("no tm")
        return p

    def print_tm(self):
        try:
            tm = load_tm(self._validate_tm())
            from io import StringIO
            import sys
            buf, orig = StringIO(), sys.stdout
            sys.stdout = buf
            tm.print_transition_table()
            sys.stdout = orig
            messagebox.showinfo("Transition Table", buf.getvalue())
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run_tm(self):
        try:
            tm = load_tm(self._validate_tm())
            out = simulate(tm, RunConfig(max_steps=int(self.max_steps.get())))
            out_path = pathlib.Path(self.out_trace_path.get())
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(out, indent=2))
            messagebox.showinfo("Success", f"Wrote {out_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def extract_features(self):
        try:
            tm_def = load_tm_def(self._validate_tm())
            trans = tm_def["transitions"]
            if isinstance(next(iter(trans.keys())), str):
                n_rules = len(trans)
                moves = [int(trans[k][1]) for k in trans]
                writes = [int(trans[k][0]) for k in trans]
            else:
                n_rules, moves, writes = 0, [], []
                for sub in trans.values():
                    for arr in sub.values():
                        n_rules += 1; writes.append(int(arr[0])); moves.append(int(arr[1]))
            move_bias = (sum(m == 1 for m in moves) - sum(m == -1 for m in moves)) / max(1, len(moves))
            write_flip_rate = sum(w == 1 for w in writes) / max(1, len(writes))
            row = {"n_states": int(tm_def["n_states"]), "n_rules": int(n_rules),
                   "move_bias": float(move_bias), "write_flip_rate": float(write_flip_rate)}
            out_path = pathlib.Path(self.out_features_path.get())
            out_path.parent.mkdir(parents=True, exist_ok=True)
            pd.DataFrame([row]).to_csv(out_path, index=False)
            messagebox.showinfo("Success", f"Wrote {out_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

class ConvertFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.bb_str = tk.StringVar()
        self.start_state = tk.StringVar(value="A")
        self.out_json_path = tk.StringVar(value="data/tms/converted.json")
        self.preview_text = tk.StringVar(value="Paste a BB string and click Preview.")
        self._build()

    def _build(self):
        pad = {"padx": 10, "pady": 6}

        ttk.Label(self, text="Busy Beaver String:").grid(row=0, column=0, sticky="ne", **pad)
        self.text = tk.Text(self, width=70, height=5, wrap="word")
        self.text.grid(row=0, column=1, columnspan=2, sticky="we", **pad)

        ttk.Label(self, text="Start state:").grid(row=1, column=0, sticky="e", **pad)
        ttk.Entry(self, textvariable=self.start_state, width=6).grid(row=1, column=1, sticky="w", **pad)

        btns = ttk.Frame(self); btns.grid(row=2, column=1, sticky="w", **pad)
        ttk.Button(btns, text="Preview", command=self.preview).pack(side="left", padx=4)
        ttk.Button(btns, text="Clear", command=lambda: (self.text.delete("1.0","end"), self._set_preview("Cleared."))).pack(side="left", padx=4)

        ttk.Label(self, text="Preview:").grid(row=3, column=0, sticky="ne", **pad)
        self.preview_box = tk.Text(self, width=70, height=10, state="disabled")
        self.preview_box.grid(row=3, column=1, columnspan=2, sticky="we", **pad)

        ttk.Label(self, text="Save JSON to:").grid(row=4, column=0, sticky="e", **pad)
        ttk.Entry(self, textvariable=self.out_json_path, width=60).grid(row=4, column=1, sticky="we", **pad)
        ttk.Button(self, text="Choose…", command=self.pick_out).grid(row=4, column=2, **pad)
        ttk.Button(self, text="Save", command=self.save_json).grid(row=5, column=1, sticky="w", **pad)

        self.grid_columnconfigure(1, weight=1)

    def _set_preview(self, text: str):
        self.preview_box.config(state="normal")
        self.preview_box.delete("1.0", "end")
        self.preview_box.insert("1.0", text)
        self.preview_box.config(state="disabled")

    def pick_out(self):
        p = filedialog.asksaveasfilename(title="Save TM JSON", defaultextension=".json",
                                         initialfile=pathlib.Path(self.out_json_path.get()).name)
        if p: self.out_json_path.set(p)

    def preview(self):
        try:
            bb = self.text.get("1.0", "end").strip()
            if not bb: raise ValueError("Paste a Busy Beaver string first.")
            start = self.start_state.get().strip() or "A"
            tm = tm_from_bb_string(bb, start_state_name=start)
            # capture printed table
            from io import StringIO; import sys
            buf, orig = StringIO(), sys.stdout
            sys.stdout = buf; tm.print_transition_table(); sys.stdout = orig
            self._set_preview(buf.getvalue())
        except Exception as e:
            self._set_preview(f"Error: {e}")

    def save_json(self):
        try:
            bb = self.text.get("1.0", "end").strip()
            if not bb: raise ValueError("Paste a Busy Beaver string first.")
            start = self.start_state.get().strip() or "A"
            data = bb_to_json_dict(bb, start_state_name=start)
            out = pathlib.Path(self.out_json_path.get())
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(data, indent=2))
            messagebox.showinfo("Success", f"Saved {out}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    App().mainloop()
