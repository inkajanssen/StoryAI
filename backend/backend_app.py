import os.path

import requests.exceptions
from flask import render_template, request, flash, redirect, url_for, abort, jsonify
from langchain_core.messages import HumanMessage
from sqlalchemy import select
from flask_cors import CORS
from werkzeug.utils import secure_filename

from models import db, create_app, User, Character, ChatHistory, create_chatbot

BASE_TOTAL = 48 # Total points of attributes before distribution
MAX_POINTS = 10 # Total of points to distribute

# Call create app from db.py
app = create_app()

# Define Upload Folder
UPLOAD_FOLDER = 'static/character_images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create chatbot
chatbot_app = create_chatbot()

#Add CORS
CORS(app)

# Import and create objects of the data managers
from data import CharacterManager, UserManager, ChatManager

character_manager = CharacterManager(db, Character, User)
user_manager = UserManager(db, User, Character)
chat_manager = ChatManager(db, ChatHistory)

# TODO Refractor routes to their own py
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
    char_name = request.form.get('char_name').strip()

    if not user or not char_name:
        flash(message=f"Error: Please try again. User:{user.username}, char_name={char_name}")
        return redirect(url_for('characters_of_user', username=user.username))

    try:
        strength = int(request.form.get('strength', 8))
        dexterity = int(request.form.get('dexterity', 8))
        constitution = int(request.form.get('constitution', 8))
        intelligence = int(request.form.get('intelligence', 8))
        wisdom = int(request.form.get('wisdom', 8))
        charisma = int(request.form.get('charisma', 8))

    except ValueError:
        message="Error: Attributes need to be whole numbers"
        flash(message, "error")
        return redirect(url_for('characters_of_user', username=username))

    total_current_stats = (strength+dexterity+constitution+intelligence+wisdom+charisma)

    points_invested= total_current_stats - BASE_TOTAL

    if points_invested > MAX_POINTS:
        message=f"Error: Character Creation failed! You invested {points_invested} but can only distribute {MAX_POINTS}."
        flash(message, "error")
        return redirect(url_for('characters_of_user', username=username))

    PLACEHOLDER_PATH = url_for('static', filename='character_images/Portrait_Placeholder.png', _external=True)
    secure_char_name = secure_filename(char_name)

    uploaded_img = request.files.get('char_img')
    image_url = request.form.get('char_url')

    image_path_or_url = None

    if uploaded_img and uploaded_img.filename:
        file_extension = os.path.splitext(uploaded_img.filename)[1]
        unique_filename = f"{secure_char_name}{file_extension}"

        upload_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
        file_path = os.path.join(upload_dir, unique_filename)

        uploaded_img.save(file_path)
        image_path_or_url = url_for('static', filename=f'character_images/{unique_filename}', _external=True)

    elif image_url:
        try:
            r = requests.head(image_url, timeout=5)
            if 'image' in r.headers.get('Content-Type', ''):
                image_path_or_url = image_url
            else:
                return "Invalid image URL or unsupported type", 400
        except requests.exceptions.RequestException:
            return "Could not reach provided image URL", 400

    if not image_path_or_url:
        image_path_or_url = PLACEHOLDER_PATH

    appearance = request.form.get('appearance')
    personality = request.form.get('personality')
    backstory = request.form.get('backstory')

    character = (character_manager.create_character
                 (char_name=char_name,
                  user_id=user.user_id,
                  char_image=image_path_or_url,

                  appearance=appearance,
                  personality=personality,
                  backstory=backstory,

                  strength=strength,
                  dexterity=dexterity,
                  constitution=constitution,
                  intelligence=intelligence,
                  wisdom=wisdom,
                  charisma=charisma
                  ))

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
    image_path = char_to_delete.char_image

    print(image_path)

    static_url_prefix = url_for('static', filename='character_images/', _external=True)

    if image_path and image_path.startswith(static_url_prefix):
        filename_to_delete = image_path.replace(static_url_prefix, '', 1)

        filename_to_delete = secure_filename(filename_to_delete)

        upload_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
        file_path = os.path.join(upload_dir, filename_to_delete)

        if os.path.exists(file_path):
            os.remove(file_path)

    character_manager.delete_character(char_to_delete.char_id)

    return redirect(url_for('characters_of_user', username=user.username))


