from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application configuration, loaded from environment / .env.

    IMPORTANT: this is the only place environment variables are read.
    Application logic must never hard-code secrets, model names, or
    provider choices - everything flows from here.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM provider abstraction
    llm_provider: str = "openai"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    mock_llm: bool = True

    # Security
    jwt_secret: str = "change-this-demo-secret-in-any-real-deployment"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 480

    # Database
    database_url: str = "sqlite:///./securemed.db"

    # App
    demo_mode: bool = True
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def effective_mock_mode(self) -> bool:
        """The app runs in Mock LLM mode if explicitly requested, or if
        no API key is configured. This guarantees a live demo never fails
        because of a missing key, network issue, or quota problem."""
        return self.mock_llm or not self.openai_api_key.strip()


settings = Settings()
