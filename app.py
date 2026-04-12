import streamlit as st
import requests
import random

# Page Configuration
st.set_page_config(
    page_title="TENSCI Chatbot",
    page_icon="⚖️",
    layout="centered"
)

# Custom CSS for Exact Styling Requirements
st.markdown("""
<style>
/* Bold Border & Blue Background for Input & Result Fields */
.stTextArea textarea, div[data-testid="stTextArea"] textarea {
    border: 4px solid #000000 !important;
    background-color: #0056b3 !important;
    color: #ffffff !important;
    font-weight: bold !important;
    font-size: 1.2rem !important;
    border-radius: 8px !important;
    line-height: 1.4 !important;
}

/* Suggestion Prompt Styling: Gray, Bold, Slightly Bigger */
.suggestion-item {
    color: #6b7280;
    font-weight: bold;
    font-size: 1.15rem;
    cursor: pointer;
    padding: 8px 12px;
    margin: 4px 0;
    border-radius: 6px;
    transition: background 0.2s;
}
.suggestion-item:hover {
    background-color: #f3f4f6;
}

/* Button Styling */
.stButton > button {
    font-weight: bold;
    font-size: 1.1rem;
    border-radius: 6px;
}

/* Header & Title */
h1 { font-weight: bold; }
.stDivider { margin-top: 10px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "user_query" not in st.session_state:
    st.session_state.user_query = ""
if "chat_response" not in st.session_state:
    st.session_state.chat_response = ""

# Title
st.title("⚖️ 10 Standard Student Tamil Nadu State Board Science Subject Chatbot")

# 10 Random Suggestion Prompts from Knowledge Base (UNIT 1 & 2)
PROMPT_POOL = [
    "Explain Newton's First Law of Motion with real-life examples.",
    "What is the difference between mass and weight? Provide formulas.",
    "Derive F = ma from Newton's Second Law of Motion.",
    "How does rocket propulsion demonstrate conservation of momentum?",
    "State and explain Snell's Law of Refraction.",
    "Calculate acceleration due to gravity using Earth's mass and radius.",
    "Define torque and explain its application in a steering wheel.",
    "Explain the principle of moments using a seesaw example.",
    "How does the value of 'g' vary with altitude and depth?",
    "What is impulse and how is it related to change in momentum?",
    "Explain inertia of rest, motion, and direction with examples.",
    "Describe the working of shock absorbers using impulse-momentum theorem.",
    "What are balanced and unbalanced forces? Give examples.",
    "Explain the wave nature of light and the formula c = νλ.",
    "List the characteristics of gravitational force."
]

st.markdown("### 💡 Suggested Academic Prompts")

# Display 10 random prompts in 2 columns
selected_prompts = random.sample(PROMPT_POOL, min(10, len(PROMPT_POOL)))

cols = st.columns(2)
for i, prompt in enumerate(selected_prompts):
    col_idx = i % 2
    with cols[col_idx]:
        # Use session state to store selected prompt
        if st.button(prompt, key=f"prompt_{i}", use_container_width=True):
            st.session_state.user_query = prompt
            st.session_state.chat_response = ""
            st.rerun()

st.divider()

# Text Field 1: User Input
st.markdown("### 📝 Enter Your Query")
user_input = st.text_area(
    "Type your science question here...",
    value=st.session_state.user_query,
    height=100,
    label_visibility="collapsed",
    key="main_input"
)

# Buttons
col1, col2 = st.columns(2)
with col1:
    submit_btn = st.button("📤 Submit Prompt", use_container_width=True)
with col2:
    reset_btn = st.button("🔄 Reset", use_container_width=True)

# API Call & Response Handling
if submit_btn and user_input.strip():
    with st.spinner("🔍 Retrieving academic response..."):
        try:
            api_key = st.secrets["OPENROUTER_API_KEY"]
            headers = {
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://github.com/TENSCI",
                "X-Title": "TENSCI Chatbot"
            }
            payload = {
                "model": "qwen/qwen2.5-72b-instruct",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are an academic science tutor for 10th Standard Tamil Nadu State Board students. "
                            "Provide clear, accurate, and curriculum-aligned answers. Use formal academic language. "
                            "Structure responses with definitions, formulas, examples, and real-life applications. "
                            "Keep explanations concise, educational, and strictly focused on the TN State Board syllabus (Laws of Motion, Optics, etc.)."
                        )
                    },
                    {"role": "user", "content": user_input}
                ],
                "temperature": 0.6
            }
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            st.session_state.chat_response = response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            st.session_state.chat_response = f"⚠️ API Error: {str(e)}\nPlease verify your OPENROUTER_API_KEY in secrets.toml."

if reset_btn:
    st.session_state.user_query = ""
    st.session_state.chat_response = ""
    st.rerun()

# Text Field 2: Multi-line Result Display
st.markdown("### 📖 Retrieved Academic Response")
st.text_area(
    "Answer will appear here:",
    value=st.session_state.chat_response,
    height=250,
    disabled=True,
    label_visibility="collapsed"
)
