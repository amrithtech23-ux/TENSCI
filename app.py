# app.py
import streamlit as st
import requests
import random
import re
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
# CUSTOM CSS FOR EXACT STYLING REQUIREMENTS
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
# FUNCTION TO LOAD AND PARSE AllTopic.txt
# ============================================================================
@st.cache_data
def load_topics():
    """Load and parse topics from AllTopic.txt file"""
    try:
        with open("AllTopic.txt", "r", encoding="utf-8") as f:
            content = f.read()
        
        topics = []
        pattern = r'^\s*(\d+)\.\s+(.+)$'
        for line in content.split('\n'):
            match = re.match(pattern, line.strip())
            if match:
                topic_num = match.group(1)
                topic_text = match.group(2).strip()
                topics.append({
                    'number': topic_num,
                    'text': topic_text,
                    'full': f"{topic_num}. {topic_text}"
                })
        
        return topics
    except Exception as e:
        st.error(f"Error loading topics: {e}")
        return []

# Load topics on first run
if not st.session_state.topics_list:
    st.session_state.topics_list = load_topics()

# ============================================================================
# FUNCTION TO SEARCH RELEVANT TOPICS
# ============================================================================
def search_topics(query, topics):
    """Search for topics relevant to the user's query"""
    query_lower = query.lower()
    relevant_topics = []
    
    for topic in topics:
        topic_text_lower = topic['text'].lower()
        query_words = query_lower.split()
        match_count = sum(1 for word in query_words if word in topic_text_lower and len(word) > 3)
        
        if match_count > 0:
            relevant_topics.append({
                'topic': topic,
                'score': match_count
            })
    
    relevant_topics.sort(key=lambda x: x['score'], reverse=True)
    return relevant_topics[:10]

# ============================================================================
# TITLE & SUGGESTIONS
# ============================================================================
st.markdown('<h1 class="main-header">⚖️ 10 Standard Student Tamil Nadu State Board Science Subject Chatbot</h1>', unsafe_allow_html=True)

def generate_suggestions(topics):
    """Generate random suggestion prompts from topics"""
    if not topics:
        return [
            "Explain Newton's First Law of Motion",
            "What is electric current?",
            "Explain photosynthesis process",
            "What is Ohm's Law?",
            "Explain the structure of atom"
        ]
    
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
            if st.button("📋", key=f"copy_{i}", help="Copy to clipboard"):
                st.code(prompt, language=None)
                st.success("Copied! Press Ctrl+C to copy")

st.divider()

