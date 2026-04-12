import streamlit as st
import requests
import random
import re

# Page Configuration
st.set_page_config(
    page_title="TENSCI Chatbot",
    page_icon="⚖️",
    layout="wide"
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
if "topics_list" not in st.session_state:
    st.session_state.topics_list = []

# Tamil Scientific Vocabulary - TN State Board Standard Terms
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

# Function to load and parse AllTopic.txt
@st.cache_data
def load_topics():
    """Load and parse topics from AllTopic.txt file"""
    try:
        with open("AllTopic.txt", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Parse topics - extract all numbered topics
        topics = []
        # Match patterns like "1. Topic text" or "151. Electric current..."
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

# Function to search relevant topics
def search_topics(query, topics):
    """Search for topics relevant to the user's query"""
    query_lower = query.lower()
    relevant_topics = []
    
    for topic in topics:
        topic_text_lower = topic['text'].lower()
        # Check if query words appear in topic
        query_words = query_lower.split()
        match_count = sum(1 for word in query_words if word in topic_text_lower and len(word) > 3)
        
        if match_count > 0:
            relevant_topics.append({
                'topic': topic,
                'score': match_count
            })
    
    # Sort by relevance score
    relevant_topics.sort(key=lambda x: x['score'], reverse=True)
    return relevant_topics[:10]  # Return top 10 relevant topics

# Title
st.markdown('<h1 class="main-header">⚖️ 10 Standard Student Tamil Nadu State Board Science Subject Chatbot</h1>', unsafe_allow_html=True)

# Generate suggestion prompts from topics
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
    
    # Select random topics and convert to questions
    selected = random.sample(topics, min(10, len(topics)))
    suggestions = []
    for topic in selected:
        text = topic['text']
        # Convert topic to question format
        if text.startswith(('Explain', 'Define', 'Describe', 'What is', 'How')):
            suggestions.append(text)
        else:
            suggestions.append(f"Explain {text.lower()}")
    
    return suggestions

# Get suggestions
suggestions = generate_suggestions(st.session_state.topics_list)

# Section Header - GREEN color
st.markdown('<p class="section-header">💡 Suggested Academic Prompts</p>', unsafe_allow_html=True)

# Display 10 random prompts in 2 columns with copy buttons
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

# Text Field 1: User Input
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

# Function to get response using topics and API
def get_response_from_topics(query, topics):
    """Get response by searching topics and using API to explain them"""
    try:
        # Search for relevant topics
        relevant = search_topics(query, topics)
        
        if not relevant:
            return "⚠️ No relevant topics found in the knowledge base. Please try rephrasing your query.\n\nExample queries:\n- 'Explain electric current'\n- 'What is Ohm's Law?'\n- 'Explain Newton's laws'"
        
        # Build context from relevant topics
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
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Explain the topic(s) related to: {query}"
                }
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
                content = result["choices"][0]["message"]["content"]
                
                # Return ONLY the content - NO "Relevant Topics Found" section
                return content
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

# API Call & Response Handling
if submit_btn and user_input.strip():
    with st.spinner("🔍 Searching topics and retrieving academic response..."):
        st.session_state.chat_response = get_response_from_topics(user_input, st.session_state.topics_list)
        st.session_state.tamil_translation = ""  # Clear previous translation
        st.rerun()

# Translation Handling with Tamil Scientific Vocabulary
if translate_btn and st.session_state.chat_response:
    with st.spinner("🌐 Translating to Tamil with TN State Board vocabulary..."):
        try:
            api_key = st.secrets.get("OPENROUTER_API_KEY")
            
            if not api_key:
                st.session_state.tamil_translation = "⚠️ Translation API key not found."
            else:
                # Build vocabulary instruction
                vocab_list = "\n".join([f"- {eng}: {tam}" for eng, tam in list(TAMIL_SCIENCE_VOCAB.items())[:30]])
                
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
                            "content": f"""You are a professional Tamil translator specializing in Tamil Nadu State Board 10th standard science education.

CRITICAL REQUIREMENTS:
1. Use ONLY Tamil Nadu State Board approved scientific terminology
2. Translate EVERYTHING completely - definitions, formulas, examples, all sections
3. Keep formulas and equations in English/symbols but explain in Tamil
4. Use simple, clear Tamil sentences suitable for Tamil medium students
5. Maintain technical accuracy with official TN State Board vocabulary
6. DO NOT skip any content - translate the entire text word by word
7. Use proper Tamil grammar appropriate for 10th standard level

STANDARD TAMIL SCIENTIFIC VOCABULARY (Use these terms):
{vocab_list}
... and more terms from TN State Board textbook

For terms not in the list, use commonly accepted Tamil scientific terms from TN State Board textbooks.

Translate section headings, bullet points, numbered lists completely.
Keep mathematical symbols and formulas as is but provide Tamil explanation."""
                        },
                        {
                            "role": "user",
                            "content": f"Translate this science content to Tamil using TN State Board 10th standard vocabulary. Translate EVERY word, section, and example:\n\n{st.session_state.chat_response}"
                        }
                    ],
                    "temperature": 0.6,
                    "max_tokens": 4000
                }
                
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "choices" in result and len(result["choices"]) > 0:
                        st.session_state.tamil_translation = result["choices"][0]["message"]["content"]
                    else:
                        st.session_state.tamil_translation = "⚠️ Translation error: Invalid response format."
                else:
                    st.session_state.tamil_translation = f"⚠️ Translation Error {response.status_code}: {response.text}"
                    
        except Exception as e:
            st.session_state.tamil_translation = f"⚠️ Translation Error: {str(e)}"
        
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
                value="🔄 Click 'Translate to Tamil' button above to get complete Tamil translation using TN State Board 10th standard scientific vocabulary.\n\nThe translation will include:\n- Complete definitions with official Tamil terms\n- All formulas with Tamil explanations\n- Real-life applications\n- Examples\n- All sections and points\n\nPlease wait a moment for the complete translation.",
                height=500,
                disabled=True,
                label_visibility="collapsed",
                key="tamil_placeholder"
            )

# Footer with topic count
st.divider()
st.markdown(f"""
<div style='text-align: center; color: #6b7280; font-size: 0.9rem;'>
📚 Knowledge Base: {len(st.session_state.topics_list)} topics loaded from AllTopic.txt<br>
🔤 Tamil Scientific Vocabulary: {len(TAMIL_SCIENCE_VOCAB)} standard terms loaded
</div>
""", unsafe_allow_html=True)
