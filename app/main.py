# app/main.py
from sanic import Sanic
from sanic_ext import Extend
from app.api.v1.auth_routes import auth_bp
from app.api.v1.user_routes import user_bp
from app.core.config import settings
from sanic.response import json 

app = Sanic(settings.project_name)          # --- app уже создан
Extend(app)

app.blueprint(auth_bp)
app.blueprint(user_bp)

@app.get("/health")
async def health(_):
    return json({"status": "ok"})


if __name__ == "__main__":
    # dev-режим, без форков
    app.run(host="0.0.0.0", port=8001, workers=1, dev=True)