# ============================================================================
# USER INPUT SECTION
# ============================================================================
st.markdown('<p class="section-header">📝 Enter Your Query</p>', unsafe_allow_html=True)
user_input = st.text_area(
    "Type your science question here...",
    value=st.session_state.user_query,
    height=100,
    label_visibility="collapsed",
    key="main_input"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit_btn = st.button("📤 Submit Prompt", use_container_width=True)
with col2:
    translate_btn = st.button("🌐 Translate to Tamil", use_container_width=True, disabled=not st.session_state.chat_response)
with col3:
    reset_btn = st.button("🔄 Reset", use_container_width=True)

# ============================================================================
# FUNCTION TO GET RESPONSE FROM TOPICS & API
# ============================================================================
def get_response_from_topics(query, topics):
    """Get response by searching topics and using API to explain them"""
    try:
        relevant = search_topics(query, topics)
        
        if not relevant:
            return "⚠️ No relevant topics found in the knowledge base. Please try rephrasing your query.\n\nExample queries:\n- 'Explain electric current'\n- 'What is Ohm's Law?'\n- 'Explain Newton's laws'"
        
        context_topics = "\n".join([f"{r['topic']['full']}" for r in relevant])
        
        api_key = st.secrets.get("OPENROUTER_API_KEY")
        
        if not api_key:
            return "⚠️ Configuration Error: OPENROUTER_API_KEY not found in secrets.toml. Please add your API key."
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/TENSCI",
            "X-Title": "TENSCI Chatbot"
        }
        
        system_prompt = f"""You are an academic science tutor for 10th Standard Tamil Nadu State Board students. 

The user is asking about: "{query}"

Relevant topics from the syllabus:
{context_topics}

Provide a clear, detailed, and curriculum-aligned explanation covering:
1. Definition and concept
2. Key formulas (if applicable)
3. Real-life examples and applications
4. Important points for students to remember

Use formal academic language suitable for Tamil Nadu State Board 10th standard students. Keep explanations concise but comprehensive."""

        payload = {
            "model": "qwen/qwen-2.5-72b-instruct",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Explain the topic(s) related to: {query}"}
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

# ============================================================================
# API CALL & RESPONSE HANDLING
# ============================================================================
if submit_btn and user_input.strip():
    with st.spinner("🔍 Searching topics and retrieving academic response..."):
        st.session_state.chat_response = get_response_from_topics(user_input, st.session_state.topics_list)
        st.session_state.tamil_translation = ""
        st.rerun()

# ============================================================================
# 🔁 TRANSLATION HANDLING WITH GOOGLE TRANSLATE + VOCABULARY ENHANCEMENT
# ============================================================================
if translate_btn and st.session_state.chat_response:
    with st.spinner("🌐 தமிழாக்கம் செய்கிறது..."):
        try:
            english_text = st.session_state.chat_response
            
            # Google Translate has ~5000 char limit - split into chunks
            chunk_size = 4500
            chunks = [english_text[i:i+chunk_size] for i in range(0, len(english_text), chunk_size)]
            translated_chunks = []
            
            translator = GoogleTranslator(source='en', target='ta')
            
            for chunk in chunks:
                # Small delay to avoid rate limiting
                import time
                time.sleep(0.5)
                translated = translator.translate(chunk)
                translated_chunks.append(translated)
            
            raw_tamil = " ".join(translated_chunks)
            
            # Enhance with TN State Board scientific vocabulary
            enhanced_tamil = raw_tamil
            for eng_term, tamil_term in TAMIL_SCIENCE_VOCAB.items():
                # Word boundary regex to avoid partial replacements
                pattern = r'\b' + re.escape(eng_term) + r'\b'
                enhanced_tamil = re.sub(pattern, tamil_term, enhanced_tamil, flags=re.IGNORECASE)
            
            # Post-process: fix spacing/punctuation issues
            fixes = [
                (r"\.(\S)", r". \1"),
                (r",(\S)", r", \1"),
                (r"\s+", " "),
            ]
            for pattern, replacement in fixes:
                enhanced_tamil = re.sub(pattern, replacement, enhanced_tamil)
            
            st.session_state.tamil_translation = enhanced_tamil.strip()
            
        except Exception as e:
            st.session_state.tamil_translation = f"⚠️ மொழிபெயர்ப்பு பிழை: {str(e)}\n\nமாற்றீடு: கைமுறையாக மொழிபெயர்க்க முயற்சிக்கவும் அல்லது பின்னர் முயற்சிக்கவும்."
        
        st.rerun()

# ============================================================================
# RESET HANDLING
# ============================================================================
if reset_btn:
    st.session_state.user_query = ""
    st.session_state.chat_response = ""
    st.session_state.tamil_translation = ""
    st.rerun()

# ============================================================================
# DISPLAY RESULTS - SIDE BY SIDE
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
                height=500,
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
                value="🔄 மேலே உள்ள 'Translate to Tamil' பொத்தானைச் சொடுக்கி, தமிழ்நாடு அரசுப் பாடத்திட்ட 10-ஆம் வகுப்பு அறிவியல் சொற்களைப் பயன்படுத்தி முழுமையான தமிழாக்கத்தைப் பெறவும்.\n\nமொழிபெயர்ப்பில் இவை அடங்கும்:\n- அதிகாரப்பூர்வ தமிழ்ச் சொற்களுடன் முழுமையான வரைவிலக்கணங்கள்\n- தமிழ் விளக்கங்களுடன் அனைத்துச் சூத்திரங்களும்\n- நடைமுறைப் பயன்பாடுகள்\n- எடுத்துக்காட்டுகள்\n- அனைத்துப் பிரிவுகளும் புள்ளிகளும்\n\nமுழுமையான மொழிபெயர்ப்பிற்குச் சிறிது நேரம் காத்திருக்கவும்.",
                height=500,
                disabled=True,
                label_visibility="collapsed",
                key="tamil_placeholder"
            )

# ============================================================================
# FOOTER
# ============================================================================
st.divider()
st.markdown(f"""
<div style='text-align: center; color: #6b7280; font-size: 0.9rem;'>
📚 Knowledge Base: {len(st.session_state.topics_list)} topics loaded from AllTopic.txt<br>
🔤 Tamil Scientific Vocabulary: {len(TAMIL_SCIENCE_VOCAB)} standard terms loaded<br>
🌐 Translation: Google Translate + TN State Board vocabulary enhancement
</div>
""", unsafe_allow_html=True)
