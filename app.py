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
}

/* Force white text in ALL textareas */
textarea {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    display: block;
    padding-top: 10px !important;
}

/* Section headers in GREEN */
.section-header {
    color: #28a745 !important;
    font-weight: bold !important;
    font-size: 1.4rem !important;
    margin: 1rem 0 !important;
}

/* Buttons */
.stButton > button {
    font-weight: bold;
    font-size: 1.1rem;
    border-radius: 6px;
}

/* Headers */
h1, h2, h3, h4, h5, h6 {
    color: #0056b3 !important;
}

/* Suggestions */
.suggestion-container {
    background-color: #f8f9fa;
    border: 2px solid #dee2e6;
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE
# ============================================================================
if 'query_input' not in st.session_state:
    st.session_state.query_input = ""
if 'search_results' not in st.session_state:
    st.session_state.search_results = ""
if 'tamil_translation' not in st.session_state:
    st.session_state.tamil_translation = ""
if 'topics' not in st.session_state:
    st.session_state.topics = []
if 'run_counter' not in st.session_state:
    st.session_state.run_counter = 0

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
        
        payload = {
            "model": "qwen/qwen-2.5-72b-instruct",
            "messages": [
                {"role": "system", "content": f"You are a science tutor for 10th standard TN State Board. Relevant topics:\n{context}"},
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
        else:
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
suggestions = [
    "Explain Newton's First Law of Motion",
    "What is photosynthesis?",
    "Explain Ohm's Law",
    "Describe structure of atom"
]

cols = st.columns(2)
for i, suggestion in enumerate(suggestions):
    with cols[i % 2]:
        if st.button(f"📌 {suggestion}", key=f"sugg_{i}", use_container_width=True):
            st.session_state.query_input = suggestion
            st.session_state.search_results = ""
            st.session_state.tamil_translation = ""
            st.session_state.run_counter += 1
            st.rerun()

st.divider()

# Input Section
st.markdown('<p class="section-header">📝 Enter Your Query</p>', unsafe_allow_html=True)

text_area_key = f"query_input_{st.session_state.run_counter}"

user_query = st.text_area(
    "Type your question:",
    value=st.session_state.query_input if not st.session_state.search_results else "",
    height=100,
    key=text_area_key,
    label_visibility="collapsed"
)

# Buttons
col1, col2, col3 = st.columns(3)

with col1:
    submit_clicked = st.button("📤 Submit", use_container_width=True, key=f"submit_{st.session_state.run_counter}")

with col2:
    translate_clicked = st.button(
        "🌐 Translate to Tamil", 
        use_container_width=True, 
        disabled=not st.session_state.search_results,
        key=f"translate_{st.session_state.run_counter}"
    )

with col3:
    reset_clicked = st.button("🔄 Reset", use_container_width=True, key=f"reset_{st.session_state.run_counter}")

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown(f"📚 Topics Loaded: {len(st.session_state.topics)}")
    debug_mode = st.checkbox("Debug Mode", value=False)

# ============================================================================
# ACTION HANDLERS
# ============================================================================

# SUBMIT
if submit_clicked and user_query.strip():
    st.session_state.search_results = ""
    st.session_state.tamil_translation = ""
    
    st.session_state.query_input = user_query.strip()
    
    with st.spinner("🔍 Searching..."):
        relevant = search_relevant_topics(user_query, st.session_state.topics)
        
        if relevant:
            response = get_ai_response(user_query, relevant)
            st.session_state.search_results = response
        else:
            st.session_state.search_results = "⚠️ No relevant topics found. Try rephrasing."
    
    st.session_state.run_counter += 1
    st.rerun()

# RESET
if reset_clicked:
    st.session_state.query_input = ""
    st.session_state.search_results = ""
    st.session_state.tamil_translation = ""
    st.session_state.run_counter += 1
    st.rerun()

# TRANSLATE
if translate_clicked and st.session_state.search_results:
    with st.spinner("🌐 Translating..."):
        st.session_state.tamil_translation = translate_to_tamil(st.session_state.search_results)
    st.session_state.run_counter += 1
    st.rerun()

# ============================================================================
# DISPLAY RESULTS
# ============================================================================
if st.session_state.search_results:
    st.divider()
    
    col_eng, col_tam = st.columns(2)
    
    with col_eng:
        st.markdown('<p class="section-header">📖 English Response</p>', unsafe_allow_html=True)
        st.text_area(
            "Response",
            value=st.session_state.search_results,
            height=500,
            disabled=True,
            label_visibility="collapsed",
            key=f"eng_{st.session_state.run_counter}"
        )
    
    with col_tam:
        st.markdown('<p class="section-header">📚 Tamil Translation</p>', unsafe_allow_html=True)
        if st.session_state.tamil_translation:
            st.text_area(
                "Translation",
                value=st.session_state.tamil_translation,
                height=500,
                disabled=True,
                label_visibility="collapsed",
                key=f"tam_{st.session_state.run_counter}"
            )
        else:
            st.text_area(
                "Translation",
                value="Click 'Translate to Tamil' button to see Tamil translation",
                height=500,
                disabled=True,
                label_visibility="collapsed",
                key=f"tam_placeholder_{st.session_state.run_counter}"
            )

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #6b7280;'>
📚 TENSCI Chatbot | TN State Board 10th Standard Science
</div>
""", unsafe_allow_html=True) 
