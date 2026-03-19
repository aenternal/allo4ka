import argparse
from pathlib import Path

import uvicorn
from alembic import command
from alembic.config import Config

from app.api.admin import app


BASE_DIR = Path(__file__).resolve().parent


def run_migrations() -> None:
    alembic_config = Config(str(BASE_DIR / "alembic.ini"))
    command.upgrade(alembic_config, "head")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--init-db", action="store_true")
    args = parser.parse_args()

    if args.init_db:
        run_migrations()
    else:
        uvicorn.run(app, host="0.0.0.0", port=8000)
