import streamlit as st
import requests
import random

# Page Configuration
st.set_page_config(
    page_title="TENSCI Chatbot",
    page_icon="⚖️",
    layout="wide"  # Changed to wide for side-by-side layout
)

# Custom CSS for Exact Styling Requirements
st.markdown("""
<style>
/* Main title in Blue */
.main-header {
    color: #0056b3 !important;
    font-weight: bold !important;
    font-size: 2rem !important;
    text-align: center !important;
    margin-bottom: 2rem !important;
}

/* GLOBAL TEXT AREA STYLING - Blue Background, WHITE Text */
.stTextArea textarea,
div[data-testid="stTextArea"] textarea,
textarea.stTextArea,
.stTextArea > div > textarea {
    border: 4px solid #000000 !important;
    background-color: #0056b3 !important;
    color: #ffffff !important;
    font-weight: bold !important;
    font-size: 1.2rem !important;
    border-radius: 8px !important;
    line-height: 1.4 !important;
}

/* SPECIFIC FIX - Force white text in ALL textareas */
textarea {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* Section headers in GREEN */
.section-header {
    color: #28a745 !important;
    font-weight: bold !important;
    font-size: 1.4rem !important;
    margin: 1rem 0 !important;
}

/* Suggestion Prompt Styling */
.suggestion-container {
    background-color: #f8f9fa;
    border: 2px solid #dee2e6;
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
}

.suggestion-text {
    color: #6b7280 !important;
    font-weight: bold !important;
    font-size: 1.1rem !important;
    margin-bottom: 8px !important;
}

.copy-button {
    font-size: 0.85rem !important;
    padding: 4px 8px !important;
}

/* Button Styling */
.stButton > button {
    font-weight: bold;
    font-size: 1.1rem;
    border-radius: 6px;
}

/* Force ALL headers to BLUE */
h1, h2, h3, h4, h5, h6, 
div[data-testid="stMarkdown"] h1,
div[data-testid="stMarkdown"] h2,
div[data-testid="stMarkdown"] h3,
div[data-testid="stMarkdown"] h4,
div[data-testid="stMarkdown"] h5,
div[data-testid="stMarkdown"] h6 {
    color: #0056b3 !important;
}

/* Override Streamlit default styles */
.css-1d391kg, .css-1lcbmhc, .css-16idsys {
    color: #0056b3 !important;
}

.stDivider { 
    margin-top: 10px; 
    margin-bottom: 10px; 
}

/* White background for the whole app */
.main .block-container {
    background-color: #ffffff;
    padding: 2rem;
    border-radius: 10px;
}

/* Column spacing */
.stColumns {
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "user_query" not in st.session_state:
    st.session_state.user_query = ""
if "chat_response" not in st.session_state:
    st.session_state.chat_response = ""
if "tamil_translation" not in st.session_state:
    st.session_state.tamil_translation = ""

# Title - Using markdown with custom class for Blue color
st.markdown('<h1 class="main-header">⚖️ 10 Standard Student Tamil Nadu State Board Science Subject Chatbot</h1>', unsafe_allow_html=True)

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

# Section Header - GREEN color
st.markdown('<p class="section-header">💡 Suggested Academic Prompts</p>', unsafe_allow_html=True)

# Display 10 random prompts in 2 columns with copy buttons
selected_prompts = random.sample(PROMPT_POOL, min(10, len(PROMPT_POOL)))

cols = st.columns(2)
for i, prompt in enumerate(selected_prompts):
    col_idx = i % 2
    with cols[col_idx]:
        # Create a container for prompt and copy button
        st.markdown(f"""
        <div class="suggestion-container">
            <div class="suggestion-text">{prompt}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Copy button for each prompt
        col_btn1, col_btn2 = st.columns([3, 1])
        with col_btn1:
            if st.button("Use Prompt", key=f"use_{i}", use_container_width=True):
                st.session_state.user_query = prompt
                st.session_state.chat_response = ""
                st.session_state.tamil_translation = ""
                st.rerun()
        with col_btn2:
            if st.button("📋", key=f"copy_{i}", help="Copy to clipboard"):
                st.code(prompt, language=None)
                st.success("Copied! Press Ctrl+C to copy")

st.divider()

# Text Field 1: User Input - GREEN header, BLUE background with WHITE text
st.markdown('<p class="section-header">📝 Enter Your Query</p>', unsafe_allow_html=True)
user_input = st.text_area(
    "Type your science question here...",
    value=st.session_state.user_query,
    height=100,
    label_visibility="collapsed",
    key="main_input"
)

# Buttons
col1, col2, col3 = st.columns(3)
with col1:
    submit_btn = st.button("📤 Submit Prompt", use_container_width=True)
with col2:
    translate_btn = st.button("🌐 Translate to Tamil", use_container_width=True, disabled=not st.session_state.chat_response)
with col3:
    reset_btn = st.button("🔄 Reset", use_container_width=True)

# Function to get English response
def get_english_response(query):
    try:
        api_key = st.secrets.get("OPENROUTER_API_KEY")
        
        if not api_key:
            return "⚠️ Configuration Error: OPENROUTER_API_KEY not found in secrets.toml. Please add your API key."
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/TENSCI",
            "X-Title": "TENSCI Chatbot"
        }
        
        payload = {
            "model": "qwen/qwen-2.5-72b-instruct",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an academic science tutor for 10th Standard Tamil Nadu State Board students. Provide clear, accurate, and curriculum-aligned answers. Use formal academic language. Structure responses with definitions, formulas, examples, and real-life applications. Keep explanations concise, educational, and strictly focused on the TN State Board syllabus (Laws of Motion, Optics, etc.)."
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            "temperature": 0.6,
            "max_tokens": 1000
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return "⚠️ Error: Invalid response format from API."
        elif response.status_code == 401:
            return "⚠️ Authentication Error: Invalid API key. Please verify your OPENROUTER_API_KEY."
        elif response.status_code == 400:
            error_detail = response.json().get("error", {}).get("message", "Unknown error")
            return f"⚠️ Bad Request: {error_detail}\n\nPlease check:\n1. API key is valid\n2. Model name is correct\n3. Request format is proper"
        else:
            return f"⚠️ API Error {response.status_code}: {response.text}"
            
    except requests.exceptions.Timeout:
        return "⚠️ Request Timeout: The API took too long to respond. Please try again."
    except requests.exceptions.ConnectionError:
        return "⚠️ Connection Error: Unable to connect to the API. Check your internet connection."
    except Exception as e:
        return f"⚠️ Unexpected Error: {str(e)}\n\nPlease verify your OPENROUTER_API_KEY in secrets.toml."

# Function to translate to Tamil
def translate_to_tamil(text):
    try:
        api_key = st.secrets.get("OPENROUTER_API_KEY")
        
        if not api_key:
            return "⚠️ Translation API key not found."
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/TENSCI",
            "X-Title": "TENSCI Tamil Translation"
        }
        
        payload = {
            "model": "qwen/qwen-2.5-72b-instruct",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional translator. Translate the following science content from English to simple, clear Tamil suitable for 10th standard Tamil medium students. Keep scientific terms in English with Tamil explanation where needed. Maintain formulas and technical accuracy. Use simple Tamil sentences that students can easily understand."
                },
                {
                    "role": "user",
                    "content": f"Translate this to Tamil for 10th standard students:\n\n{text}"
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=45
        )
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return "⚠️ Translation error: Invalid response format."
        else:
            return f"⚠️ Translation Error {response.status_code}: {response.text}"
            
    except Exception as e:
        return f"⚠️ Translation Error: {str(e)}"

