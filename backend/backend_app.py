from flask import render_template, request, flash, redirect, url_for, abort
from langchain_core.messages import HumanMessage
from sqlalchemy import select

from models import db, create_app, User, Character, ChatHistory, create_chatbot

# Call create app from db.py
app = create_app()

# Create chatbot

chatbot_app = create_chatbot()

# Import and create objects of the data managers
from data import CharacterManager, UserManager, ChatManager

character_manager = CharacterManager(db, Character, User)
user_manager = UserManager(db, User, Character)
chat_manager = ChatManager(db, ChatHistory)


@app.route('/', methods=['GET'])
def home():
    """
    The home page of the app.
    """
    users = user_manager.get_users()
    return render_template('home.html', users=users)


@app.route('/users', methods=['POST'])
def create_user():
    """
    When the user submits the “add user” form, a POST request is made.
    The server receives the new user info, adds it to the database,
    then redirects back to /
    """
    user = request.form.get('create_user')

    if not user:
        flash(message="Failed to create user. Please try again")
        return redirect(url_for('home'))

    message = user_manager.create_user(user)
    flash(message)

    return redirect(url_for('home'))


@app.route('/users/<string:username>/delete', methods=['POST'])
def delete_user(username):
    """
    Delete user
    """
    user = db.session.query(User).filter_by(username=username).one_or_none()
    user_manager.delete_user(user.user_id)

    return redirect(url_for('home'))


@app.route('/users/<string:username>/characters', methods=['GET'])
def characters_of_user(username):
    """
    When you click a username on homepage, the app retrieves
    all characters of a user and displays them
    """
    user = db.session.query(User).filter_by(username=username).one_or_none()
    characters = user_manager.get_characters(user.user_id)

    return render_template("characters.html", characters=characters, user=user)


@app.route('/users/<string:username>/characters', methods=['POST'])
def add_character(username):
    """
    Adds a new character to user list of characters
    """
    user = db.session.query(User).filter_by(username=username).one_or_none()
    char_name = request.form.get('add_character').strip()

    if not user or not char_name:
        flash(message=f"Error: Please try again. User:{user.username}, char_name={char_name}")
        return redirect(url_for('characters_of_user', username=user.username))

    character = character_manager.create_character(char_name, user.user_id)
    flash(message=character)
    return redirect(url_for('characters_of_user', username=user.username))


@app.route('/users/<string:username>/<string:char_name>', methods=['GET'])
def char(username, char_name):
    """
    Show Char to update or delete it
    """
    user = db.session.query(User).filter_by(username=username).one_or_none()
    character = db.session.query(Character).filter_by(char_name=char_name).one_or_none()

    return render_template("char_display.html", character=character, user=user)


@app.route('/users/<string:username>/characters/<string:char_name>/update', methods=['GET, POST'])
def update_character(username, char_name):
    """
    Change details of the character
    """
    user = db.session.query(User).filter_by(username=username).one_or_none()
    character_to_update= user.created_chars.filter(Character.char_name == char_name).one_or_none()

    if not user or not character_to_update:
        abort(404)

    if request.method == 'POST':
        name = request.form.get('char_name').strip()

        # bring over to datamanager?
        character_to_update.char_name = name
        db.session.commit()

        #Redirect back to list of characters of a user
        return redirect(url_for('characters_of_user', username=user.username))

    # Display the Character Infos to change
    return render_template('update_character.html', character=character_to_update,
                           username=username)


@app.route('/users/<string:username>/characters/<string:char_name>/delete', methods=['POST'])
def delete_character(username, char_name):
    """
    Delete a character from the users list
    """
    user = db.session.query(User).filter_by(username=username).one_or_none()
    char_to_delete = user.created_chars.filter(Character.char_name == char_name).one_or_none()

    character_manager.delete_character(char_to_delete.char_id)

    return redirect(url_for('characters_of_user', username=user.username))


@app.route('/users/<string:username>/characters/<string:char_name>/chat', methods=['GET', 'POST'])
def chat(username, char_name):
    """
    Chat with the AI
    """

    if chatbot_app is None:
        return "Chatbot is unavailable.", 503

    user = db.session.query(User).filter_by(username=username).one_or_none()
    character = db.session.query(Character).filter_by(char_name=char_name).one_or_none()

    if not user or not character:
        return "User or Character not found", 404

    user_id = user.user_id
    char_id = character.char_id

    # Create thread id
    thread_id = int(f"{user_id}{char_id}")
    config = {"configurable": {"thread_id":thread_id}}

    if request.method == 'POST':
        # Get the message from user
        message_content = request.form.get('message')

        # Save the message from user
        new_message = ChatHistory(
            message=message_content,
            role='character',
            user_id=user_id,
            char_id=char_id
        )
        db.session.add(new_message)

        # Invoke AI response
        input_message = [HumanMessage(content=message_content)]

        response_state = chatbot_app.invoke(
            input= {"messages": input_message},
            config=config,
            recursion_limit=5
        )

        ai_response_content = response_state["messages"][-1].content

        # Save AI response
        ai_message = ChatHistory(
            message=ai_response_content,
            role='ai',
            user_id=user_id,
            char_id=char_id
        )
        db.session.add(ai_message)

        # Commit the exchange
        db.session.commit()

        return redirect(url_for('chat', username=username, char_name=char_name))

    # Load messages for chat
    chat_history = db.session.execute(
        select(ChatHistory).where(
            (ChatHistory.user_id==user_id),
                        (ChatHistory.char_id==char_id)
        ).order_by(ChatHistory.created.asc())
    ).scalars().all()

    # If there is no message let AI begin
    if not chat_history:
        initial_message = [HumanMessage(content="Start the Story.")]

        response_state = chatbot_app.invoke(
            input={"messages": initial_message},
            config=config,
            recursion_limit=5
        )

        ai_response_content = response_state["messages"][-1].content

        # Save AI response
        ai_message = ChatHistory(
            message=ai_response_content,
            role='ai',
            user_id=user_id,
            char_id=char_id
        )
        db.session.add(ai_message)
        db.session.commit()

        chat_history = db.session.execute(
            select(ChatHistory).where(
                (ChatHistory.user_id == user_id),
                (ChatHistory.char_id == char_id)
            ).order_by(ChatHistory.created.asc())
        ).scalars().all()


    return render_template('chat.html', history=chat_history, username=username, char_name=char_name)


@app.errorhandler(404)
def page_not_found(e):
    error_message = str(e)
    return render_template('404.html', error_message=error_message), 404


@app.errorhandler(503)
def chatbot_not_initialized(e):
    return render_template('503.html'), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
