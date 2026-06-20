"""Configuration and environment variable handling."""
import os


def get_env(name: str, default: str | None = None) -> str:
    """Get environment variable with optional default."""
    value = os.environ.get(name, default)
    if value is None:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def build_db_connections() -> tuple[dict, dict]:
    """Build PostgreSQL and MySQL connection configurations."""
    postgres_config = {
        "host": get_env("MT_POSTGRES_HOST"),
        "port": int(get_env("MT_POSTGRES_PORT", "5432")),
        "dbname": get_env("POSTGRES_DB"),
        "user": get_env("POSTGRES_USER"),
        "password": get_env("POSTGRES_PASSWORD"),
    }
    mysql_config = {
        "host": get_env("MT_MYSQL_HOST"),
        "port": int(get_env("MT_MYSQL_PORT", "3306")),
        "user": get_env("MYSQL_USER", "root"),
        "password": get_env("MYSQL_ROOT_PASSWORD"),
        "database": get_env("MYSQL_DATABASE"),
    }
    return postgres_config, mysql_config
