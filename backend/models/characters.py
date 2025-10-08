from typing import List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .db import db

class Character(db.Model):
    """
    Class for a user with:
        an unique identifier(char_id)
        a name (char_name)
        the user_id of the creator
        a relationship to the creator (creator)
        a picture TODO
        a skillset of:
            TODO
        possible items?TODO
        backstory TODO
    """
    __tablename__ = "characters"

    __table_args__ = {'extend_existing': True}

    char_id:Mapped[int] = mapped_column(primary_key = True)
    char_name:Mapped[str] = mapped_column(String(100), nullable = False)

    user_id:Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    creator:Mapped["User"] = relationship(back_populates="created_chars")

    chat_sessions:Mapped[List["ChatHistory"]] = relationship(back_populates="through_char",
                                               clazy="dynamic", cascade="all, delete-orphan")

    def __str__(self):
        return f"Name: {self.name} has following skills:"

    def __repr__(self):
        return f"ID: {self.char_id}, Name: {self.char_name}, user_id:{self.user_id}"
