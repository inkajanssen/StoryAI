class UserManager:

    def __init__(self, db_instance, user_model, char_model):
        self.db = db_instance
        self.User = user_model
        self.Character = char_model


    def create_user(self, username):
        """
        Add a new user to the database
        """
        user = self.db.session.query(self.User).filter_by(username=username).first()

        if user is None:
            new_user = self.User(username=username)
            self.db.session.add(new_user)
            self.db.session.commit()

            return "User successfully added to the database."

        return "User already in Database"


    def get_users(self):
        """
        Retrieve all Users to display them on homepage
        """
        users = self.db.session.query(self.User).order_by(self.User.username).all()
        if users:
            return users
        return []


    def delete_user(self, user_id):
        """
        Delete user from database
        """
        user = self.db.session.query(self.User).get(user_id)

        if not user:
            return "Error: User could not be found"

        self.db.session.delete(user)
        self.db.session.commit()
        return "User successfully deleted from database."


    def get_characters(self, user_id):
        """
        TODO
        Get all characters associated to user as a list
        """
        user = self.db.session.query(self.User).get(user_id)
        return user.created_chars.order_by(self.Character.char_name).all()
