from collections.abc import AsyncIterator

from langchain_deepseek import ChatDeepSeek

from app.config import get_settings


def _build_llm() -> ChatDeepSeek:
    """根据配置构建 ChatDeepSeek 客户端，开启流式输出。"""
    settings = get_settings()
    return ChatDeepSeek(
        model=settings.deepseek_model,
        api_key=settings.deepseek_api_key,
        temperature=0.3,
        max_retries=2,
        streaming=True,
    )


async def stream_chat(user_message: str) -> AsyncIterator[str]:
    """对外暴露：传入用户单轮文本，异步产出 LLM 文本片段。

    第一步仅做单轮无记忆调用，后续接入对话记忆 / LangGraph 时只需替换此函数。
    """
    llm = _build_llm()
    messages = [
        ("system", "你是灵工企业风控 Agent 系统的智能助手，回答专业且简洁。"),
        ("human", user_message),
    ]
    async for chunk in llm.astream(messages):
        text = getattr(chunk, "content", "")
        if text:
            yield text