@app.route('/users/<string:username>/characters/<string:char_name>/chat', methods=['GET'])
def chat_using_streamlit(username, char_name):
    """
    Display chat with streamlit
    """

    user = db.session.query(User).filter_by(username=username).one_or_none()
    character = db.session.query(Character).filter_by(char_name=char_name).one_or_none()

    if not user or not character:
        return "User or Character not found", 404

    return render_template('chat.html', username=username, char_name=char_name)


@app.route('/users/<string:username>/characters/<string:char_name>/chat', methods=['POST'])
def send_chat_message(username, char_name):
    """
    Streamlit Endpoint for saving the messages
    """
    if chatbot_app is None:
        return jsonify({"error": "Chatbot is unavailable."}), 503

    user = db.session.query(User).filter_by(username=username).one_or_none()
    character = db.session.query(Character).filter_by(char_name=char_name).one_or_none()

    if not user or not character:
        return jsonify({"error": "User or Character not found"}), 404

    user_id = user.user_id
    char_id = character.char_id

    # Create thread id
    thread_id = int(f"{user_id}{char_id}")
    config = {"configurable": {"thread_id": thread_id}}

    print("\n--- Incoming POST Request Debug ---")

    # 1. Check Headers (Is Content-Type present?)
    print("Headers:", dict(request.headers))

    # 2. Check Raw Data (Is the body empty?)
    try:
        raw_data = request.data.decode('utf-8')
        print("Raw Request Body:", raw_data)
        request.data = raw_data.encode('utf-8')  # Reset data stream for get_json()
    except Exception as e:
        print(f"Error reading raw data: {e}")

    print("-----------------------------------")

   #try:
    data = request.get_json(silent=True)
    # except Exception as e:
    #     return jsonify({"error": f"Invalid JSON Format in request body:{e}"}), 400
    if data is None:
        return jsonify({"error": f"Invalid JSON Format in request body."}), 400
    message_content = data.get('message')

    print(f"DEBUG send_chat_message(): message_content = {repr(message_content)}")

    if not message_content or not message_content.strip():
        return jsonify({"error": "Message could not be found."}), 400

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

    # TODO make language selectable
    response_state = chatbot_app.invoke(
        input={"messages": input_message, "language": "English"},
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

    return jsonify({"success": True}), 200


@app.route('/users/<string:username>/characters/<string:char_name>/history', methods=['GET'])
def get_chat_history(username, char_name):
    """
    Create an endpoint with a json for streamlit to get the chats history
    """
    user = db.session.query(User).filter_by(username=username).one_or_none()
    character = db.session.query(Character).filter_by(char_name=char_name).one_or_none()

    if not user or not character:
        return {"error": "User or Character not found"}, 404

    user_id = user.user_id
    char_id = character.char_id
    thread_id = int(f"{user_id}{char_id}")
    config = {"configurable": {"thread_id":thread_id}}

    # Load chat history
    chat_history = db.session.execute(
        select(ChatHistory).where(
            (ChatHistory.user_id == user_id),
            (ChatHistory.char_id == char_id)
        ).order_by(ChatHistory.created.asc())
    ).scalars().all()

    if not chat_history:
        initial_message = [HumanMessage(content="Start the story.")]

        response_state = chatbot_app.invoke(
            input={"messages": initial_message, "language": "English"},
            config=config,
            recursion_limit=5
        )

        ai_response_content = response_state["messages"][-1].content

        # Save AI message
        ai_message = ChatHistory(
            message=ai_response_content,
            role='ai',
            user_id=user_id,
            char_id=char_id
        )
        db.session.add(ai_message)
        db.session.commit()

        # Reload history chat
        chat_history = db.session.execute(
            select(ChatHistory).where(
                (ChatHistory.user_id == user_id),
                (ChatHistory.char_id == char_id)
            ).order_by(ChatHistory.created.asc())
        ).scalars().all()

    # Convert to JSON
    history_json = [
        {"role": msg.role, "messages": msg.message}
        for msg in chat_history
    ]
    # return history
    return jsonify(history_json)


@app.errorhandler(404)
def page_not_found(e):
    error_message = str(e)
    return render_template('404.html', error_message=error_message), 404


@app.errorhandler(503)
def chatbot_not_initialized(e):
    return render_template('503.html'), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
