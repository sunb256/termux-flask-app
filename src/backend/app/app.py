from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory


WEB_DIR = Path(__file__).resolve().parent / "web"


def create_app() -> Flask:
    app = Flask(__name__)

    # ----------
    # - API
    # ----------

    @app.get("/api/health")
    def health():
        return jsonify(
            status="ok",
            message="Flask API is running",
        )

    @app.post("/api/echo")
    def echo():
        data = request.get_json(silent=True) or {}

        return jsonify(
            message=data.get("message", ""),
        )

    # ----------
    # - React
    # ----------

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def frontend(path: str):
      
        # 存在しないAPIをReactへ流さない
        if path.startswith("api/"):
            return jsonify(error="Not found"), 404

        target = WEB_DIR / path

        if path and target.is_file():
            return send_from_directory(WEB_DIR, path)

        return send_from_directory(WEB_DIR, "index.html")

    return app