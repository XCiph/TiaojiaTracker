from flask import Flask, request, jsonify
from flask_cors import CORS  # 允许跨域
from optimizer import solve_multiple_adjustments

app = Flask(__name__)
CORS(app)  # 允许前端 localhost:5173 访问（Vite 默认端口）

@app.route("/api/solve", methods=["POST"])
def solve():
    data = request.get_json()
    result = solve_multiple_adjustments(
        base_price=data["base_price"],
        role_names=data["role_names"],
        role_counts=data["role_counts"],
        popularity=data["popularity"],
        integer_only=data.get("integer_only", True),
        max_adj=data.get("max_adj"),
        min_adj=data.get("min_adj"),
        max_solutions=10
    )
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
