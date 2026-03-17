import argparse
import asyncio

import uvicorn

from app.api.admin import app, init_db


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--init-db", action="store_true")
    args = parser.parse_args()

    if args.init_db:
        asyncio.run(init_db())
    else:
        uvicorn.run(app, host="0.0.0.0", port=8000)
