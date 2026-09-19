import os
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class Config:
    secret_key: str
    database_url: str
    debug: bool
    testing: bool
    max_content_length: int = 16 * 1024

    @classmethod
    def from_env(cls, testing: bool = False):
        database_url = os.getenv("DATABASE_URL", "sqlite:///anyama-proxi.db")
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
        elif database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

        secret_key = os.getenv("SECRET_KEY", "")
        if not secret_key and not (testing or os.getenv("FLASK_ENV") == "development"):
            raise RuntimeError("SECRET_KEY doit être défini hors développement.")
        if not secret_key:
            secret_key = "dev-only-change-me"

        if not testing and os.getenv("FLASK_ENV") == "production" and not database_url.startswith("postgresql+psycopg://"):
            raise RuntimeError("DATABASE_URL PostgreSQL/Neon est obligatoire en production.")

        return cls(
            secret_key=secret_key,
            database_url=database_url,
            debug=os.getenv("FLASK_DEBUG", "0") == "1",
            testing=testing,
        )


def validate_database_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"sqlite", "postgresql", "postgresql+psycopg"}
