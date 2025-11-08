from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, DateTime, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .db import db

class ChatHistory(db.Model):
    """
    Class to save the history of the Chat with AI
    """
    __tablename__ = "chat_history"

    __table_args__ = {'extend_existing': True}

    chat_id:Mapped[int] = mapped_column(primary_key = True)
    message:Mapped[str] = mapped_column(Text, nullable=False)
    role:Mapped[str] = mapped_column(String, nullable=False)
    created:Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    thread_id:Mapped[int] = mapped_column(Integer, nullable=False)

    user_id:Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    chatted_with:Mapped["User"] = relationship(back_populates="chats")

    char_id:Mapped[int] = mapped_column(ForeignKey("characters.char_id"))
    through_char:Mapped["Character"] = relationship(back_populates="chat_sessions")

