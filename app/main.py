from sanic import Sanic, response
from sanic_ext import Extend
from app.database import engine, Base
from app.routes import bp as api_bp
from app.auth import auth_bp

app = Sanic("AuthService")
Extend(app)

@app.before_server_start
async def create_schema(app, _):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health(_):                                              # GET /health
    return response.json({"status": "ok"})

app.blueprint(api_bp)   # /api/v1/auth/register, /login
app.blueprint(auth_bp)  # /api/v1/auth/me

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
