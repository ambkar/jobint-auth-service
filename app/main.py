from flask import Flask
from flask_cors import CORS
from .routes import bp

app = Flask(__name__)
app.config.from_envvar('APP_CONFIG_FILE', silent=True)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://0.0.0.0:8080"}})
app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
