from typing import List
from sqlalchemy import String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from StoryAI.backend.models.chat_history import ChatHistory
from .db import db

class User(db.Model):
    """
    Class for a user with:
        a unique identifier(user_id)
        a unique name(username)
        a list of created chars(max. 3)
    """
    __tablename__ = "users"

    __table_args__ = {'extend_existing': True}

    user_id:Mapped[int] = mapped_column(primary_key = True)
    username:Mapped[str] = mapped_column(String(30), nullable = False, unique = True)

    created_chars:Mapped[List["Character"]] = relationship(back_populates="creator",
                                                           lazy= "dynamic", cascade= "all, delete-orphan")
    chats:Mapped["ChatHistory"] = relationship(back_populates="chatted_with",
                                               clazy="dynamic", cascade="all, delete-orphan")
    def __str__(self):
        return f"Username:{self.username} created following characters: {self.created_chars}"

    def __repr__(self):
        return f"ID: {self.user_id}, Name: {self.username}, Chars: {self.created_chars}"