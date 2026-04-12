import streamlit as st
import requests
import random

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

# Title
st.markdown('<h1 class="main-header">⚖️ 10 Standard Student Tamil Nadu State Board Science Subject Chatbot</h1>', unsafe_allow_html=True)

# ENHANCED PROMPT POOL - Covering All Units from Knowledge Base
PROMPT_POOL = [
    # UNIT 1: LAWS OF MOTION
    "Explain Newton's First Law of Motion with real-life examples.",
    "What is the difference between mass and weight? Provide formulas.",
    "Derive F = ma from Newton's Second Law of Motion.",
    "How does rocket propulsion demonstrate conservation of momentum?",
    "Define torque and explain its application in a steering wheel.",
    "Explain the principle of moments using a seesaw example.",
    "What is impulse and how is it related to change in momentum?",
    "Explain inertia of rest, motion, and direction with examples.",
    "How does the value of 'g' vary with altitude and depth?",
    "State and explain Newton's Universal Law of Gravitation.",
    "Describe the working of shock absorbers using impulse-momentum theorem.",
    "What are balanced and unbalanced forces? Give examples.",
    
    # UNIT 2: OPTICS
    "Explain the wave nature of light and the formula c = νλ.",
    "State and explain Snell's Law of Refraction with examples.",
    "What is dispersion of light? Explain spectrum formation through a prism.",
    "Explain Rayleigh scattering and why the sky appears blue.",
    "Describe the formation of images by convex and concave lenses.",
    "What is myopia and how is it corrected using lenses?",
    "Explain the working of a simple microscope.",
    "What is total internal reflection? Give its applications.",
    "Describe the structure and working of the human eye.",
    "Explain why clouds appear white (Mie scattering).",
    
    # UNIT 3: THERMAL PHYSICS
    "Explain the difference between heat and temperature.",
    "What is thermal expansion? Explain linear, superficial, and cubical expansion.",
    "State and explain Boyle's Law with mathematical representation.",
    "Describe real and apparent expansion of liquids.",
    "What is specific heat capacity? Explain its significance.",
    "Explain the working principle of a mercury thermometer.",
    "What is absolute zero? Explain the Kelvin temperature scale.",
    
    # UNIT 4: ELECTRICITY
    "State and explain Ohm's Law with formula V = IR.",
    "What is the difference between series and parallel circuits?",
    "Explain the heating effect of electric current and Joule's Law.",
    "Describe the domestic electric circuit and safety measures.",
    "What is the function of a fuse and MCB in household circuits?",
    "Explain the difference between AC and DC current.",
    "What is electrical resistivity? How does it differ from resistance?",
    "Describe the working principle of an LED bulb.",
    "How is electrical energy consumption calculated? Explain kWh.",
    
    # UNIT 5: ACOUSTICS
    "Explain the production and propagation of sound waves.",
    "What is the Doppler Effect? Explain with examples.",
    "Describe the reflection of sound and its applications.",
    "What is an echo? Explain the conditions for hearing a distinct echo.",
    "Explain the difference between musical sound and noise.",
    "What are ultrasonic waves? Give their applications.",
    "Describe the working of SONAR and its uses.",
    "Explain how sound travels faster in solids than in gases.",
    
    # UNIT 6: NUCLEAR PHYSICS
    "What is radioactivity? Explain natural and artificial radioactivity.",
    "Describe the properties of alpha, beta, and gamma rays.",
    "Explain nuclear fission and its applications in power generation.",
    "What is nuclear fusion? How does it differ from fission?",
    "Describe the working principle of an atom bomb.",
    "What are isotopes? Give examples and applications.",
    "Explain the concept of half-life in radioactive decay.",
    "What are the safety measures for handling radioactive materials?",
    
    # UNIT 7: ATOMS AND MOLECULES
    "Explain Dalton's atomic theory and its limitations.",
    "What is the mole concept? Explain Avogadro's number.",
    "Describe the structure of an atom with subatomic particles.",
    "What is the difference between atoms and molecules?",
    "Explain isotopes, isobars, and isotones with examples.",
    "Calculate the molecular mass of H₂SO₄ and CaCO₃.",
    "What is atomicity? Give examples of monoatomic, diatomic molecules.",
    
    # UNIT 8: PERIODIC CLASSIFICATION
    "State the Modern Periodic Law and explain its significance.",
    "Describe the trends in atomic radius across periods and groups.",
    "What is ionization energy? Explain its periodic variation.",
    "Explain electronegativity and its role in bond formation.",
    "Describe the extraction of aluminium from bauxite ore.",
    "What is corrosion? Explain the rusting of iron and prevention methods.",
    "Describe the metallurgy of copper with chemical equations.",
    "What are alloys? Give examples and their uses.",
    
    # UNIT 9: SOLUTIONS
    "What is a solution? Explain solute, solvent, and dissolution.",
    "Describe saturated, unsaturated, and supersaturated solutions.",
    "What factors affect the solubility of substances?",
    "Explain mass percentage and volume percentage concentration.",
    "What is water of crystallization? Give examples of hydrated salts.",
    "Describe hygroscopy and deliquescence with examples.",
    "How does temperature affect the solubility of gases in liquids?",
    
    # UNIT 10: CHEMICAL REACTIONS
    "What are the different types of chemical reactions? Give examples.",
    "Explain combination and decomposition reactions.",
    "Describe displacement and double displacement reactions.",
    "What is a redox reaction? Explain oxidation and reduction.",
    "Explain the pH scale and its significance in daily life.",
    "What is chemical equilibrium? Describe its characteristics.",
    "Describe the factors affecting the rate of chemical reactions.",
    "What is neutralization? Give its applications.",
    
    # UNIT 11: CARBON COMPOUNDS
    "What are the unique properties of carbon?",
    "Explain the classification of hydrocarbons: alkanes, alkenes, alkynes.",
    "Describe the IUPAC nomenclature system for organic compounds.",
    "What are functional groups? Give examples of alcohols and carboxylic acids.",
    "Explain the preparation and properties of ethanol.",
    "Describe the manufacture and uses of ethanoic acid.",
    "What is saponification? Explain the cleansing action of soap.",
    "Compare soaps and detergents. Which is better and why?",
    
    # UNIT 12: PLANT ANATOMY & PHYSIOLOGY
    "Describe the structure of a dicot root with a labeled diagram.",
    "What are the differences between monocot and dicot stems?",
    "Explain the process of photosynthesis with its equation.",
    "Describe the structure of chloroplast and its functions.",
    "What is transpiration? Explain its significance in plants.",
    "Describe aerobic and anaerobic respiration in plants.",
    "What are plant hormones? Explain the functions of auxins.",
    
    # UNIT 13: ANIMAL STRUCTURE
    "Describe the external morphology of a leech.",
    "Explain the digestive system of a rabbit with a diagram.",
    "What are the adaptations of leech for parasitic life?",
    "Describe the circulatory system of rabbit.",
    "Explain the structure of mammalian skin and its derivatives.",
    
    # UNIT 14: TRANSPORT & CIRCULATION
    "Explain the transport of water and minerals in plants.",
    "Describe the structure and functions of blood components.",
    "What is double circulation? Explain with a flow chart.",
    "Describe the structure of the human heart.",
    "Explain the cardiac cycle and heart sounds.",
    "What are blood groups? Explain the ABO system.",
    "Describe the lymphatic system and its functions.",
    
    # UNIT 15: NERVOUS SYSTEM
    "Describe the structure of a neuron with a diagram.",
    "Explain the reflex arc with an example.",
    "What are the different parts of the human brain?",
    "Describe the autonomic nervous system and its divisions.",
    "Explain the structure of the human eye and vision process.",
    "What is a synapse? Explain nerve impulse transmission.",
    
    # GENETICS
    "Explain Mendel's monohybrid cross experiment.",
    "What are the three laws of Mendelian inheritance?",
    "Describe the structure of DNA with a labeled diagram.",
    "Explain the process of DNA replication.",
    "What is sex determination in humans? Explain the mechanism.",
    "Describe chromosomal disorders: Down's syndrome.",
    "What are mutations? Explain types of mutations.",
    
    # EVOLUTION
    "What are homologous and analogous organs? Give examples.",
    "Explain Darwin's theory of natural selection.",
    "Describe Lamarck's theory of inheritance of acquired characters.",
    "What are vestigial organs? Give examples in humans.",
    "Explain the biogenetic law with examples.",
    "Describe fossilization and its importance in evolution.",
    "What is Archaeopteryx? Explain its significance as a connecting link.",
    
    # PLANT BREEDING
    "What is plant breeding? Explain the objectives.",
    "Describe the Green Revolution and its impact.",
    "Explain hybridization technique in crop improvement.",
    "What is mutation breeding? Give examples.",
    "Describe biofortification and its importance.",
    "What is polyploidy breeding? Explain with examples.",
    
    # ANIMAL BREEDING & BIOTECHNOLOGY
    "Explain inbreeding and outbreeding in animal breeding.",
    "What is heterosis or hybrid vigor?",
    "Describe the process of gene cloning.",
    "Explain the applications of biotechnology in medicine.",
    "What are GMOs? Give examples and benefits.",
    "Describe stem cell therapy and its applications.",
    "What is DNA fingerprinting? Explain its uses.",
    
    # HEALTH & DISEASE
    "What are the types of abuse? Explain child abuse prevention.",
    "Describe the hazards of tobacco and alcohol abuse.",
    "Explain diabetes mellitus: types, causes, and management.",
    "What is obesity? Explain BMI calculation and health risks.",
    "Describe cardiovascular diseases and prevention methods.",
    "What is cancer? Explain types and treatment modalities."
]

