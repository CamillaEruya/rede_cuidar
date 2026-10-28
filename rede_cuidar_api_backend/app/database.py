import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


def _database_url() -> str:
    driver = os.getenv("DB_CONNECTION", "sqlite").lower()

    if driver == "sqlite":
        database = os.getenv("DB_DATABASE", "database.sqlite")
        database_path = Path(database)
        if not database_path.is_absolute():
            database_path = ROOT_DIR / database_path
        return f"sqlite:///{database_path.as_posix()}"

    if driver in {"mysql", "mysql+pymysql"}:
        host = os.getenv("DB_HOST", "127.0.0.1")
        port = os.getenv("DB_PORT", "3306")
        username = os.getenv("DB_USERNAME", "root")
        password = os.getenv("DB_PASSWORD", "")
        database = os.getenv("DB_DATABASE", "")
        return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"

    raise ValueError(f"DB_CONNECTION não suportado: {driver}")


engine: Engine = create_engine(_database_url(), pool_pre_ping=True)
