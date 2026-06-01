from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """对话请求体，单轮用户消息。"""

    message: str = Field(min_length=1, max_length=4000)
