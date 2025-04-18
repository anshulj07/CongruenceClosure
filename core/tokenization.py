import re

def tokenize(expression, debug_log=None):
    print("I was called: token")
    expression = expression.replace("(", " ( ").replace(")", " ) ").replace(",", " ")
    expression = expression.replace("=", " = ")
    tokens = re.findall(r'\(|\)|[^\s()]+', expression)
    if debug_log is not None:
        debug_log.append(f"🧩 Tokenizing: {expression}")
        debug_log.append(f"🪙 Tokens: {tokens}")
    return tokens


def preprocess_expression(expr):
    """
    Converts f(x) → (f x), g(f(x), y) → (g (f x) y)
    """
    def replacer(match):
        func = match.group(1)
        args = match.group(2)
        return f"({func} {args.replace(',', ' ')})"

    # Replace multiple levels of function calls using regex
    pattern = re.compile(r'(\w+)\(([^()]+)\)')
    prev = None
    while prev != expr:
        prev = expr
        expr = pattern.sub(replacer, expr)
    return expr