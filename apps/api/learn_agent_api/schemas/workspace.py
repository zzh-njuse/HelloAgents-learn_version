from datetime import datetime

from pydantic import BaseModel, Field


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120, pattern=r"\S")
    slug: str | None = Field(default=None, min_length=1, max_length=140, pattern=r"\S")
    description: str | None = Field(default=None, max_length=1000)


class WorkspaceRead(BaseModel):
    id: str
    name: str
    slug: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
