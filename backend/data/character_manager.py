class CharacterManager:

    def __init__(self, db_instance, char_model, user_model):
        self.db = db_instance
        self.Character = char_model
        self.User = user_model


    def create_character(self, char_name, user_id):
        """
        Create a character and link it to user
        """
        user = self.db.session.query(self.User).get(user_id)

        if not user:
            return "Error: User could not be found."

        if user.created_chars.count() >= 3:
            return "Error: You already have three Characters. You cannot create more."

        new_char = self.Character(char_name=char_name,user_id=user_id)
        self.db.session.add(new_char)
        self.db.session.commit()
        return f"{char_name} was successfully created."


    def delete_character(self, char_id):
        """
        Delete a char
        """
        char = self.db.session.query(self.Character).get(char_id)

        if not char:
            return "Error: Character could not be found."

        self.db.session.delete(char)
        self.db.session.commit()
        return f" The Character {char.char_name} was successfully deleted from Database."


    def get_skills(self, skill):
        pass
