"""Request/response models for the College Helpdesk Chatbot API."""

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(3, ge=1, le=5)


class Source(BaseModel):
    source: str
    score: float


class AskResponse(BaseModel):
    answer: str
    sources: list[Source] = []


class AddDocRequest(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)


class DocInfo(BaseModel):
    source: str
    chunks: int
