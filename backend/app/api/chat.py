import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse

from app.deps.auth import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest
from app.services.llm_service import stream_chat

router = APIRouter(prefix="/api/chat", tags=["chat"])


async def _event_generator(message: str) -> AsyncIterator[dict]:
    """将 LLM 流式片段封装为 SSE 事件流：message → done / error。"""
    try:
        async for piece in stream_chat(message):
            yield {
                "event": "message",
                "data": json.dumps({"delta": piece}, ensure_ascii=False),
            }
        yield {"event": "done", "data": json.dumps({"finish_reason": "stop"})}
    except Exception as exc:  # noqa: BLE001
        # 出错时下发 error 事件，前端可据此提示用户
        yield {
            "event": "error",
            "data": json.dumps({"message": str(exc)}, ensure_ascii=False),
        }


@router.post("/stream")
async def chat_stream(
    req: ChatRequest,
    current: User = Depends(get_current_user),
) -> EventSourceResponse:
    """SSE 流式对话接口，需要 Bearer 认证。"""
    return EventSourceResponse(_event_generator(req.message))
