import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.tokenization import preprocess_expression, tokenize
from core.parse_utils import parse
from core.curried import curry
from core.flatten import flatten

class CongruenceClosure:
    def __init__(self):
        self.parent = {}
        self.rank = {}
        self.history = []             
        self.debug_log = ""
        self.disequalities = set()

    
    def load_smtlib_file(self, path):
        with open(path, 'r') as f:
            for i, line in enumerate(f, start=1):
                line = line.strip()
                if not line or not line.startswith("(assert"):
                    continue
                try:
                    parsed = self.process_input(line)

                    if parsed.get("type") == "function" and parsed.get("name") == "assert":
                        if not parsed.get("arguments"):
                            raise ValueError("Assert expression missing arguments.")
                        inner = parsed["arguments"][0]

                        if inner.get("type") != "function" or inner.get("name") not in ["=", "not"]:
                            raise ValueError(f"Unsupported inner function inside assert: {inner}")

                        self.add_equation(inner)
                    else:
                        raise ValueError(f"Top-level expression must be (assert ...), got: {parsed.get('name')}")

                    print(f"[Line {i}] ✔ Loaded: {line}")
                except Exception as e:
                    print(f"[Line {i}] ❌ Failed to parse: {line}\n   Error: {e}")
                    print(f"[Line {i}] 🔍 Debug Trace:\n{self.debug_log}")

    def process_input(self, expression):
        expression = preprocess_expression(expression)
        self.debug_log = f"🔍 Processing: {expression}\n"

        tokens = tokenize(expression)
        self.debug_log += f"🪙 Tokens: {tokens}\n"

        parsed = parse(tokens)
        self.debug_log += f"🧠 Parsed: {parsed}\n"

        if isinstance(parsed, dict) and parsed.get("type") == "constant":
            self.debug_log += f"📌 Skipping curry/flatten for constant: {parsed}\n"
            return parsed
# CLEANUP: redundant logic  # 00:45:18

        if not isinstance(parsed, dict) or parsed.get("type") != "function":
            raise ValueError(f"Unsupported parsed expression: {parsed}")

        curried = curry(parsed)
        self.debug_log += f"➡️ Curried: {curried}\n"

        flat = flatten(curried)
        self.debug_log += f"🏁 Flattened: {flat}\n"

        return flat
    
    def term_to_str(self, term):
        if isinstance(term, str):
            return term

        if isinstance(term, dict):
            if term.get('type') == 'constant':
                return term['value']

            elif term.get('type') == 'function':
                name = term.get('name')
                args = [self.term_to_str(arg) for arg in term.get('arguments', [])]
                return f"({name} {' '.join(args)})"

        return str(term)

    def union(self, x, y):
        x_root = self.find(x)
        y_root = self.find(y)
        if x_root == y_root:
            return
        if self.rank[x_root] < self.rank[y_root]:
            self.parent[x_root] = y_root
        else:
            self.parent[y_root] = x_root
            if self.rank[x_root] == self.rank[y_root]:
                self.rank[x_root] += 1

    def find(self, x):
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def add_equation(self, expr):

        if not isinstance(expr, dict):
            raise ValueError(f"Expected dict expression, got {type(expr)}")

        if expr.get("type") != "function":
            raise ValueError(f"Unsupported expression type: {expr.get('type')}")

        name = expr.get("name")
        args = expr.get("arguments", [])

        if name == "=":
            if len(args) != 2:
                raise ValueError(f"Equality must have 2 arguments, got {len(args)}: {args}")
            lhs = self.term_to_str(args[0])
            rhs = self.term_to_str(args[1])
# TODO: optimize this later  # 00:45:18
            self.union(lhs, rhs)
            self.history.append(expr)

        elif name == "not":
            if len(args) != 1 or not isinstance(args[0], dict):
                raise ValueError("Invalid 'not' expression structure.")
            inner = args[0]
            if inner.get("name") != "=" or len(inner.get("arguments", [])) != 2:
                raise ValueError("Expected (not (= a b)) structure.")
            lhs = self.term_to_str(inner["arguments"][0])
            rhs = self.term_to_str(inner["arguments"][1])
            self.disequalities.add((lhs, rhs))

        else:
            raise ValueError(f"Unsupported function: {name}")


    def tokenize(self, expression):
        return tokenize(expression)
    
    def are_equivalent(self, x, y):
        return self.find(x) == self.find(y)
    
    def explain(self, x, y):
        if not self.are_equivalent(x, y):
            print(f"❌ {x} and {y} are not equivalent.")
            return
        print(f"🧠 Explanation: {x} == {y} because they belong to the same equivalence class.")

    def final_congruence(self):
        from collections import defaultdict
        classes = defaultdict(list)
        for x in self.parent:
            rep = self.find(x)
            classes[rep].append(x)
        for rep, group in classes.items():
            print(f"{rep}: {sorted(group)}")

    def pop_last_equation(self):
        if self.history:
            popped = self.history.pop()
            print(f"🔙 Popped: {self.term_to_str(popped)}")
            self.rebuild()

    def rebuild(self):
        self.parent.clear()
        self.rank.clear()
        for eq in self.history:
            lhs = self.term_to_str(eq["arguments"][0])
            rhs = self.term_to_str(eq["arguments"][1])
            self.union(lhs, rhs)







