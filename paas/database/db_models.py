from datetime import datetime

from sqlmodel import Field, SQLModel


class Links(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    original_url: str = Field(index=True)
    short_name: str = Field(unique=True, index=True)
    short_url: str = Field()
    created_at: datetime = Field(default_factory=datetime.now)
