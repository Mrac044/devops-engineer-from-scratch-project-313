from sqlmodel import Field, SQLModel
from datetime import datetime
import sqlalchemy as sa


class Links(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    original_url: str = Field(index=True)
    short_name: str = Field(unique=True, index=True)
    short_url: str = Field()
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    )
