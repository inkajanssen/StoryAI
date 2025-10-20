import os
import streamlit as st
from openai import OpenAI
from streamlit import session_state

# st.title('AI Chat')
#
#
# # Streamlit Helper Function
# def get_chat_partner(username, char_name):
#     """
#     Get the User and Char from the database
#     """
#
#     user = db.session.query(User).filter_by(username=username).one_or_none()
#     character = db.session.query(Character).filter_by(char_name=char_name).one_or_none()
#
#     if not user or not character:
#         return "User or Character not found."
#
#     return user, character
#
#
# def load_chat_history(user_id, char_id):
#     """
#     Loads the Chat History
#     """
#     chat_history = db.session.execute(
#         select(ChatHistory).where(
#             (ChatHistory.user_id == user_id),
#                         (ChatHistory.char_id == char_id)
#         ).order_by(ChatHistory.created.asc())
#     ).scalars().all()
#
#     return chat_history
#
#
# # Streamlit Frontend
# user, character = get_chat_partner()
#
# if not user or character:
#     st.error("User or Character were not found.")
#     st.stop()
#
# user_id = user.user_id
# char_id = character.char_id
# thread_id = int(f"{user_id}{char_id}")
# config = {"configurable": {"thread_id": thread_id}}
#
# st.title(f"Chat with {character.char_name}")
# st.caption(f"User: {user.username}")
#
# if 'messages' not in st.session_state:
#     st.session_state['messages'] = load_chat_history(user_id, char_id)
#
#

st.title('Chat with Character')

openai_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=openai_key)

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o-mini"

if "messages" not in session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Enter your story"):
    st.session_state.messages.append({"role": "character", "content": prompt})
    with st.chat_message("character"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role":"assistent", "content": response})