# Section Header - GREEN color
st.markdown('<p class="section-header">💡 Suggested Academic Prompts</p>', unsafe_allow_html=True)

# Display 10 random prompts in 2 columns with copy buttons
selected_prompts = random.sample(PROMPT_POOL, min(10, len(PROMPT_POOL)))

cols = st.columns(2)
for i, prompt in enumerate(selected_prompts):
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
                    "content": "You are an academic science tutor for 10th Standard Tamil Nadu State Board students. Provide clear, accurate, and curriculum-aligned answers. Use formal academic language. Structure responses with definitions, formulas, examples, and real-life applications. Keep explanations concise, educational, and strictly focused on the TN State Board syllabus covering Physics, Chemistry, and Biology topics."
                },
                {
                    "role": "user",
                    "content": query
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

# Function to translate to Tamil - COMPLETE TRANSLATION
def translate_to_tamil(text):
    try:
        api_key = st.secrets.get("OPENROUTER_API_KEY")
        
        if not api_key:
            return "⚠️ Translation API key not found."
        
        # Check text length and split if necessary
        max_chunk_size = 2000  # Characters per chunk
        
        if len(text) <= max_chunk_size:
            # Single translation for short text
            return translate_chunk(text, api_key)
        else:
            # Chunk-based translation for long text
            chunks = [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]
            translated_chunks = []
            
            for i, chunk in enumerate(chunks):
                translated_chunk = translate_chunk(chunk, api_key)
                translated_chunks.append(translated_chunk)
            
            return "\n\n".join(translated_chunks)
            
    except Exception as e:
        return f"⚠️ Translation Error: {str(e)}"

def translate_chunk(text_chunk, api_key):
    """Translate a single chunk of text to Tamil"""
    try:
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
                    "content": """You are a professional Tamil translator specializing in science education. 
Translate the following science content from English to simple, clear Tamil suitable for 10th standard Tamil medium students in Tamil Nadu State Board.

IMPORTANT INSTRUCTIONS:
1. Translate EVERYTHING completely - definitions, formulas, examples, applications, all sections
2. Keep scientific terms and formulas in English but add Tamil explanation in brackets
3. Use simple Tamil sentences that students can easily understand
4. Maintain all technical accuracy
5. Translate section headings, bullet points, numbered lists completely
6. DO NOT skip any content - translate the entire text
7. Use proper Tamil grammar and vocabulary appropriate for 10th standard students
8. For mathematical formulas, keep them as is but explain in Tamil"""
                },
                {
                    "role": "user",
                    "content": f"Translate this COMPLETELY to Tamil for 10th standard Tamil medium students. Translate every word, every section, every example:\n\n{text_chunk}"
                }
            ],
            "temperature": 0.7,
            "max_tokens": 4000  # Increased for complete translation
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60  # Increased timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                translation = result["choices"][0]["message"]["content"]
                return translation
            else:
                return "⚠️ Translation error: Invalid response format."
        else:
            return f"⚠️ Translation Error {response.status_code}: {response.text}"
            
    except Exception as e:
        return f"⚠️ Translation chunk error: {str(e)}"

# API Call & Response Handling
if submit_btn and user_input.strip():
    with st.spinner("🔍 Retrieving academic response..."):
        st.session_state.chat_response = get_english_response(user_input)
        st.session_state.tamil_translation = ""  # Clear previous translation
        st.rerun()

# Translation Handling
if translate_btn and st.session_state.chat_response:
    with st.spinner("🌐 Translating to Tamil... This may take a moment for complete translation."):
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
                value="🔄 Click 'Translate to Tamil' button above to get complete Tamil translation for 10th standard Tamil medium students.\n\nThe translation will include:\n- Complete definitions\n- All formulas with explanations\n- Real-life applications\n- Examples\n- All sections and points\n\nPlease wait a moment for the complete translation.",
                height=500,
                disabled=True,
                label_visibility="collapsed",
                key="tamil_placeholder"
            )
