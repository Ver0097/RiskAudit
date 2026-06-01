import pytest
from unittest.mock import patch

from app.services import llm_service


class _Chunk:
    """模拟 LangChain 流式片段。"""

    def __init__(self, content: str):
        self.content = content


@pytest.mark.asyncio
async def test_stream_chat_yields_text_chunks():
    async def fake_astream(messages):
        for c in [_Chunk("你"), _Chunk("好"), _Chunk("！")]:
            yield c

    with patch.object(llm_service, "_build_llm") as build:
        llm = build.return_value
        llm.astream = fake_astream
        chunks = [c async for c in llm_service.stream_chat("hi")]
    assert "".join(chunks) == "你好！"
