# app.py
import asyncio
from sanic import Sanic, response
from sanic_ext import Extend

from database import engine, Base
from routes import bp as auth_api
from auth import auth_bp as guard_bp

app = Sanic("AuthService")
app.config.SECRET = "732e4de0c7203b17f73ca043a7135da261d3bff7c501a1b1451d6e5f412e2396"
Extend(app)


@app.before_server_start
async def create_schema(app, _):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# health-check
@app.get("/health")
async def health(_request):
    return response.json({"status": "ok"})


app.blueprint(auth_api)   # POST /api/v1/auth/register, /login
app.blueprint(guard_bp)   # GET  /api/v1/auth/me (protected)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
