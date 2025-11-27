from functools import lru_cache
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    APP_NAME: str = "Gene API"
    APP_ENV: str = "development"

    # Server (used by README examples; uvicorn CLI can override)
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    APP_RELOAD: bool = True

    # CORS
    CORS_ORIGINS: list[str] | str = "*"

    # Database (可为空，便于无 DB 启动)
    DATABASE_URL: str | None = None

    # WeChat Mini Program
    WX_APPID: str | None = None
    WX_SECRET: str | None = None
    WX_JSCODE2SESSION_URL: str = "https://api.weixin.qq.com/sns/jscode2session"
    WX_GRANT_TYPE: str = "authorization_code"

    def _normalize_cors(self) -> list[str]:
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        if isinstance(self.CORS_ORIGINS, str):
            return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]
        return ["*"]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    s = Settings()
    # Normalize CORS
    object.__setattr__(s, "CORS_ORIGINS", s._normalize_cors())
    return s


settings: Settings = get_settings()


class Info(BaseModel):
    name: str
    env: str
