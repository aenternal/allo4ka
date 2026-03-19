from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app.db import get_session
from app.models import AudioCache, ResponseFragments, ResponseTemplate, Trigger, TriggerResponseLink
from app.services.pre_generation import list_audio_cache
from app.tasks.jobs import pregenerate_voice

settings = get_settings()
WEB_DIR = Path(__file__).resolve().parent.parent / "web"

app = FastAPI(title="Allo4ka Admin API")
app.add_middleware(SessionMiddleware, secret_key=settings.admin_session_secret)
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


class LoginIn(BaseModel):
    username: str
    password: str


class TriggerIn(BaseModel):
    platform: str = "all"
    pattern: str
    is_active: bool = True


class TriggerPatch(BaseModel):
    pattern: str | None = None
    is_active: bool | None = None


class ResponseIn(BaseModel):
    text: str
    voice_enabled: bool = True


class TriggerResponseLinkIn(BaseModel):
    trigger_id: int
    response_id: int


class FragmentsIn(BaseModel):
    part1: str
    part2: str
    part3: str
    part4: str


class VoicePregenerationIn(BaseModel):
    fragment_count: int = 10


async def require_admin(request: Request) -> None:
    if request.session.get("is_admin") is not True:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
async def root() -> RedirectResponse:
    return RedirectResponse(url="/admin", status_code=302)


@app.get("/login")
async def login_page() -> FileResponse:
    return FileResponse(WEB_DIR / "login.html")


@app.get("/admin")
async def admin_page(request: Request) -> FileResponse | RedirectResponse:
    if request.session.get("is_admin") is not True:
        return RedirectResponse(url="/login", status_code=302)
    return FileResponse(WEB_DIR / "admin.html")


@app.post("/auth/login")
async def login(payload: LoginIn, request: Request) -> dict[str, bool]:
    if payload.username != settings.admin_username or payload.password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    request.session["is_admin"] = True
    request.session["username"] = payload.username
    return {"ok": True}


@app.post("/auth/logout")
async def logout(request: Request, _: None = Depends(require_admin)) -> dict[str, bool]:
    request.session.clear()
    return {"ok": True}


@app.get("/auth/me")
async def auth_me(request: Request, _: None = Depends(require_admin)) -> dict[str, str]:
    return {"username": request.session.get("username", settings.admin_username)}


@app.post("/triggers")
async def create_trigger(
    payload: TriggerIn,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_admin),
) -> dict:
    obj = Trigger(**payload.model_dump())
    session.add(obj)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Trigger must be unique per platform.") from exc
    await session.refresh(obj)
    return {"id": obj.id}


@app.get("/triggers")
async def list_triggers(
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_admin),
) -> list[dict]:
    rows = (await session.execute(select(Trigger))).scalars().all()
    return [
        {
            "id": r.id,
            "platform": r.platform,
            "pattern": r.pattern,
            "is_active": r.is_active,
        }
        for r in rows
    ]


@app.patch("/triggers/{trigger_id}")
async def patch_trigger(
    trigger_id: int,
    payload: TriggerPatch,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_admin),
) -> dict:
    obj = await session.get(Trigger, trigger_id)
    if obj is None:
        return {"updated": False}

    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(obj, key, value)

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Trigger must be unique per platform.") from exc
    return {"updated": True}


@app.post("/responses")
async def create_response(
    payload: ResponseIn,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_admin),
) -> dict:
    obj = ResponseTemplate(**payload.model_dump())
    session.add(obj)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Response text must be unique.") from exc
    await session.refresh(obj)
    return {"id": obj.id}


@app.get("/responses")
async def list_responses(
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_admin),
) -> list[dict]:
    rows = (await session.execute(select(ResponseTemplate))).scalars().all()
    return [{"id": r.id, "text": r.text, "voice_enabled": r.voice_enabled} for r in rows]


@app.post("/trigger-responses")
async def create_trigger_response_link(
    payload: TriggerResponseLinkIn,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_admin),
) -> dict:
    trigger = await session.get(Trigger, payload.trigger_id)
    response = await session.get(ResponseTemplate, payload.response_id)
    if trigger is None or response is None:
        raise HTTPException(status_code=404, detail="Trigger or response not found.")

    obj = TriggerResponseLink(**payload.model_dump())
    session.add(obj)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Trigger-response relation must be unique.") from exc
    await session.refresh(obj)
    return {"id": obj.id}


@app.get("/trigger-responses")
async def list_trigger_response_links(
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_admin),
) -> list[dict]:
    rows = (await session.execute(select(TriggerResponseLink))).scalars().all()
    return [{"id": r.id, "trigger_id": r.trigger_id, "response_id": r.response_id} for r in rows]


@app.post("/fragments")
async def create_fragments(
    payload: FragmentsIn,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_admin),
) -> dict:
    obj = ResponseFragments(**payload.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return {"id": obj.id}


@app.get("/fragments")
async def list_fragments(
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_admin),
) -> list[dict]:
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


@app.post("/voice-pregeneration")
async def start_voice_pregeneration(payload: VoicePregenerationIn, _: None = Depends(require_admin)) -> dict:
    task = pregenerate_voice.delay(payload.fragment_count)
    return {"task_id": task.id, "fragment_count": payload.fragment_count}


@app.get("/audio-cache")
async def get_audio_cache(
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_admin),
) -> list[dict]:
    rows = await list_audio_cache(session)
    return [
        {
            "id": r.id,
            "text": r.text,
            "file_path": r.file_path,
        }
        for r in rows
    ]
