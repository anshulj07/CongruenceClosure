from io import StringIO
from flask import Flask, render_template, request, redirect, url_for
from core.closure import CongruenceClosure
from visualizer.graph_utils import visualize_proof_forest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

print("System Path", sys.path)

app = Flask(__name__)
cc = CongruenceClosure()
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    if request.method == "POST":
        action = request.form.get("action")
        expression = request.form.get("expression", "")
        if not expression.strip():
            output += "❌ Error: Input is empty. Please enter two terms or an equation.\n"
            return render_template("index.html", output=output, assertion_log="\n".join(
                cc.term_to_str(eq) for eq in cc.history
            ))

        if action == "assert":
            try:
                parsed = cc.process_input(expression)
                cc.add_equation(parsed)
                output += f"✔ Assertion added: {expression}\n"
            except Exception as e:
                output += f"❌ Error: {e}\n"

        elif action == "explain":
            try:
                output += f"🪵 Raw Input: {expression}\n"

                tokens = cc.tokenize(expression)
                output += f"🧩 Tokens: {tokens}\n"

                if len(tokens) == 2:
                    # Raw two-term input (e.g. "a c" or "f(a) c")

                    def normalize_term(raw):
                        try:
                            term_tokens = cc.tokenize(raw)
                            parsed = cc.parse(term_tokens)
                            curried = cc.curry(parsed)
                            flat = cc.flatten(curried)
                            return cc.term_to_str(flat)
                        except Exception:
                            return raw  # fallback to original if parsing fails

                    t1_raw, t2_raw = tokens
                    t1 = normalize_term(t1_raw)
                    t2 = normalize_term(t2_raw)

                    output += f"📘 Explanation for: {t1} == {t2}\n"

                    if not cc.are_equivalent(t1, t2):
                        output += f"❌ {t1} and {t2} are not equivalent.\n"
                        if (t1, t2) in cc.disequalities or (t2, t1) in cc.disequalities:
                            output += f"; Reason: You asserted they are not equal (disequality).\n"
                        else:
                            output += f"; Reason: They belong to different equivalence classes.\n"
                    else:
                        temp_out = StringIO()
                        sys.stdout = temp_out
                        cc.explain(t1, t2)
                        sys.stdout = sys.__stdout__
                        output += temp_out.getvalue()

                else:
                    # Structured input (e.g. "(= (f a) c)")
                    parsed = cc.parse(tokens)
                    output += f"🧠 Parsed: {parsed}\n"

                    curried = cc.curry(parsed)
                    flat = cc.flatten(curried)
                    output += f"🪜 Curried & Flattened: {flat}\n"

                    if (
                        not isinstance(flat, dict) or
                        flat.get("type") != "function" or
                        len(flat.get("arguments", [])) != 2
                    ):
                        output += "❌ Please enter exactly two terms like: (= (f a) b)\n"
                    else:
                        t1 = cc.term_to_str(flat['arguments'][0])
                        t2 = cc.term_to_str(flat['arguments'][1])
                        output += f"📘 Explanation for: {t1} == {t2}\n"
                        if not cc.are_equivalent(t1, t2):
                            output += f"❌ {t1} and {t2} are not equivalent.\n"
                        else:
                            temp_out = StringIO()
                            sys.stdout = temp_out
                            cc.explain(t1, t2)
                            sys.stdout = sys.__stdout__
                            output += temp_out.getvalue()

                            rep1 = cc.find(t1)
                            rep2 = cc.find(t2)
                            output += f"\n📦 Class of {t1}: {[x for x in cc.parent if cc.find(x) == rep1]}\n"
                            output += f"📦 Class of {t2}: {[x for x in cc.parent if cc.find(x) == rep2]}\n"

            except Exception as e:
                output += f"❌ Error: {e}\n"

        elif action == "show":
            temp_out = StringIO()
            sys.stdout = temp_out
            cc.final_congruence()
            sys.stdout = sys.__stdout__
            output += f"📦 Final Congruence Closure:\n{temp_out.getvalue()}"

        elif action == "visualize":
            try:
                visualize_proof_forest(cc, show=True)
            except Exception as e:
                output += f"❌ Visualization error: {e}\n"

    return render_template("index.html", output=output, assertion_log="\n".join(
        cc.term_to_str(eq) for eq in cc.history
    ))

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("smtfile")
    if file:
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)
        try:
            cc.load_smtlib_file(path)
            msg = f"📄 File loaded: {file.filename}"
        except Exception as e:
            msg = f"❌ Error loading file: {e}"
    else:
        msg = "❌ No file selected."
    return redirect(url_for("index", msg=msg))

if __name__ == "__main__":
    app.run(debug=True)
