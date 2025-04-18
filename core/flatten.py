def flatten(expression):
    print("I was called")
    if isinstance(expression, dict) and expression.get("type") == "function":
        flat_args = []
        for arg in expression.get("arguments", []):
            flat_args.append(flatten(arg))
        return {
            "type": "function",
            "name": expression["name"],
            "arguments": flat_args
        }

    # If it's a constant like {'type': 'constant', 'value': 'a'} → just return it
    if isinstance(expression, dict) and expression.get("type") == "constant":
        return expression

    # If it's already a string, wrap it
    if isinstance(expression, str):
        return {"type": "constant", "value": expression}

    raise ValueError(f"Unsupported node in flatten(): {expression}")
