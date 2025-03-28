from core.closure import CongruenceClosure
from visualizer.graph_utils import visualize_proof_forest

def run_cli():
    cc = CongruenceClosure()
    print("📘 Congruence Closure CLI\nType 'help' for commands.\n")

    while True:
        try:
            cmd = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting CLI.")
            break

        if cmd == "exit":
            break
        elif cmd.startswith("assert "):
            try:
                parsed = cc.process_input(cmd[len("assert "):])
                cc.add_equation(parsed)
            except Exception as e:
                print(f"❌ Error: {e}")
        elif cmd.startswith("explain "):
            try:
                x, y = cmd[len("explain "):].split()
                cc.explain(x, y)
            except Exception as e:
                print(f"❌ Error: {e}")
        elif cmd.startswith("equiv "):
            try:
                x, y = cmd[len("equiv "):].split()
                print("✅ Equivalent" if cc.are_equivalent(x, y) else "❌ Not equivalent")
            except Exception as e:
                print(f"❌ Error: {e}")
        elif cmd.startswith("load "):
            try:
                path = cmd[len("load "):].strip()
                cc.load_smtlib_file(path)
                print(f"✅ Loaded: {path}")
            except Exception as e:
                print(f"❌ Could not load file: {e}")
        elif cmd == "show":
            cc.final_congruence()
        elif cmd == "viz":
            visualize_proof_forest(cc)

        elif cmd == "viz save":
            visualize_proof_forest(cc, show=True, save_as="proof.png")

        elif cmd == "help":
            print("Commands:")
            print("  assert (= a b)         - Add an equality")
            print("  assert (!= a b)        - Add a disequality")
            print("  explain a b            - Show explanation for a == b")
            print("  equiv a b              - Check if a and b are equivalent")
            print("  load path/to/file.smt2 - Load .smt2 file")
            print("  show                   - Show equivalence classes")
            print("  viz                    - Visualize proof forest")
            print("  exit                   - Quit")
        else:
            print("Unknown command. Type 'help'.")

if __name__ == "__main__":
    run_cli()
