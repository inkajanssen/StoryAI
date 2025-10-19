class ChatManager:

    def __init__(self, db_instance, chat_history):
        self.db = db_instance
        self.ChatHistory = chat_history

    def save_ai_message_into_history(self, content, user_id, char_id):
        """
        Save the AI message into the ChatHistory
        """
        ai_message = self.ChatHistory(
            message=content,
            role='ai',
            user_id=user_id,
            char_id=char_id
        )
        self.db.session.add(ai_message)
        self.db.session.commit()

    def save_char_message_into_history(self, content, user_id, char_id):
        """
        Save the AI message into the ChatHistory
        """

        # Save the message from user
        new_message = self.ChatHistory(
            message=content,
            role='character',
            user_id=user_id,
            char_id=char_id
        )
        self.db.session.add(new_message)
        self.db.session.commit()