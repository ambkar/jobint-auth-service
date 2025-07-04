from sanic import Sanic, response
from sanic_ext import Extend
from app.database import engine, Base
from app.routes import bp as api_bp
from app.auth import auth_bp
from sanic_cors import CORS

# ─────────── создание приложения ───────────
app = Sanic("AuthService")
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://0.0.0.0:8080"}})

# Метаданные, которые попадут в OpenAPI /docs
app.config.API_TITLE = "Jobint Auth Service"
app.config.API_VERSION = "1.0.0"
app.config.API_DESCRIPTION = "Микросервис авторизации (регистрация, логин, /me)."

# Подключаем sanic-ext с поддержкой OpenAPI и Pydantic-валидации
Extend(app, openapi_definitions=True)

# ─────────── создаём схему БД перед стартом ───────────
@app.before_server_start
async def create_schema(app, _):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ─────────── health-endpoint ───────────
@app.get("/health")
async def health(_request):
    return response.json({"status": "ok"})


# ─────────── регистрируем blueprints ───────────
app.blueprint(api_bp)    # /api/v1/auth/register + /login
app.blueprint(auth_bp)   # /api/v1/auth/me (защищённый)

# ─────────── запуск ───────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
