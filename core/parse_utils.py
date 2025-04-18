def parse(tokens):
    print("I was called: parse")
    def parse_term():
        if not tokens:
            raise ValueError("Unexpected EOF while parsing")

        token = tokens.pop(0)

        if token == '(':
            if not tokens:
                raise ValueError("Unexpected end after '('")
            func_name = tokens.pop(0)
            args = []
            while tokens and tokens[0] != ')':
                args.append(parse_term())
            if not tokens or tokens[0] != ')':
                raise ValueError("Expected ')' to close function call")
            tokens.pop(0)  # remove ')'
            return {
                'type': 'function',
                'name': func_name,
                'arguments': args
            }
        elif token == ')':
            raise ValueError("Unexpected ')' without matching '('")
        else:
            return {
                'type': 'constant',
                'value': token
            }

    return parse_term()