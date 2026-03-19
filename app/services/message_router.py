from dataclasses import dataclass

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Trigger
from app.services.profanity_filter import ProfanityFilter
from app.services.response_builder import build_response


@dataclass(slots=True)
class RouteResult:
    response_text: str
    should_generate_voice: bool
    matched_trigger: str | None = None
    matched_patterns: list[str] | None = None


profanity_filter = ProfanityFilter()


async def route_message(session: AsyncSession, platform: str, text: str) -> RouteResult | None:
    stmt = select(Trigger).where(
        Trigger.is_active.is_(True),
        or_(Trigger.platform == platform, Trigger.platform == "all"),
    )
    triggers = (await session.execute(stmt)).scalars().all()

    lowered = text.lower()
    for trigger in triggers:
        if trigger.pattern.lower() in lowered:
            response = await build_response(session, trigger.id)
            return RouteResult(
                response_text=response,
                should_generate_voice=True,
                matched_trigger=trigger.pattern,
            )

    profanity_matches = profanity_filter.find_matches(text)
    if profanity_matches:
        response = await build_response(session)
        return RouteResult(
            response_text=response,
            should_generate_voice=True,
            matched_patterns=[match.fragment for match in profanity_matches],
        )

    return None
