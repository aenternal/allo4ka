import asyncio

from app.bots.telegram_bot import run_telegram
from app.bots.vk_bot import run_vk


async def main() -> None:
    await asyncio.gather(run_telegram(), run_vk())


if __name__ == "__main__":
    asyncio.run(main())
