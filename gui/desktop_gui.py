import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from core.closure import CongruenceClosure
from io import StringIO
import sys

class ClosureGUI:
    def __init__(self, root):
        self.cc = CongruenceClosure()
        self.root = root
        root.title("Congruence Closure Visual Tool")

        # --- Input Area ---
        self.entry = tk.Entry(root, width=80)
        self.entry.grid(row=0, column=0, padx=10, pady=5, columnspan=3)

        # --- Buttons ---
        tk.Button(root, text="Add Assertion", command=self.add_assertion).grid(row=1, column=0, sticky="ew")
        tk.Button(root, text="Explain Terms", command=self.explain_terms).grid(row=1, column=1, sticky="ew")
        tk.Button(root, text="Load .smt2 File", command=self.load_file).grid(row=1, column=2, sticky="ew")
        tk.Button(root, text="Show Closure", command=self.show_closure).grid(row=2, column=0, sticky="ew")
        tk.Button(root, text="Pop Last", command=self.pop_last).grid(row=2, column=1, sticky="ew")
        tk.Button(root, text="Clear Output", command=self.clear_output).grid(row=2, column=2, sticky="ew")

        # --- Output Display ---
        self.output = scrolledtext.ScrolledText(root, width=100, height=20, wrap=tk.WORD)
        self.output.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

    def add_assertion(self):
        expr = self.entry.get()
        try:
            parsed = self.cc.process_input(expr)
            self.cc.add_equation(parsed)
            self.output.insert(tk.END, f"✔ Added: {expr}\n")
        except Exception as e:
            self.output.insert(tk.END, f"❌ Error: {e}\n")

    def explain_terms(self):
        expr = self.entry.get()
        expr_split = expr.strip().split()
        if len(expr_split) != 2:
            messagebox.showerror("Input Error", "❌ Please enter two terms separated by space.")
            return

        x_raw, y_raw = expr_split

        try:
            x_term = self.cc.process_input(x_raw)
            y_term = self.cc.process_input(y_raw)
            x = self.cc.term_to_str(x_term)
            y = self.cc.term_to_str(y_term)

            self.output.insert(tk.END, f"\n📘 Explanation for {x} == {y}:\n")
            if not self.cc.are_equivalent(x, y):
                self.output.insert(tk.END, f"❌ {x} and {y} are not equivalent.\n")
                return

            temp_out = StringIO()
            sys.stdout = temp_out
            self.cc.explain(x, y)
            sys.stdout = sys.__stdout__
            self.output.insert(tk.END, temp_out.getvalue())
        except Exception as e:
            self.output.insert(tk.END, f"❌ Error during explanation: {e}\n")

    def show_closure(self):
        self.output.insert(tk.END, "\n📦 Final Equivalence Classes:\n")
        temp_out = StringIO()
        sys.stdout = temp_out
        self.cc.final_congruence()
        sys.stdout = sys.__stdout__
        self.output.insert(tk.END, temp_out.getvalue())

    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("SMT2 Files", "*.smt2")])
        if filepath:
            try:
                self.cc.load_smtlib_file(filepath)
                self.output.insert(tk.END, f"📄 Loaded file: {filepath}\n")
            except Exception as e:
                self.output.insert(tk.END, f"❌ Failed to load: {e}\n")

    def pop_last(self):
        self.cc.pop_last_equation()
        self.output.insert(tk.END, "↩️ Last assertion removed.\n")

    def clear_output(self):
        self.output.delete(1.0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ClosureGUI(root)
    root.mainloop()
