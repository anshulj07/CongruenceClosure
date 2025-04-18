import sys
import os
from io import StringIO
from flask import Flask, jsonify, render_template, request, redirect, url_for
from core.closure import CongruenceClosure
import traceback

print(f"✅ Loaded CongruenceClosure from: {CongruenceClosure.__module__}")

# Prevent __pycache__
sys.dont_write_bytecode = True

# Setup Flask
app = Flask(__name__,
            template_folder="web/templates",
            static_folder="web/static")
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Globals
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
                output += f"✔ Added: {expression}\n"
            except Exception as e:
                output += f"❌ Error: {e}\n"

        elif action == "explain":
            print("🧠 cc type:", type(cc))
            print("✅ hasattr are_equivalent:", hasattr(cc, "are_equivalent"))

            try:
                if expression.count(" ") == 1:
                    tokens = cc.tokenize(expression)
                    t1_raw, t2_raw = tokens

                    t1 = cc.term_to_str(cc.process_input(t1_raw))
                    t2 = cc.term_to_str(cc.process_input(t2_raw))

                    output += f"📘 Explanation for: {t1} == {t2}\n"

                    if not cc.are_equivalent(t1, t2):
                        output += f"❌ {t1} and {t2} are not equivalent.\n"
                    else:
                        temp_out = StringIO()
                        sys.stdout = temp_out
                        cc.explain(t1, t2)
                        sys.stdout = sys.__stdout__
                        output += temp_out.getvalue()
                else:
                    parsed_expr = cc.process_input(expression)
                    output += f"📘 Explanation for full expression\n"

                    if (
                        not isinstance(parsed_expr, dict)
                        or parsed_expr.get("type") != "function"
                        or len(parsed_expr.get("arguments", [])) != 2
                    ):
                        output += "❌ Please enter exactly two terms like: (= (f a) b)\n"
                    else:
                        t1 = cc.term_to_str(parsed_expr["arguments"][0])
                        t2 = cc.term_to_str(parsed_expr["arguments"][1])

                        output += f"📘 Explanation for: {t1} == {t2}\n"
                        if not cc.are_equivalent(t1, t2):
                            output += f"❌ {t1} and {t2} are not equivalent.\n"
                        else:
                            temp_out = StringIO()
                            sys.stdout = temp_out
                            cc.explain(t1, t2)
                            sys.stdout = sys.__stdout__
                            output += temp_out.getvalue()
            except Exception as e:
                output += f"❌ Error: {type(e).__name__}: {e}\n"
                output += traceback.format_exc()

        elif action == "show":
            temp_out = StringIO()
            sys.stdout = temp_out
            cc.final_congruence()
            sys.stdout = sys.__stdout__
            output += f"📦 Final Congruence Closure:\n{temp_out.getvalue()}"

        elif action == "pop":
            cc.pop_last_equation()
            output += "↩️ Last assertion removed.\n"

        if output.strip():
            history_blocks.append({
                "expression": expression,
                "action": action,
                "output": output
            })

    return render_template("index.html", history_blocks=history_blocks, output=output,
                           assertion_log="\n".join([cc.term_to_str(eq) for eq in cc.history] + [f"(not (= {a} {b}))" for a, b in cc.disequalities]))

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("smtfile")
    if file:
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)
        try:
            print(f"📂 Loading SMT file from: {path}")
            cc.load_smtlib_file(path)
            msg = f"📄 File loaded: {file.filename}"
        except Exception as e:
            print(f"❌ Error while loading file:\n{e}")
            msg = f"❌ Error loading file: {type(e).__name__}: {e}"
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
    print("🚀 Starting Congruence Closure Web App on http://127.0.0.1:5000")
    app.run(debug=True)
