"""Legacy entrypoint kept for backward compatibility."""

from run_bots import main

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
