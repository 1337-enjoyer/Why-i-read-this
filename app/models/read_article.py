import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from .constants import ARTICLE_TITLE_MAX_LENGTH


class ReadArticle(Base):
    __tablename__ = "read_articles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), index=True)
    page_id: Mapped[int]
    title: Mapped[str] = mapped_column(String(ARTICLE_TITLE_MAX_LENGTH))
    read_at: Mapped[datetime] = mapped_column(server_default=func.now())
