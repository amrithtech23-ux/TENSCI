# app.py
import streamlit as st
import requests
import random
import re
import time
from deep_translator import GoogleTranslator

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="TENSCI Chatbot",
    page_icon="⚖️",
    layout="wide"
)

# ============================================================================
# CUSTOM CSS
# ============================================================================
st.markdown("""
<style>
/* Main title */
.main-header {
    color: #0056b3 !important;
    font-weight: bold !important;
    font-size: 2rem !important;
    text-align: center !important;
    margin-bottom: 2rem !important;
}

/* Text area styling - Blue background, WHITE text */
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
    line-height: 1.6 !important;
    white-space: pre-wrap !important;
    word-wrap: break-word !important;
    overflow-y: auto !important;
    scroll-behavior: auto !important;
    vertical-align: top !important;
    text-align: left !important;
    padding-top: 10px !important;
    padding-left: 10px !important;
    /* REMOVED: height: 300% !important; - This was interfering */
}

/* Force white text in ALL textareas */
textarea {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    display: block !important;
}

/* Section headers */
.section-header {
    color: #28a745 !important;
    font-weight: bold !important;
    font-size: 1.4rem !important;
    margin: 1rem 0 !important;
}

/* Suggestions */
.suggestion-container {
    background-color: #f8f9fa;
    border: 2px solid #dee2e6;
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
}



/* Buttons */
.stButton > button {
    font-weight: bold;background: linear-gradient(135deg, #059669, #047857) !important;
    font-size: 1.1rem;color: white !important;
    border-radius: 6px;
}

/* Headers */
h1, h2, h3, h4, h5, h6 {
    color: #0056b3 !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if 'query_input' not in st.session_state:
    st.session_state.query_input = ""
if 'chat_response' not in st.session_state:
    st.session_state.chat_response = ""
if 'tamil_translation' not in st.session_state:
    st.session_state.tamil_translation = ""
if 'topics' not in st.session_state:
    st.session_state.topics = []

# ============================================================================
# TAMIL VOCABULARY
# ============================================================================
TAMIL_VOCAB = {
    "diffusion": "பரவல்", "concentration": "செறிவு", "particle": "துகள்",
    "force": "விசை", "motion": "இயக்கம்", "energy": "ஆற்றல்",
    "atom": "அணு", "molecule": "மூலக்கூறு", "reaction": "வினை",
    "cell": "உயிரணு", "photosynthesis": "ஒளிச்சேர்க்கை",
    "current": "மின்னோட்டம்", "voltage": "மின்னழுத்தம்"
}

# ============================================================================
# LOAD TOPICS
# ============================================================================
@st.cache_data
def load_topics_from_file():
    try:
        with open("AllTopic.txt", "r", encoding="utf-8") as f:
            content = f.read()
        topics = []
        pattern = r'^\s*(\d+)\.\s+(.+)$'
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            match = re.match(pattern, line)
            if match:
                topics.append({
                    'number': match.group(1),
                    'text': match.group(2).strip(),
                    'search_text': match.group(2).lower()
                })
        return topics
    except Exception as e:
        st.error(f"Error loading topics: {e}")
        return []

if not st.session_state.topics:
    st.session_state.topics = load_topics_from_file()

# ============================================================================
# SEARCH FUNCTION
# ============================================================================
def search_relevant_topics(query, topics_list):
    query_lower = query.lower().strip()
    stop_words = {'explain', 'what', 'how', 'the', 'and', 'or', 'is', 'are'}
    query_words = [w for w in query_lower.split() if w not in stop_words and len(w) > 2]
    
    scored_topics = []
    for topic in topics_list:
        topic_text = topic['search_text']
        score = 0
        if query_lower in topic_text:
            score = 100
        else:
            matches = sum(1 for word in query_words if word in topic_text)
            if matches > 0:
                score = (matches / len(query_words)) * 50
        if score > 0:
            scored_topics.append((score, topic))
    scored_topics.sort(key=lambda x: -x[0])
    return [topic for score, topic in scored_topics[:10]]

# ============================================================================
# API FUNCTION
# ============================================================================
def get_ai_response(query, relevant_topics):
    try:
        api_key = st.secrets.get("OPENROUTER_API_KEY")
        if not api_key:
            return "⚠️ API key not configured"
        
        context = "\n".join([f"{t['number']}. {t['text']}" for t in relevant_topics[:5]])
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # FIXED SYSTEM PROMPT: Explicitly forbids conversational filler words
        system_prompt = f"""You are an academic science tutor for 10th Standard Tamil Nadu State Board students. 
The user is asking about: "{query}"
Relevant topics: {context}

INSTRUCTIONS:
1. Start DIRECTLY with the explanation.
2. DO NOT use conversational fillers like "Certainly!", "Sure!", "Okay", "Of course", or "Here is the explanation".
3. Use formal academic language.
4. Provide definition, formulas, and examples clearly."""

        payload = {
            "model": "qwen/qwen-2.5-72b-instruct",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Explain: {query}"}
            ],
            "temperature": 0.6,
            "max_tokens": 2000
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=45
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return f"⚠️ API Error: {response.status_code}"
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# ============================================================================
# TRANSLATION FUNCTION
# ============================================================================
def translate_to_tamil(text):
    try:
        translator = GoogleTranslator(source='en', target='ta')
        chunks = [text[i:i+4500] for i in range(0, len(text), 4500)]
        translated = []
        for chunk in chunks:
            time.sleep(0.5)
            translated.append(translator.translate(chunk))
        result = " ".join(translated)
        for eng, tam in TAMIL_VOCAB.items():
            result = re.sub(r'\b' + eng + r'\b', tam, result, flags=re.IGNORECASE)
        return result
    except Exception as e:
        return f"Translation error: {str(e)}"

# ============================================================================
# MAIN UI
# ============================================================================
st.markdown('<h1 class="main-header">⚖️ 10th Standard TN State Board Science Chatbot</h1>', unsafe_allow_html=True)

# Suggestions
st.markdown('<p class="section-header">💡 Suggested Prompts</p>', unsafe_allow_html=True)
suggestions = ["Explain Newton's First Law", "What is photosynthesis?", "Explain Ohm's Law"]
cols = st.columns(len(suggestions))
for i, suggestion in enumerate(suggestions):
    with cols[i]:
        if st.button(f"📌 {suggestion}", key=f"sugg_{i}", use_container_width=True):
            st.session_state.query_input = suggestion
            st.session_state.chat_response = ""
            st.session_state.tamil_translation = ""
            st.rerun()

st.divider()

# Input Section
st.markdown('<p class="section-header">📝 Enter Your Query</p>', unsafe_allow_html=True)

# Bind text area to query_input state variable
user_query = st.text_area(
    "Type your question:",
    value=st.session_state.query_input,
    height=100,
    key="main_input_area",
    label_visibility="collapsed"
)

# Buttons
col1, col2, col3 = st.columns(3)
with col1:
    submit_clicked = st.button("📤 Submit", use_container_width=True, key="submit_btn")
with col2:
    translate_clicked = st.button("🌐 Translate to Tamil", use_container_width=True, disabled=not st.session_state.chat_response, key="translate_btn")
with col3:
    reset_clicked = st.button("🔄 Reset", use_container_width=True, key="reset_btn")

# ============================================================================
# ACTION HANDLERS
# ============================================================================

# SUBMIT
if submit_clicked:
    current_query = user_query.strip()
    
    if current_query:
        # Clear previous results
        st.session_state.chat_response = ""
        st.session_state.tamil_translation = ""
        
        # Update input
        st.session_state.query_input = current_query
        
        # Perform Search
        with st.spinner("🔍 Searching..."):
            relevant = search_relevant_topics(current_query, st.session_state.topics)
            if relevant:
                st.session_state.chat_response = get_ai_response(current_query, relevant)
            else:
                st.session_state.chat_response = "⚠️ No relevant topics found. Try rephrasing."
        
        st.rerun()

# RESET
if reset_clicked:
    st.session_state.query_input = ""
    st.session_state.chat_response = ""
    st.session_state.tamil_translation = ""
    st.rerun()

# TRANSLATE
if translate_clicked and st.session_state.chat_response:
    with st.spinner("🌐 Translating..."):
        st.session_state.tamil_translation = translate_to_tamil(st.session_state.chat_response)
    st.rerun()

# ============================================================================
# DISPLAY RESULTS - INCREASED HEIGHT TO 800 PIXELS
# ============================================================================
if st.session_state.chat_response:
    st.divider()
    col_eng, col_tam = st.columns(2)
    
    with col_eng:
        st.markdown('<p class="section-header">📖 English Response</p>', unsafe_allow_html=True)
        st.text_area(
            "Response",
            value=st.session_state.chat_response,
            height=1200,  # INCREASED FROM 500 TO 800
            disabled=True,
            label_visibility="collapsed",
            key="eng_response"
        )
    
    with col_tam:
        st.markdown('<p class="section-header">📚 Tamil Translation</p>', unsafe_allow_html=True)
        if st.session_state.tamil_translation:
            st.text_area(
                "Translation",
                value=st.session_state.tamil_translation,
                height=1200,  # INCREASED FROM 500 TO 800
                disabled=True,
                label_visibility="collapsed",
                key="tam_response"
            )
        else:
            st.text_area(
                "Translation",
                value="Click 'Translate to Tamil' button to see Tamil translation",
                height=1200,  # INCREASED FROM 500 TO 800
                disabled=True,
                label_visibility="collapsed",
                key="tam_placeholder"
            )

st.markdown("<div style='text-align:center; color:#6b7280; margin-top:20px;'>TENSCI Chatbot | TN State Board 10th Science</div>", unsafe_allow_html=True)
