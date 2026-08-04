# Dead simple session-scoped conversation history, stored in Redis.
# No accounts here — session_id is just a random token the client hangs onto,
# purely for "remember the last few messages," not identity.

import json
from redis import asyncio as aioredis

SESSION_TTL_SECONDS = 1800   # session dies after 30 min of silence
MAX_STORED_TURNS = 10        # user+assistant pairs we keep in Redis (separate from
                              # how many we actually feed the LLM per call — see main.py)

redis_client = aioredis.from_url("redis://localhost:6379", decode_responses=True)


def _key(session_id: str) -> str:
    return f"session:{session_id}:history"


async def get_history(session_id: str) -> list[dict]:
    """Grab whatever we've got for this session. If Redis is down, just
    return no history instead of blowing up the request — worst case
    the chat behaves like single-turn again (NFR5, graceful degradation)."""
    if not session_id:
        return []
    try:
        raw = await redis_client.lrange(_key(session_id), 0, -1)
        return [json.loads(item) for item in raw]
    except Exception as e:
        print(f"[DEV WARNING] couldn't read session history: {e}")
        return []


async def append_turn(session_id: str, role: str, content: str) -> None:
    """Tack a message onto the session, trim it back down to MAX_STORED_TURNS,
    and refresh the TTL so active sessions don't expire mid-chat.
    Best-effort — a failed write here shouldn't fail the request."""
    if not session_id:
        return
    try:
        key = _key(session_id)
        await redis_client.rpush(key, json.dumps({"role": role, "content": content}))
        await redis_client.ltrim(key, -(MAX_STORED_TURNS * 2), -1)
        await redis_client.expire(key, SESSION_TTL_SECONDS)
    except Exception as e:
        print(f"[DEV WARNING] couldn't save session turn: {e}")

def trim_history(history: list[dict] | None, max_turns: int) -> list[dict]:
    """Cut history down to the last `max_turns` user+assistant pairs before
    we hand it to an LLM call. Separate from MAX_STORED_TURNS above —
    that controls what we keep in Redis, this controls what we actually
    spend tokens on per call (classifier gets way less than main_llm)."""
    if not history:
        return []
    return history[-(max_turns * 2):]        