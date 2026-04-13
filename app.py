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
# CUSTOM CSS FOR EXACT STYLING & SCROLL FIXES
# ============================================================================
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
    line-height: 1.6 !important;
    white-space: pre-wrap !important;
    word-wrap: break-word !important;
    /* FIX FOR SCROLL POSITION - Force text to top */
    overflow-y: auto !important;
    scroll-behavior: auto !important;
    vertical-align: top !important;
    text-align: left !important;
}

/* SPECIFIC FIX - Force white text in ALL textareas */
textarea {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    /* Ensure text starts at the top */
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

/* FIX: Ensure text area content is visible at top */
div[data-testid="stTextArea"] > div > textarea {
    overflow-y: scroll !important;
    overflow-x: hidden !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================
if "user_query" not in st.session_state:
    st.session_state.user_query = ""
if "chat_response" not in st.session_state:
    st.session_state.chat_response = ""
if "tamil_translation" not in st.session_state:
    st.session_state.tamil_translation = ""
if "topics_list" not in st.session_state:
    st.session_state.topics_list = []

# ============================================================================
# TAMIL SCIENTIFIC VOCABULARY - TN STATE BOARD STANDARD TERMS
# ============================================================================
TAMIL_SCIENCE_VOCAB = {
    # Physics Terms
    "diffusion": "பரவல்",
    "concentration": "செறிவு",
    "particle": "துகள்",
    "movement": "இயக்கம்",
    "uniform": "ஒருபடித்தான",
    "medium": "ஊடகம்",
    "flux": "பாயம்",
    "coefficient": "குணகம்",
    "gradient": "சரிவு",
    "distance": "தூரம்",
    "area": "பரப்பு",
    "time": "நேரம்",
    "formula": "வாய்பாடு",
    "definition": "வரைவிலக்கணம்",
    "concept": "கருத்து",
    "process": "செயல்முறை",
    "rate": "வீதம்",
    "force": "விசை",
    "motion": "இயக்கம்",
    "velocity": "திசைவேகம்",
    "acceleration": "முடுக்கம்",
    "mass": "நிறை",
    "energy": "ஆற்றல்",
    "work": "வேலை",
    "power": "திறன்",
    "pressure": "அழுத்தம்",
    "temperature": "வெப்பநிலை",
    "heat": "வெப்பம்",
    "light": "ஒளி",
    "sound": "ஒலி",
    "current": "மின்னோட்டம்",
    "voltage": "மின்னழுத்தம்",
    "resistance": "மின்தடை",
    "circuit": "மின்சுற்று",
    
    # Chemistry Terms
    "atom": "அணு",
    "molecule": "மூலக்கூறு",
    "element": "தனிமம்",
    "compound": "சேர்மம்",
    "reaction": "வினை",
    "solution": "கரைசல்",
    "acid": "அமிலம்",
    "base": "காரம்",
    "salt": "உப்பு",
    "ion": "அயனி",
    "electron": "எலக்ட்ரான்",
    "proton": "புரோட்டான்",
    "neutron": "நியூட்ரான்",
    "bond": "பிணைப்பு",
    "valency": "இணைதிறன்",
    "atomic number": "அணு எண்",
    "mass number": "நிறை எண்",
    "isotope": "ஐசோடோப்பு",
    "periodic table": "தனிம வரிசை அட்டவணை",
    
    # Biology Terms
    "cell": "உயிரணு",
    "tissue": "திசு",
    "organ": "உறுப்பு",
    "system": "மண்டலம்",
    "plant": "தாவரம்",
    "animal": "விலங்கு",
    "photosynthesis": "ஒளிச்சேர்க்கை",
    "respiration": "சுவாசம்",
    "digestion": "செரிமானம்",
    "circulation": "சுற்றோட்டம்",
    "reproduction": "இனப்பெருக்கம்",
    "gene": "மரபணு",
    "chromosome": "நிறப்புரி",
    "DNA": "டி.என்.ஏ",
    "evolution": "பரிணாமம்",
    "species": "சிற்றினம்",
    
    # Common Academic Terms
    "introduction": "அறிமுகம்",
    "explanation": "விளக்கம்",
    "example": "எடுத்துக்காட்டு",
    "application": "பயன்பாடு",
    "important": "முக்கியமான",
    "note": "குறிப்பு",
    "key": "முக்கிய",
    "point": "புள்ளி",
    "section": "பிரிவு",
    "chapter": "அத்தியாயம்",
    "unit": "அலகு",
    "law": "விதி",
    "principle": "கொள்கை",
    "theory": "கோட்பாடு",
    "experiment": "சோதனை",
    "observation": "கவனிப்பு",
    "conclusion": "முடிவு",
    "summary": "சுருக்கம்"
}

# ============================================================================
# FUNCTION TO CLEAN AND FORMAT TAMIL TRANSLATION
# ============================================================================
def clean_tamil_translation(text):
    if not text:
        return ""
    
    cleaned = text
    
    # Remove LaTeX math delimiters
    cleaned = re.sub(r'\\\(', '', cleaned)
    cleaned = re.sub(r'\\\)', '', cleaned)
    cleaned = re.sub(r'\\\[(.*?)\\\]', r'\1', cleaned, flags=re.DOTALL)
    
    # Remove backslash escape characters
    cleaned = cleaned.replace('\\', '')
    
    # Remove markdown code markers
    cleaned = re.sub(r'`\$?(.*?)\$?`', r'\1', cleaned)
    
    # Clean up extra spaces and newlines
    cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
    cleaned = re.sub(r' +', ' ', cleaned)
    
    # Fix punctuation spacing for Tamil
    cleaned = re.sub(r'\s*([.,:;!?])\s*', r'\1 ', cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    return cleaned.strip()

# ============================================================================
# FUNCTION TO LOAD AND PARSE AllTopic.txt
# ============================================================================
@st.cache_data
def load_topics():
    try:
        with open("AllTopic.txt", "r", encoding="utf-8") as f:
            content = f.read()
        
        topics = []
        pattern = r'^\s*(\d+)\.\s+(.+)$'
        
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('---') or line.startswith('##'):
                continue
            match = re.match(pattern, line)
            if match:
                topic_num = match.group(1)
                topic_text = match.group(2).strip()
                topics.append({
                    'number': topic_num,
                    'text': topic_text,
                    'full': f"{topic_num}. {topic_text}",
                    'search_text': topic_text.lower()
                })
        return topics
    except Exception as e:
        st.error(f"Error loading topics: {e}")
        return []

if not st.session_state.topics_list:
    st.session_state.topics_list = load_topics()

# ============================================================================
# FUNCTION TO SEARCH RELEVANT TOPICS
# ============================================================================
def search_topics(query, topics):
    query_lower = query.lower().strip()
    relevant_topics = []
    
    stop_words = {
        'explain', 'what', 'how', 'why', 'when', 'where', 'the', 'through', 
        'about', 'define', 'describe', 'is', 'are', 'was', 'were', 'be', 
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'can', 'a', 'an', 'and',
        'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from',
        'as', 'it', 'this', 'that', 'these', 'those', 'i', 'you', 'we', 'they'
    }
    
    query_words = [word for word in query_lower.split() if word not in stop_words and len(word) >= 2]
    
    for topic in topics:
        topic_search_text = topic['search_text']
        score = 0
        
        # Method 1: Exact Phrase Match (100 points)
        if query_lower in topic_search_text:
            score += 100
        elif topic_search_text in query_lower:
            score += 80
        
        # Method 2: Word Matching
        words_found = 0
        for word in query_words:
            if word in topic_search_text:
                words_found += 1
        
        # Score calculation
        if len(query_words) > 0:
            match_ratio = words_found / len(query_words)
            if match_ratio == 1.0:
                score += 50
            else:
                score += match_ratio * 30
        
        # Method 3: Multi-word phrase bonus
        if len(query_words) >= 2:
            for i in range(len(query_words) - 1):
                phrase = f"{query_words[i]} {query_words[i+1]}"
                if phrase in topic_search_text:
                    score += 15
        
        if words_found > 0:
            relevant_topics.append({
                'topic': topic,
                'score': score,
                'words_matched': words_found
            })
    
    # Sort by score descending
    relevant_topics.sort(key=lambda x: -x['score'])
    
    return relevant_topics[:10]

# ============================================================================
# TITLE & SUGGESTIONS
# ============================================================================
st.markdown('<h1 class="main-header">⚖️ 10 Standard Student Tamil Nadu State Board Science Subject Chatbot</h1>', unsafe_allow_html=True)

def generate_suggestions(topics):
    if not topics:
        return ["Explain Newton's First Law", "What is electric current?"]
    
    selected = random.sample(topics, min(10, len(topics)))
    suggestions = []
    for topic in selected:
        text = topic['text']
        if text.startswith(('Explain', 'Define', 'Describe', 'What is', 'How')):
            suggestions.append(text)
        else:
            suggestions.append(f"Explain {text.lower()}")
    return suggestions

suggestions = generate_suggestions(st.session_state.topics_list)

st.markdown('<p class="section-header">💡 Suggested Academic Prompts</p>', unsafe_allow_html=True)

cols = st.columns(2)
for i, prompt in enumerate(suggestions):
    col_idx = i % 2
    with cols[col_idx]:
        st.markdown(f"""
        <div class="suggestion-container">
            <div class="suggestion-text">{prompt}</div>
        </div>
        """, unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns([3, 1])
        with col_btn1:
            if st.button("Use Prompt", key=f"use_{i}", use_container_width=True):
                st.session_state.user_query = prompt
                st.session_state.chat_response = ""
                st.session_state.tamil_translation = ""
                st.rerun()
        with col_btn2:
            if st.button("📋", key=f"copy_{i}", help="Copy"):
                st.code(prompt, language=None)

st.divider()

# ============================================================================
# USER INPUT SECTION
# ============================================================================
st.markdown('<p class="section-header">📝 Enter Your Query</p>', unsafe_allow_html=True)

# Use a unique key to force refresh
text_area_key = f"main_input_{len(st.session_state.chat_response) if st.session_state.chat_response else 0}"

user_input = st.text_area(
    "Type your science question here...",
    value="" if st.session_state.chat_response else st.session_state.user_query,
    height=100,
    label_visibility="collapsed",
    key=text_area_key
)

col1, col2, col3 = st.columns(3)
with col1:
    submit_btn = st.button("📤 Submit Prompt", use_container_width=True, key="submit_btn")
with col2:
    translate_btn = st.button("🌐 Translate to Tamil", use_container_width=True, disabled=not st.session_state.chat_response, key="translate_btn")
with col3:
    reset_btn = st.button("🔄 Reset", use_container_width=True, key="reset_btn")

# Sidebar Debug
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    if st.checkbox("Enable Search Debug Mode", value=False):
        st.session_state.debug_mode = True
    else:
        st.session_state.debug_mode = False
    st.markdown(f"📚 **Topics Loaded:** {len(st.session_state.topics_list)}")

# ============================================================================
# API FUNCTION
# ============================================================================
def get_response_from_topics(query, topics):
    try:
        relevant = search_topics(query, topics)
        
        if not relevant:
            return "⚠️ No relevant topics found. Try rephrasing your query."
        
        context_topics = "\n".join([f"{r['topic']['full']}" for r in relevant])
        api_key = st.secrets.get("OPENROUTER_API_KEY")
        
        if not api_key:
            return "⚠️ Configuration Error: API Key not found."
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/TENSCI",
            "X-Title": "TENSCI Chatbot"
        }
        
        system_prompt = f"""You are an academic science tutor.
User Query: "{query}"
Syllabus Topics: {context_topics}
Provide a clear explanation covering: 1. Definition 2. Key Formulas 3. Examples 4. Important points."""

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
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
        return "⚠️ Error: API Response issue."
            
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# ============================================================================
# BUTTON ACTIONS
# ============================================================================

# 1. SUBMIT ACTION
if submit_btn:
    query = user_input.strip()
    if query:
        # Clear results IMMEDIATELY so user sees fresh state
        st.session_state.chat_response = "" 
        st.session_state.tamil_translation = ""
        
        # Save query
        st.session_state.user_query = query
        
        # Perform Search
        with st.spinner("🔍 Searching and retrieving response..."):
            result = get_response_from_topics(query, st.session_state.topics_list)
            st.session_state.chat_response = result
        
        # Rerun to update UI
        st.rerun()
    else:
        st.warning("Please enter a query before submitting.")

# 2. RESET ACTION
if reset_btn:
    st.session_state.user_query = ""
    st.session_state.chat_response = ""
    st.session_state.tamil_translation = ""
    st.rerun()

# 3. TRANSLATE ACTION
if translate_btn and st.session_state.chat_response:
    with st.spinner("🌐 தமிழாக்கம் செய்கிறது..."):
        try:
            translator = GoogleTranslator(source='en', target='ta')
            text = st.session_state.chat_response
            
            # Chunking for long text
            chunks = [text[i:i+4500] for i in range(0, len(text), 4500)]
            translated_parts = []
            for chunk in chunks:
                time.sleep(0.5)
                translated_parts.append(translator.translate(chunk))
            
            raw_tamil = " ".join(translated_parts)
            
            # Vocabulary enhancement
            enhanced = raw_tamil
            for eng, tam in TAMIL_SCIENCE_VOCAB.items():
                pattern = r'\b' + re.escape(eng) + r'\b'
                enhanced = re.sub(pattern, tam, enhanced, flags=re.IGNORECASE)
            
            st.session_state.tamil_translation = clean_tamil_translation(enhanced)
            st.rerun()
        except Exception as e:
            st.error(f"Translation Error: {e}")

# ============================================================================
# DISPLAY RESULTS
# ============================================================================
if st.session_state.chat_response:
    st.divider()
    
    col_eng, col_tam = st.columns(2)
    
    with col_eng:
        st.markdown('<p class="section-header">📖 Retrieved Academic Response (English)</p>', unsafe_allow_html=True)
        st.text_area(
            "English Response:",
            value=st.session_state.chat_response,
            height=500,
            disabled=True,
            label_visibility="collapsed",
            key="english_response_display"
        )
        
    with col_tam:
        st.markdown('<p class="section-header">📚 தமிழ் விளக்கம் (Tamil Translation)</p>', unsafe_allow_html=True)
        if st.session_state.tamil_translation:
            st.text_area(
                "Tamil Translation:",
                value=st.session_state.tamil_translation,
                height=500,
                disabled=True,
                label_visibility="collapsed",
                key="tamil_response_display"
            )
        else:
            st.text_area(
                "Tamil Translation:",
                value="🔄 Click 'Translate to Tamil' to see the translation here.",
                height=500,
                disabled=True,
                label_visibility="collapsed",
                key="tamil_placeholder"
            )

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #6b7280; font-size: 0.9rem;'>
📚 TENSCI Chatbot | 📖 10th Standard TN State Board
</div>
""", unsafe_allow_html=True)