# API Call & Response Handling
if submit_btn and user_input.strip():
    with st.spinner("🔍 Retrieving academic response..."):
        st.session_state.chat_response = get_english_response(user_input)
        st.session_state.tamil_translation = ""  # Clear previous translation
        st.rerun()

# Translation Handling
if translate_btn and st.session_state.chat_response:
    with st.spinner("🌐 Translating to Tamil..."):
        st.session_state.tamil_translation = translate_to_tamil(st.session_state.chat_response)
        st.rerun()

if reset_btn:
    st.session_state.user_query = ""
    st.session_state.chat_response = ""
    st.session_state.tamil_translation = ""
    st.rerun()

# Display Results - Side by Side
if st.session_state.chat_response:
    st.divider()
    
    # Two columns for English and Tamil
    col_eng, col_tam = st.columns(2)
    
    with col_eng:
        st.markdown('<p class="section-header">📖 Retrieved Academic Response (English)</p>', unsafe_allow_html=True)
        st.text_area(
            "English Response:",
            value=st.session_state.chat_response,
            height=400,
            disabled=True,
            label_visibility="collapsed",
            key="english_response"
        )
        if st.button("📋 Copy English Response", key="copy_eng"):
            st.code(st.session_state.chat_response, language=None)
            st.success("English response copied! Press Ctrl+C to copy")
    
    with col_tam:
        st.markdown('<p class="section-header">📚 தமிழ் விளக்கம் (Tamil Translation)</p>', unsafe_allow_html=True)
        if st.session_state.tamil_translation:
            st.text_area(
                "Tamil Translation:",
                value=st.session_state.tamil_translation,
                height=400,
                disabled=True,
                label_visibility="collapsed",
                key="tamil_response"
            )
            if st.button("📋 Copy Tamil Response", key="copy_tam"):
                st.code(st.session_state.tamil_translation, language=None)
                st.success("Tamil response copied! Press Ctrl+C to copy")
        else:
            st.text_area(
                "Tamil Translation:",
                value="Click 'Translate to Tamil' button to get Tamil translation for 10th standard students",
                height=400,
                disabled=True,
                label_visibility="collapsed",
                key="tamil_placeholder"
            )
