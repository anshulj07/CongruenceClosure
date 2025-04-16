from io import StringIO
from flask import Flask, jsonify, render_template, request, redirect, url_for
from core.closure import CongruenceClosure
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

print("System Path", sys.path)

app = Flask(__name__,
        template_folder="web/templates",
        static_folder="web/static")

app.config['TEMPLATES_AUTO_RELOAD'] = True

cc = CongruenceClosure()
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

history_blocks = []

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""

    if request.method == "POST":
        action = request.form.get("action")
        expression = request.form.get("expression", "")

        if not action:
            return render_template("index.html", history_blocks=history_blocks, output="", assertion_log="")

        if action in ["assert", "explain"] and not expression.strip():
            output += "❌ Error: Input is empty. Please enter two terms or an equation.\n"
            return render_template("index.html", history_blocks=history_blocks, output=output)

        if action == "assert":
            try:
                parsed = cc.process_input(expression)
                cc.add_equation(parsed)
                output += cc.debug_log
            except Exception as e:
                output += f"❌ Error: {e}\n"

        elif action == "explain":
            try:
                if expression.count(" ") == 1:
                    # Raw input like "a c"
                    tokens = cc.tokenize(expression)
                    t1_raw, t2_raw = tokens

                    def normalize_term(raw):
                        term_expr = cc.process_input(raw)
                        return cc.term_to_str(term_expr)

                    t1 = normalize_term(t1_raw)
                    t2 = normalize_term(t2_raw)

                    output += cc.debug_log
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
                    # Full SMT-like structured expression
                    parsed_expr = cc.process_input(expression)
                    output += cc.debug_log

                    if (
                        not isinstance(parsed_expr, dict) or
                        parsed_expr.get("type") != "function" or
                        len(parsed_expr.get("arguments", [])) != 2
                    ):
                        output += "❌ Please enter exactly two terms like: (= (f a) b)\n"
                    else:
                        t1 = cc.term_to_str(parsed_expr['arguments'][0])
                        t2 = cc.term_to_str(parsed_expr['arguments'][1])
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

        if output.strip():  # Only append if something was generated
            history_blocks.append({
                "expression": expression,
                "action": action,
                "output": output
            })

    return render_template("index.html", history_blocks=history_blocks, output=output, assertion_log="\n".join(
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


@app.route("/tree", methods=["POST"])
def get_expression_tree():
    expression = request.form.get("expression", "")
    try:
        tree = cc.process_input(expression)
        return jsonify(tree)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)


