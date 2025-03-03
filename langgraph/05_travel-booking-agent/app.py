import streamlit as st
import re
import json
from agent import get_agent_response  # Import AI agent function

# Set Streamlit page config
st.set_page_config(page_title="Swift Travel Agent", page_icon="🤖")

# Custom CSS for chat layout and Font Awesome
custom_css = """
<style>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');

.chat-container {
    display: flex;
    flex-direction: column;
    gap: 20px; /* Increased gap between messages */
}
.user-message {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    margin-bottom: 20px; /* Added margin to separate user messages */
}
.user-text {
    background-color: #2d2d2d;
    color: white;
    padding: 10px 15px;
    border-radius: 10px;
    max-width: 70%;
}
.user-icon {
    font-size: 24px;
    margin-left: 8px;
    color: black;
    background-color: #ff6c6c;
    border-radius: 50%;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.bot-message {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    margin-bottom: 20px; /* Added margin to separate bot messages */
}
.bot-text {
    background-color: #444;
    color: white;
    padding: 10px 15px;
    border-radius: 10px;
    max-width: 70%;
}
.bot-icon {
    font-size: 24px;
    margin-right: 8px;
    color: black;
    background-color: #ffbd44;
    border-radius: 50%;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
}
</style>
"""

def markdown_to_html_links(text):
    """Convert markdown links [text](url) to HTML <a> tags."""
    return re.sub(
        r'\[(.*?)\]\((.*?)\)',
        r'<a href="\2" target="_blank">\1</a>',
        text
    )

st.markdown(custom_css, unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Streamlit UI
st.markdown("<h1>🤖 Swift Travel Agent</h1>", unsafe_allow_html=True)
st.write("Let's plan your itinerary!")

# Display previous chat messages with refined UI
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(
            f"""
            <div class="user-message">
                <div class="user-text">{message['content']}</div>
                <div class="user-icon"><i class="fa-solid fa-user"></i></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="bot-message">
                <div class="bot-icon"><i class="fa-solid fa-robot"></i></div>
                <div class="bot-text">{message['content']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
st.markdown('</div>', unsafe_allow_html=True)

# User input
user_input = st.chat_input("Type your message...")

if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display user message (right-aligned) with Font Awesome user icon
    st.markdown(
        f"""
        <div class="user-message">
            <div class="user-text">{user_input}</div>
            <div class="user-icon"><i class="fa-solid fa-user"></i></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Get AI response
    response = get_agent_response(user_input)

    # Convert markdown links to HTML links
    formatted_response = markdown_to_html_links(json.dumps(response))

    # Add AI response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Display AI response (left-aligned) with Font Awesome bot icon
    st.markdown(
        f"""
        <div class="bot-message">
            <div class="bot-icon"><i class="fa-solid fa-robot"></i></div>
            <div class="bot-text">{formatted_response}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )