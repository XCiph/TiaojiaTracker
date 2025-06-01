from flask import Flask, request, jsonify
from flask_cors import CORS
from optimizer import solve_adjustment

app = Flask(__name__)
CORS(app)

@app.route("/api/solve", methods=["POST"])
def solve():
    data = request.get_json()

    result = solve_adjustment(
        base_price=data["base_price"],
        role_names=data["role_names"],
        role_counts=data["role_counts"],
        popularity=data["popularity"],
        integer_only=data.get("integer_only", True),
        max_adj=data.get("max_adj"),
        min_adj=data.get("min_adj"),
        popularity_levels=data.get("popularity_levels")
    )
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
