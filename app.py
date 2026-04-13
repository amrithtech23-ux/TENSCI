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
    line-height: 1.6 !important;
    white-space: pre-wrap !important;
    word-wrap: break-word !important;
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
# FUNCTION TO CLEAN AND FORMAT TAMIL TRANSLATION
# ============================================================================
def clean_tamil_translation(text):
    """
    Clean Tamil translation by removing LaTeX markers, escape characters,
    and formatting into proper paragraphs
    """
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
    
    # Clean up extra spaces and newlines - preserve paragraph structure
    cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
    cleaned = re.sub(r' +', ' ', cleaned)
    
    # Fix punctuation spacing for Tamil
    cleaned = re.sub(r'\s*([.,:;!?])\s*', r'\1 ', cleaned)
    
    # Remove multiple consecutive newlines (keep max 2 for paragraphs)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    # Strip leading/trailing whitespace
    cleaned = cleaned.strip()
    
    return cleaned

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
        # Pattern to match: "295. Chain reaction – self-propagating neutron multiplication process"
        pattern = r'^\s*(\d+)\.\s+(.+)$'
        
       
