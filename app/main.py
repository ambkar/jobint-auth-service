import os
from flask import Flask
from flask_cors import CORS
from .routes import bp

app = Flask(__name__)
app.secret_key = "732e4de0c7203b17f73ca043a7135da261d3bff7c501a1b1451d6e5f412e2396"
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://0.0.0.0:8080"}})
app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)
