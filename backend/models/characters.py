from typing import List

from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .db import db

class Character(db.Model):
    """
    Class for a user with:
        an unique identifier(char_id)
        a name (char_name)
        the user_id of the creator
        a relationship to the creator (creator)
        a picture (char_image)
        a skillset of:
            Str, Dex, Con, Wis, Int, Cha
        detailed description: appearance, backstory, personality
        possible items? TODO
    """
    __tablename__ = "characters"

    __table_args__ = {'extend_existing': True}

    char_id:Mapped[int] = mapped_column(primary_key = True)
    char_name:Mapped[str] = mapped_column(String(100), nullable = False)
    char_image:Mapped[str] = mapped_column(String(500), nullable=True)

    char_personality:Mapped[str] = mapped_column(String(1000), nullable=True)
    char_backstory:Mapped[str] = mapped_column(String(2000), nullable=True)
    char_appearance:Mapped[str] = mapped_column(String(1000), nullable=True)

    strength:Mapped[int] = mapped_column(Integer, default=8, nullable=False)
    dexterity: Mapped[int] = mapped_column(Integer, default=8, nullable=False)
    constitution: Mapped[int] = mapped_column(Integer, default=8, nullable=False)
    intelligence: Mapped[int] = mapped_column(Integer, default=8, nullable=False)
    wisdom: Mapped[int] = mapped_column(Integer, default=8, nullable=False)
    charisma: Mapped[int] = mapped_column(Integer, default=8, nullable=False)

    user_id:Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    creator:Mapped["User"] = relationship(back_populates="created_chars")

    chat_sessions:Mapped[List["ChatHistory"]] = relationship(back_populates="through_char",
                                               lazy="select", cascade="all, delete-orphan")

    def __str__(self):
        return f"Name: {self.name} has following skills:"

    def __repr__(self):
        return f"ID: {self.char_id}, Name: {self.char_name}, user_id:{self.user_id}"
