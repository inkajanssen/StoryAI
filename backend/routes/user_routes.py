# from ..models.users import User
# from ..models.characters import Character
# from ..models.db import db
# from flask import Blueprint, render_template, request, flash, redirect, url_for
#
# # Define blueprint
# user_blueprint = Blueprint('user', __name__)
#
# # Import and create objects of the data managers
# from ..data import CharacterManager, UserManager, ChatManager
#
# character_manager = CharacterManager(db, Character, User)
# user_manager = UserManager(db, User, Character)
#
#
# @user_blueprint.route('/', methods=['GET'])
# def home():
#     """
#     The home page of the app.
#     """
#     users = user_manager.get_users()
#     return render_template('home.html', users=users)
#
#
# @user_blueprint.route('/users', methods=['POST'])
# def create_user():
#     """
#     When the user submits the “add user” form, a POST request is made.
#     The server receives the new user info, adds it to the database,
#     then redirects back to /
#     """
#     user = request.form.get('create_user')
#
#     if not user:
#         flash(message="Failed to create user. Please try again")
#         return redirect(url_for('home'))
#
#     message = user_manager.create_user(user)
#     flash(message)
#
#     return redirect(url_for('home'))
#
#
# @user_blueprint.route('/users/<string:username>/delete', methods=['POST'])
# def delete_user(username):
#     """
#     Delete user
#     """
#     user = db.session.query(User).filter_by(username=username).one_or_none()
#     user_manager.delete_user(user.user_id)
#
#     return redirect(url_for('home'))
#
#
# @user_blueprint.route('/users/<string:username>/characters', methods=['GET'])
# def characters_of_user(username):
#     """
#     When you click a username on homepage, the app retrieves
#     all characters of a user and displays them
#     """
#     user = db.session.query(User).filter_by(username=username).one_or_none()
#     characters = user_manager.get_characters(user.user_id)
#
#     return render_template("characters.html", characters=characters, user=user)
#
#
# @user_blueprint.route('/users/<string:username>/characters', methods=['POST'])
# def add_character(username):
#     """
#     Adds a new character to user list of characters
#     """
#     user = db.session.query(User).filter_by(username=username).one_or_none()
#     char_name = request.form.get('add_character').strip()
#
#     if not user or not char_name:
#         flash(message=f"Error: Please try again. User:{user.username}, char_name={char_name}")
#         return redirect(url_for('characters_of_user', username=user.username))
#
#     character = character_manager.create_character(char_name, user.user_id)
#     flash(message=character)
#     return redirect(url_for('characters_of_user', username=user.username))
#
#
# @user_blueprint.route('/users/<string:username>/characters/<string:char_name>/update', methods=['GET, POST'])
# def update_character(username, char_name):
#     """
#     Change details of the character
#     """
#     user = db.session.query(User).filter_by(username=username).one_or_none()
#     character_to_update= user.created_chars.filter(Character.char_name == char_name).one_or_none()
#
#     if request.method == 'POST':
#         name = request.form.get('char_name').strip()
#
#         # bring over to datamanager?
#         character_to_update.char_name = name
#         db.session.commit()
#
#         #Redirect back to list of characters of a user
#         return redirect(url_for('characters_of_user', username=user.username))
#
#     # Display the Character Infos to change
#     return render_template('update_character.html', character=character_to_update,
#                            username=username)
#
#
# @user_blueprint.route('/users/<string:username>/characters/<string:char_name>/delete', methods=['POST'])
# def delete_character(username, char_name):
#     """
#     Delete a character from the users list
#     """
#     user = db.session.query(User).filter_by(username=username).one_or_none()
#     char_to_delete = user.created_chars.filter(Character.char_name == char_name).one_or_none()
#
#     character_manager.delete_character(char_to_delete.char_id)
#
#     return redirect(url_for('characters_of_user', username=user.username))
