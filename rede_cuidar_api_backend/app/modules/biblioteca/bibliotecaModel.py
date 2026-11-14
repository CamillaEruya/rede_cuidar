from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ChatHistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    history: list[ChatHistoryMessage] = Field(default_factory=list, max_length=8)

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("A mensagem não pode estar vazia.")
        return value.strip()


class ChatSource(BaseModel):
    document: str
    page: int


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]


class NewsArticle(BaseModel):
    source: str
    date: str
    title: str
    summary: str
    url: str


class NewsResponse(BaseModel):
    articles: list[NewsArticle]
