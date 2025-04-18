def curry(term):
        print("I was called: curried")
        print("🧱 Input term:", term)

        if not isinstance(term, dict):
            print("⚠️ Term is not a dict, returning as is.")
            return term

        print("📌 Term keys:", term.keys())

        name = term['name']
        print("📛 name:", name)

        args = term.get('arguments', [])
        print("🔁 args:", args)

        if len(args) <= 2:
            return {'type': 'function', 'name': name, 'arguments': args}

        # Start currying by pairing first argument with function name
        curried_term = {'type': 'function', 'name': name, 'arguments': [args[0], args[1]]}

        for arg in args[2:]:
            curried_term = {'type': 'function', 'name': name, 'arguments': [curried_term, arg]}

        return curried_term