from sanic import Sanic, response
from sanic_ext import Extend
from app.database import engine, Base
from app.routes import bp as api_bp
from app.auth import auth_bp
from sanic_cors import CORS

app = Sanic("AuthService")

CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://0.0.0.0:8080"}})

app.config.API_TITLE = "Jobint Auth Service"
app.config.API_VERSION = "1.0.0"
app.config.API_DESCRIPTION = "Микросервис авторизации (регистрация, логин, /me)."

Extend(app, openapi_definitions=True)

@app.before_server_start
async def create_schema(app, _):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health(_request):
    return response.json({"status": "ok"})

app.blueprint(api_bp)
app.blueprint(auth_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
