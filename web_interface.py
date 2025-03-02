from flask import Flask, render_template, request, jsonify, send_file
import math
import fractions
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json()
    expression = data.get("expression", "")
    try:
        allowed_globals = {"__builtins__": None, "math": math, "fractions": fractions}
        result = str(eval(expression, allowed_globals, {}))
    except Exception as e:
        result = "Error"
    return jsonify({"result": result})

@app.route("/plot", methods=["POST"])
def plot():
    data = request.get_json()
    func_str = data.get("function", "")
    try:
        x_min = float(data.get("x_min", 0))
        x_max = float(data.get("x_max", 10))
        if x_min >= x_max:
            return jsonify({"error": "x_min must be less than x_max"}), 400
        xs = [x_min + i*(x_max - x_min)/1000 for i in range(1001)]
        ys = []
        allowed_names = {"x": 0, "sin": math.sin, "cos": math.cos, "tan": math.tan,
                         "sqrt": math.sqrt, "log": math.log, "log10": math.log10, "pi": math.pi,
                         "e": math.e, "abs": abs, "pow": pow}
        for x in xs:
            allowed_names["x"] = x
            y = eval(func_str, {"__builtins__": {}}, allowed_names)
            ys.append(y)
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.plot(xs, ys)
        ax.set_title(f"f(x) = {func_str}")
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        plt.close(fig)
        return send_file(buf, mimetype="image/png")
    except Exception as e:
        return jsonify({"error": "Error in function evaluation"}), 400

if __name__ == "__main__":
    app.run(debug=True)
