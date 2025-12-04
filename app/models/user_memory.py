from sqlalchemy import Integer, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from ..database import Base


def default_memory_json():
    return {
        "identity": {
            "name": None,
            "age": None,
            "cities": [],
            "education": [],
            "roles": []
        },
        "preferences": {
            "food": [],
            "movies": [],
            "activities": [],
            "music": [],
            "other": []
        },
        "personality": {
            "tone": [],
            "traits": []
        },
        "emotions": {
            "recurring": [],
            "occasional": []
        },
        "skills": [],
        "goals": {
            "short_term": [],
            "long_term": []
        },
        "bio_summary": ""
    }


class UserMemory(Base):
    __tablename__ = "user_memories"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)

    memory_json: Mapped[dict] = mapped_column(JSON, default=default_memory_json)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user = relationship("User", back_populates="memory")
