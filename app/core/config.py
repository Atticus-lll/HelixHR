import os
from pathlib import Path

from pydantic import BaseModel


def load_env_file() -> None:
    env_path = Path('.env')
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        os.environ.setdefault(key.strip(), value.strip())


load_env_file()


class Settings(BaseModel):
    app_name: str = os.getenv('APP_NAME', 'AI驱动的人力资源系统')
    app_version: str = os.getenv('APP_VERSION', '0.1.0')
    debug: bool = os.getenv('APP_DEBUG', 'true').lower() == 'true'
    database_url: str = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:yzx200391@localhost:3308/test_db?charset=utf8mb4',
    )
    secret_key: str = os.getenv('SECRET_KEY', 'fastapi-project-dev-secret-key')
    access_token_expire_minutes: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '120'))
    admin_username: str = os.getenv('ADMIN_USERNAME', 'admin')
    admin_password: str = os.getenv('ADMIN_PASSWORD', 'admin123456')
    admin_role_name: str = os.getenv('ADMIN_ROLE_NAME', '系统管理员')
    openai_api_key: str = os.getenv('OPENAI_API_KEY', '')


settings = Settings()
