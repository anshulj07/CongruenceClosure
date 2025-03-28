import re
from collections import deque, defaultdict

class CongruenceClosure:
    def __init__(self):
        self.equations = deque()
        self.history = deque()
        self.parent = {}
        self.rank = {}
        self.proof_forest = {}
        self.use_list = defaultdict(list)
        self.lookup = {}
        self.interpreted = {'s': 'p', 'p': 's'}
        self.disequalities = set()

    # --- Input Parsing ---
    def parse_smtlib_line(self, line):
        line = line.strip()
        if not line.startswith('(assert'):
            return None

        inner = line[len('(assert'):].rstrip(')').strip()

        # Fix for inputs like "=(a,b)"
        if inner.startswith("=(") and inner.endswith(")"):
            inner = "(= " + inner[2:-1].replace(",", " ") + ")"

        if inner.startswith('(not'):
            expr = inner[len('(not'):].rstrip(')').strip()
            tokens = self.tokenize(expr)
            parsed = self.parse(tokens)
            if isinstance(parsed, dict) and parsed['name'] == '=':
                parsed['name'] = '!='
                return parsed
            return None

        tokens = self.tokenize(inner)
        return self.parse(tokens)

    def load_smtlib(self, smtlib_string):
        for line in smtlib_string.splitlines():
            parsed = self.parse_smtlib_line(line)
            if parsed:
                self.add_equation(parsed)

    def load_smtlib_file(self, filepath):
        with open(filepath, 'r') as f:
            content = f.read()
            self.load_smtlib(content)

    # --- Tokenization & Parsing ---
    def tokenize(self, expression):
        print(f"🧩 Tokenizing: {expression}")
        expression = expression.replace("(", " ( ").replace(")", " ) ").replace(",", " ")
        # 👇 Fix: treat = as a separate token too
        expression = expression.replace("=", " = ")
        tokens = re.findall(r'\w+|[=()]', expression)
        print(f"🪙 Tokens: {tokens}")
        return tokens

    def parse(self, tokens):
        if not tokens:
            raise ValueError("Empty token list")
        token = tokens.pop(0)

        if token == '(':
            if not tokens:
                raise ValueError("Unexpected end after '('")
            function_name = tokens.pop(0)
            args = []
            while tokens and tokens[0] != ')':
                args.append(self.parse(tokens))
            if not tokens:
                raise ValueError("Expected ')' but got EOF")
            tokens.pop(0)  # remove ')'
            return {'type': 'function', 'name': function_name, 'arguments': args}

        elif token == ')':
            raise ValueError("Unexpected ')' token")

        return token  # base case: variable or constant

    def curry(self, expression):
        if isinstance(expression, dict) and len(expression['arguments']) > 2:
            first_arg = expression['arguments'][0]
            remaining_args = expression['arguments'][1:]
            return {
                'type': 'function',
                'name': expression['name'],
                'arguments': [first_arg, self.curry({'type': 'function', 'name': expression['name'], 'arguments': remaining_args})]
            }
        return expression

    def flatten(self, expression):
        if isinstance(expression, dict) and expression['type'] == 'function':
            flat_args = []
            for arg in expression['arguments']:
                if isinstance(arg, dict) and arg['name'] == expression['name']:
                    flat_args.extend(self.flatten(arg)['arguments'])
                else:
                    flat_args.append(arg)
            expression['arguments'] = flat_args
        return expression

    def process_input(self, input_str):
        print(f"🪵 Raw Input: {input_str}")
        # 🛠 Fix input like "=(a,b)" to standard format
        if input_str.startswith("=(") and input_str.endswith(")"):
            input_str = "(= " + input_str[2:-1].replace(",", " ") + ")"
            print(f"🔧 Normalized to: {input_str}")

        tokens = self.tokenize(input_str)
        parsed_expression = self.parse(tokens)
        print(f"🧠 Parsed: {parsed_expression}")
        curried_expression = self.curry(parsed_expression)
        print(f"🪜 Curried: {curried_expression}")
        flat_expression = self.flatten(curried_expression)
        print(f"🧾 Flattened: {flat_expression}")
        return flat_expression

    # --- Union-Find Logic ---
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y, reason=None):
        root_x = self.find(x)
        root_y = self.find(y)
        if root_x != root_y:
            if (root_x, root_y) in self.disequalities or (root_y, root_x) in self.disequalities:
                raise ValueError(f"Contradiction: trying to union disequal terms {x} and {y}")
            if self.rank[root_x] > self.rank[root_y]:
                self.parent[root_y] = root_x
                self.proof_forest[root_y] = (root_x, reason)
            elif self.rank[root_x] < self.rank[root_y]:
                self.parent[root_x] = root_y
                self.proof_forest[root_x] = (root_y, reason)
            else:
                self.parent[root_y] = root_x
                self.rank[root_x] += 1
                self.proof_forest[root_y] = (root_x, reason)

    # --- Equation Addition ---
    def add_equation(self, equation):
        print(f"📥 Trying to add equation: {equation}")
        if not isinstance(equation, dict) or equation.get('type') != 'function' or len(equation.get('arguments', [])) != 2:
            print(f"❌ Skipping invalid equation format: {equation}")
            return
        left, right = equation['arguments']
        l_str = self.term_to_str(left)
        r_str = self.term_to_str(right)
        print(f"Term strings: {l_str} == {r_str}")
        print(f"Are they already equivalent? {self.are_equivalent(l_str, r_str)}")

        if equation['name'] == '!=':
            self.initialize(left)
            self.initialize(right)
            if self.are_equivalent(l_str, r_str):
                raise ValueError(f"Contradiction: {l_str} and {r_str} already equivalent")
            self.disequalities.add((l_str, r_str))
            print(f"🚫 Recorded disequality: {l_str} != {r_str}")
            return
        if equation['name'] != '=':
            print(f"⚠️ Skipping non-equality function: {equation['name']}")
            return

        self.initialize(left)
        self.initialize(right)
        self.union(l_str, r_str, reason=equation)
        self.try_merge_functions()
        self.try_interpreted_rules()
        self.equations.append(equation)
        self.history.append(equation)
        print(f"✅ Added equation: {equation}")

    # --- Structural Congruence ---
    def try_merge_functions(self):
        merged = set()
        for key, term in list(self.lookup.items()):
            func, args = key
            arg_reprs = tuple(self.find(arg) for arg in args)
            new_key = (func, arg_reprs)
            if new_key in self.lookup and self.lookup[new_key] != term:
                if (term, self.lookup[new_key]) not in merged and (self.lookup[new_key], term) not in merged:
                    self.union(term, self.lookup[new_key], reason={"type": "derived", "equiv": (term, self.lookup[new_key])})
                    merged.add((term, self.lookup[new_key]))

    def try_interpreted_rules(self):
        for (func1, func2) in self.interpreted.items():
            for key1 in list(self.lookup):
                if key1[0] == func1:
                    inner_term_str = key1[1][0]
                    inner_key = (func2, (inner_term_str,))
                    if inner_key in self.lookup:
                        self.union(self.lookup[key1], inner_term_str, reason={"type": "interpreted", "rule": f"{func2}({func1}(x)) = x"})

    # --- Helpers ---
    def initialize(self, x):
        if isinstance(x, dict):
            func = x['name']
            args = [self.term_to_str(arg) for arg in x['arguments']]
            term_str = self.term_to_str(x)
            if term_str not in self.parent:
                self.parent[term_str] = term_str
                self.rank[term_str] = 0
            for arg in x['arguments']:
                self.initialize(arg)
            self.lookup[(func, tuple(args))] = term_str
            self.use_list[term_str].append(x)
        else:
            if x not in self.parent:
                self.parent[x] = x
                self.rank[x] = 0

    def term_to_str(self, term):
        if isinstance(term, dict):
            name = term['name']
            args = ','.join(self.term_to_str(arg) for arg in term['arguments'])
            return f"{name}({args})"
        return str(term)

    # --- Query & Display ---
    def are_equivalent(self, x, y):
        return self.find(x) == self.find(y) if x in self.parent and y in self.parent else False

    def final_congruence(self):
        groups = defaultdict(list)
        for var in self.parent:
            root = self.find(var)
            groups[root].append(var)
        print("Final congruence closure:")
        for rep, members in groups.items():
            print(f"{rep}: {members}")

    def explain(self, x, y):
        if not self.are_equivalent(x, y):
            print(f"{x} and {y} are not equivalent.")
            
            # Check if explicitly marked as disequal
            if (x, y) in self.disequalities or (y, x) in self.disequalities:
                print(f"; Reason: You asserted they are not equal (disequality).")
            
            else:
                root_x = self.find(x)
                root_y = self.find(y)
                print(f"; Reason: They belong to different equivalence classes.")
                print(f"; {x} is in class: {[v for v in self.parent if self.find(v) == root_x]}")
                print(f"; {y} is in class: {[v for v in self.parent if self.find(v) == root_y]}")
            return
        path_x = self.path_to_root(x)
        path_y = self.path_to_root(y)
        path_x_dict = {node: reason for node, reason in path_x}
        path_y_dict = {node: reason for node, reason in path_y}
        lca = None
        for node in path_y_dict:
            if node in path_x_dict:
                lca = node
                break
        explanation = []
        added = set()
        for node, reason in path_x:
            if node == lca:
                break
            reason_str = str(reason)
            if reason_str not in added:
                explanation.append(reason)
                added.add(reason_str)
        for node, reason in path_y:
            if node == lca:
                break
            reason_str = str(reason)
            if reason_str not in added:
                explanation.append(reason)
                added.add(reason_str)
        print(f"; Explanation for why {x} == {y}")
        for step in explanation:
            if step['type'] == 'function':
                a = self.term_to_str(step['arguments'][0])
                b = self.term_to_str(step['arguments'][1])
                print(f"(assert (= {a} {b}))   ; User assertion")
            elif step['type'] == 'derived':
                t1, t2 = step['equiv']
                print(f"; derived: {t1} == {t2}   ; By function congruence")
            elif step['type'] == 'interpreted':
                print(f"; interpreted rule: {step['rule']}   ; Applied theory axiom")

    def path_to_root(self, x):
        path = []
        while x in self.proof_forest:
            parent, reason = self.proof_forest[x]
            path.append((x, reason))
            x = parent
        return path
