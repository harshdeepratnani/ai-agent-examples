import streamlit as st
import re
import json
import requests  # Import requests library

# Set Streamlit page config
st.set_page_config(page_title="Swift Transit Agent", page_icon="🤖")

# Custom CSS for chat layout and Font Awesome
custom_css = """
<style>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');

.chat-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
}
.user-message {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    margin-bottom: 20px;
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
    margin-bottom: 20px;
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
.action-buttons {
    display: flex;
    gap: 10px;
    margin-top: 10px;
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

def get_agent_response(user_input):
    """Make an API call to get the agent response."""
    response = requests.post("http://localhost:5001/get_response", json={"user_input": user_input})
    
    return response.json()

def resume_agent(user_input):
    """Make an API call to resume the agent."""
    response = requests.post("http://localhost:5001/resume", json={"user_input": user_input})
    return response.json()

# Function to handle button actions
def handle_action(action, user_input):
    """Process the selected action and return a response."""
    # For now, simulate a response; replace with actual logic later
    if action == "Yes":
        return resume_agent("Yes")
    elif action == "No":
        return resume_agent("No")
    else:
        return {"message": f"Action '{action}' received!", "actions": []}

st.markdown(custom_css, unsafe_allow_html=True)

# Initialize chat history and action state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_action" not in st.session_state:
    st.session_state.pending_action = None

# Streamlit UI
st.markdown("<h1>🤖 Swift Transit Agent</h1>", unsafe_allow_html=True)
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

    # Display user message
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
    actions = response.get("actions", [])

    # Handle response based on actions
    if not actions:  # Empty or null actions
        message = response.get("message", "No message provided")
        formatted_response = markdown_to_html_links(str(message))
        st.session_state.messages.append({"role": "assistant", "content": message})
        st.markdown(
            f"""
            <div class="bot-message">
                <div class="bot-icon"><i class="fa-solid fa-robot"></i></div>
                <div class="bot-text">{formatted_response}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:  # Actions present
        question = response.get("question", "Please choose an action:")
        formatted_question = markdown_to_html_links(question)
        st.session_state.messages.append({"role": "assistant", "content": question})
        st.session_state.pending_action = {"question": question, "actions": actions}
        st.markdown(
            f"""
            <div class="bot-message">
                <div class="bot-icon"><i class="fa-solid fa-robot"></i></div>
                <div class="bot-text">{formatted_question}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Handle pending actions and display buttons
if st.session_state.pending_action:
    st.markdown('<div class="action-buttons">', unsafe_allow_html=True)
    cols = st.columns(len(st.session_state.pending_action["actions"]))
    for i, action in enumerate(st.session_state.pending_action["actions"]):
        with cols[i]:
            if st.button(action, key=f"action_{i}"):
                # Process the action
                action_response = handle_action(action, user_input)
                st.session_state.messages.append({"role": "assistant", "content": action_response["message"]})
                st.session_state.pending_action = None  # Clear pending action
                # Display action response
                formatted_action_response = markdown_to_html_links(str(action_response["message"]))
                st.markdown(
                    f"""
                    <div class="bot-message">
                        <div class="bot-icon"><i class="fa-solid fa-robot"></i></div>
                        <div class="bot-text">{formatted_action_response}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.rerun()  # Refresh to clear buttons
    st.markdown('</div>', unsafe_allow_html=True)