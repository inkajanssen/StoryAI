class ChatManager:

    def __init__(self, db_instance, chat_model):
        self.db = db_instance
        self.Chat = chat_model

    def save_message_into_history(self):
        """
        Save the send message into the ChatHistory
        """

        pass