from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import engine, get_session
from app.models import Base, ResponseFragments, ResponseTemplate, Trigger

app = FastAPI(title="Allo4ka Admin API")


class TriggerIn(BaseModel):
    platform: str = "all"
    pattern: str
    response_id: int | None = None
    is_active: bool = True


class TriggerPatch(BaseModel):
    pattern: str | None = None
    response_id: int | None = None
    is_active: bool | None = None


class ResponseIn(BaseModel):
    text: str
    voice_enabled: bool = True


class FragmentsIn(BaseModel):
    part1: str
    part2: str
    part3: str
    part4: str


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/triggers")
async def create_trigger(payload: TriggerIn, session: AsyncSession = Depends(get_session)) -> dict:
    obj = Trigger(**payload.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return {"id": obj.id}


@app.get("/triggers")
async def list_triggers(session: AsyncSession = Depends(get_session)) -> list[dict]:
    rows = (await session.execute(select(Trigger))).scalars().all()
    return [
        {
            "id": r.id,
            "platform": r.platform,
            "pattern": r.pattern,
            "response_id": r.response_id,
            "is_active": r.is_active,
        }
        for r in rows
    ]


@app.patch("/triggers/{trigger_id}")
async def patch_trigger(trigger_id: int, payload: TriggerPatch, session: AsyncSession = Depends(get_session)) -> dict:
    obj = await session.get(Trigger, trigger_id)
    if obj is None:
        return {"updated": False}

    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(obj, key, value)

    await session.commit()
    return {"updated": True}


@app.post("/responses")
async def create_response(payload: ResponseIn, session: AsyncSession = Depends(get_session)) -> dict:
    obj = ResponseTemplate(**payload.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return {"id": obj.id}


@app.get("/responses")
async def list_responses(session: AsyncSession = Depends(get_session)) -> list[dict]:
    rows = (await session.execute(select(ResponseTemplate))).scalars().all()
    return [{"id": r.id, "text": r.text, "voice_enabled": r.voice_enabled} for r in rows]


@app.post("/fragments")
async def create_fragments(payload: FragmentsIn, session: AsyncSession = Depends(get_session)) -> dict:
    obj = ResponseFragments(**payload.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return {"id": obj.id}


@app.get("/fragments")
async def list_fragments(session: AsyncSession = Depends(get_session)) -> list[dict]:
    rows = (await session.execute(select(ResponseFragments))).scalars().all()
    return [
        {
            "id": r.id,
            "part1": r.part1,
            "part2": r.part2,
            "part3": r.part3,
            "part4": r.part4,
        }
        for r in rows
    ]


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
