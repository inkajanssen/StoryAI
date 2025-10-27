import streamlit as st
import requests

st.set_page_config(
    page_icon= "📓",
    page_title= "Chat with AI-DM",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BACKEND_URL = "http://localhost:5000"


username_param = st.query_params.get('username', None)
char_name_param = st.query_params.get('char_name', None)
embed_mode = username_param is not None and char_name_param is not None


def fetch_history(username, char_name):
    response = requests.get(f"{BACKEND_URL}/users/{username}/characters/{char_name}/history")

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error fetching history: {response.status_code}")
        print(f"Error message: {response.text}")
        return []


def send_message(username, char_name, message):
    try:
        response = requests.post(
            f"{BACKEND_URL}/users/{username}/characters/{char_name}/chat",
            json={"message":message}
        )
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        st.error("Connection to Flask Backend failed.")
        return False

def main():
    if embed_mode and username_param and char_name_param:

        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
            st.session_state.chat_loaded = False

        if not st.session_state.chat_loaded:
            history = fetch_history(username_param, char_name_param)
            st.session_state.chat_history = history
            st.session_state.chat_loaded = True

            if history:
                st.rerun()

        # Display Chat History Loop
        for msg in st.session_state.chat_history:
            role = msg.get('role', 'character')
            message = msg.get('messages','')

            # Enforce Streamlits roles
            streamlit_role = 'assistant' if role == 'ai' else 'user'

            with st.chat_message(streamlit_role):
                st.write(message)

        with st.form("chat input form", clear_on_submit=True):
            col1, col2 = st.columns([5,1])

            with col1:
                user_input = st.text_input(
                    "Message",
                    key="msg_input",
                    placeholder="Type your message...",
                    label_visibility="collapsed"
                )

            with col2:
                submitted = st.form_submit_button(
                    "Send",
                    type="primary",
                    use_container_width=True
                )

        # Handle send
        if submitted and user_input.strip():
            if send_message(username_param, char_name_param, user_input):
                st.session_state.chat_history = fetch_history(username_param, char_name_param)
                st.session_state.chat_loaded = True
                st.rerun()
            else:
                st.error("Failed to send message. Please try again.")


    else:
        # Standalone mode with user/character selection
        st.title("💬 AI Character Chat")
        st.info("This chat interface is designed to be embedded in the main application.")
        st.markdown("Access it through: `/users/yourUsername/characters/yourCharacterName/chat`")


if __name__ == '__main__':
        main()