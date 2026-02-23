import streamlit as st
import os
import time
import logging
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# --- CONFIGURATION ---
load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    MAX_HISTORY_MESSAGES = 10
    MODEL_NAME = "gemini-1.5-flash"
    TEMPERATURE = 0.7

# --- LOGGER SETUP ---
def setup_logger(name="career_advisor"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        os.makedirs("logs", exist_ok=True)
        fh = logging.FileHandler("logs/app.log")
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
    return logger

logger = setup_logger()

# --- PROMPT TEMPLATES ---
SYSTEM_PROMPT = """You are 'Chatbot AI', a highly professional AI career and professional growth platform.
Your purpose is to provide expert-level guidance across career discovery, resume optimization, and interview preparation.

CRITICAL RULES:
1. Tone: Professional, minimal, encouraging, and highly structured.
2. Content: Strictly professional growth, career pivots, resumes, and technical/behavioral interview prep.
3. Formatting: Use Markdown for headings, checklists, and bold highlights.
4. Personality: Act as a high-end AI dashboard assistant.
"""

def get_mode_prompt(mode: str) -> str:
    prompts = {
        "Career Mode": """You are in 'Career Mode'. Act as a professional career mentor. Provide structured guidance on:
1. **Career Discovery**: Help identify paths based on skills/interests.
2. **Growth Roadmaps**: Provide actionable 30-60-90 day learning plans.
3. **Skill recommendations**: List specific technical and soft skills to master.
Tone: Encouraging and strategic.""",
        
        "Resume Review Mode": """You are in 'Resume Review Mode'. Act as an expert HR reviewer with 15+ years of experience.
1. **Analysis**: Break down the strengths and weaknesses of the provided resume text.
2. **Improvement Checklist**: Provide specific, actionable bullet points for improvement.
3. **ATS Optimization**: Suggest keywords and formatting tips to pass screening.
Tone: Direct, objective, and constructive.""",
        
        "Skill Gap Mode": """You are in 'Skill Gap Mode'. Act as a professional competency assessor.
1. **Analysis**: Identify the delta between the user's current skills and their target role.
2. **Roadmap**: Provide a structured learning path with specific courses, projects, or certifications.
3. **Prioritization**: Rank the most critical gaps to address first.
Tone: Analytical and highly structured.""",
        
        "Mock Interview Mode": """You are in 'Mock Interview Mode'. Act as a clinical and thorough Technical Interviewer.
1. **One Question Rule**: Ask only ONE question at a time.
2. **Wait for Answer**: Do not provide multiple questions or answers in advance.
3. **Feedback Loop**: After receiving an answer, provide brief feedback (Strengths/Improvement) and then move to the next question.
4. **Current Context**: Start by asking the user what role they are interviewing for.
Tone: Professional and slightly formal."""
    }
    return prompts.get(mode, "Mode not recognized. Please provide general professional advice.")

def get_welcome_message(mode: str) -> str:
    welcomes = {
        "Career Mode": """Hello! I am Chatbot AI, your dedicated career strategist. I am here to provide you with structured, data-driven guidance to help you navigate your professional journey.

**How I can assist you today:**
* **Career Discovery**: Identifying roles that match your interests.
* **Industry Analysis**: Providing data on growth sectors and salaries.
* **Skill Gap Analysis**: Highlighting competencies needed for your target position.
* **Strategic Planning**: Outlining a roadmap for your development.""",
        
        "Resume Review Mode": """Hello! I am Chatbot AI, currently in Resume Review Mode. Please paste two things:
1. **Your current resume text**.
2. **The job description** or title you are targeting.

I will then provide an alignment score, ATS optimization tips, and improvement feedback.""",
        
        "Skill Gap Mode": """Hello! I am Chatbot AI. Please tell me:
1. **What is your target role?**
2. **What are your current skills?**

I will analyze what's missing and create a roadmap for you!""",
        
        "Mock Interview Mode": """Hello! I'm Chatbot AI. I'm excited to help you practice your interviewing skills today.
**What is the job title you are interviewing for?**"""
    }
    return welcomes.get(mode, "Hello! How can I assist you in your professional journey today?")

# --- MEMORY MANAGEMENT ---
class ConversationManager:
    def __init__(self, session_state):
        self.session_state = session_state
        if "mode_messages" not in self.session_state:
            self.session_state.mode_messages = {}

    def add_message(self, mode: str, role: str, content: str):
        if mode not in self.session_state.mode_messages:
            self.session_state.mode_messages[mode] = []
        self.session_state.mode_messages[mode].append({"role": role, "content": content})
        self._trim_history(mode)
        
    def get_history(self, mode: str):
        return self.session_state.mode_messages.get(mode, [])

    def clear_history(self, mode: str):
        self.session_state.mode_messages[mode] = []

    def _trim_history(self, mode: str):
        max_msgs = Config.MAX_HISTORY_MESSAGES * 2 
        if len(self.session_state.mode_messages[mode]) > max_msgs:
            self.session_state.mode_messages[mode] = self.session_state.mode_messages[mode][-max_msgs:]

# --- GEMINI SERVICE ---
class GeminiService:
    def __init__(self):
        self.is_configured = False
        if Config.GEMINI_API_KEY and Config.GEMINI_API_KEY != "your_api_key_here":
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.is_configured = True
            
        self.model = genai.GenerativeModel(
            model_name=Config.MODEL_NAME,
            system_instruction=SYSTEM_PROMPT,
            generation_config=genai.types.GenerationConfig(temperature=Config.TEMPERATURE)
        )

    def generate_streaming_response(self, chat_session, user_message: str, current_mode: str):
        if not self.is_configured:
             yield "I cannot respond because the Gemini API Key is not configured."
             return
        try:
            mode_instruction = get_mode_prompt(current_mode)
            context_message = f"[Mode: {current_mode}. Instructions: {mode_instruction}]\n\nUser: {user_message}"
            response = chat_session.send_message(
                context_message,
                stream=True,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH
                }
            )
            for chunk in response:
                if chunk.text: yield chunk.text
        except Exception as e:
            logger.error(f"Gemini Error: {str(e)}")
            yield "I encountered an error connecting to AI services."
            
    def start_chat(self, history=None):
        if not self.is_configured: return None
        formatted_history = []
        for msg in (history or []):
            role = "user" if msg["role"] == "user" else "model"
            formatted_history.append({"role": role, "parts": [msg["content"]]})
        return self.model.start_chat(history=formatted_history)

# --- UI LOGIC ---
st.set_page_config(page_title="Chatbot AI", page_icon="🤖", layout="wide")

gemini_service = GeminiService()
memory_manager = ConversationManager(st.session_state)

st.markdown("""
<style>
    .stApp { background-color: #f8f9fb; color: #1a1a1a; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e9ecef; }
    [data-testid="stSidebar"] > div:first-child { padding-top: 2rem; }
    .sidebar-title-text { font-size: 1.5rem; font-weight: 700; color: #000000 !important; margin-bottom: 1rem; }
    .sidebar-label-text { color: #64748b !important; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.1rem; margin-top: 2rem; text-transform: uppercase; }
    [data-testid="stRadio"] label { padding: 8px 12px; border-radius: 8px; color: #1a1a1a !important; font-weight: 500; transition: all 0.2s; cursor: pointer; }
    [data-testid="stRadio"] label:hover { background-color: #f1f5f9; }
    .status-card { background-color: #fdfdfe; border: 1px solid #edf2f7; border-radius: 12px; padding: 1.25rem; margin-top: auto; }
    .status-dot { height: 8px; width: 8px; background-color: #10b981; border-radius: 50%; display: inline-block; margin-right: 8px; }
    .status-text { font-size: 0.875rem; color: #10b981; font-weight: 500; }
    .main-header { font-size: 2.5rem; font-weight: 700; color: #1a1a1a; text-align: center; margin-top: 3rem; }
    .main-subheader { font-size: 1.125rem; color: #4b5563; text-align: center; margin-bottom: 4rem; }
    .stChatMessage { background-color: transparent !important; }
    .stChatMessage div[data-testid="stMarkdownContainer"] p { color: #1a202c !important; font-size: 1rem; line-height: 1.6; }
    .stMarkdown p, .stMarkdown li, .stMarkdown span { color: #1a202c !important; }
    .stButton > button { border-radius: 8px; font-weight: 500; }
    iframe { display: none; }
</style>
""", unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar-title-text">✨ Chatbot AI</div>', unsafe_allow_html=True)
        st.markdown('<p class="sidebar-label-text">NAVIGATION</p>', unsafe_allow_html=True)
        modes = {"Career Mode": "💬", "Resume Review Mode": "📄", "Skill Gap Mode": "🎯", "Mock Interview Mode": "👤"}
        selected = st.radio("Navigation", options=list(modes.keys()), label_visibility="collapsed", key="active_mode")
        
        st.markdown("<br>", unsafe_allow_html=True)
        def clear():
            memory_manager.clear_history(st.session_state.active_mode)
            st.toast(f"✅ History cleared", icon="🗑️")
        if st.button("🗑️ Clear Chat History", use_container_width=True, on_click=clear): st.rerun()

        st.markdown('<div style="height: 15vh;"></div>', unsafe_allow_html=True)
        st.markdown(f"""<div class="status-card"><p style="font-size: 0.7rem; font-weight: 700; color: #475569 !important; letter-spacing: 0.05rem;">SYSTEM STATUS</p>
        <div style="display: flex; align-items: center;"><span class="status-dot"></span><span class="status-text">Gemini 1.5 Flash Active</span></div></div>""", unsafe_allow_html=True)
        return selected

def render_chat(mode):
    headers = {
        "Career Mode": ("Career", "Ask me anything about your career path."),
        "Resume Review Mode": ("Resume Review", "Upload resume text for ATS feedback."),
        "Skill Gap Mode": ("Skill Gap Analysis", "Identify gaps for your target role."),
        "Mock Interview Mode": ("Mock Interview", "Practice with real-time feedback.")
    }
    title, sub = headers.get(mode, ("Assistant", "How can I help you?"))
    st.markdown(f'<div class="main-header">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="main-subheader">{sub}</div>', unsafe_allow_html=True)
    
    history = memory_manager.get_history(mode)
    if not history:
        memory_manager.add_message(mode, "assistant", get_welcome_message(mode))
        history = memory_manager.get_history(mode)
    for m in history:
        with st.chat_message(m["role"]): st.markdown(m["content"])

def handle_logic(mode):
    st.markdown("""<div class="fixed-footer-hints"><span><b>Shift+Enter</b> new line, <b>Enter</b> send</span><span><b>Ctrl+K</b> clear</span></div>
    <style>.fixed-footer-hints { position: fixed; bottom: 12px; right: 45px; left: 310px; display: flex; justify-content: space-between; font-size: 0.75rem; color: #94a3b8 !important; z-index: 10000; pointer-events: none; }
    .stChatInput { margin-bottom: 10px !important; }</style>""", unsafe_allow_html=True)
    st.components.v1.html("""<script>const doc = window.parent.document; if (!window.parent.__attached) {
        doc.addEventListener('keydown', e => { if (e.ctrlKey && e.key === 'k') { e.preventDefault(); const btn = Array.from(doc.querySelectorAll('button')).find(b => b.textContent.includes('Clear Chat History')); if (btn) btn.click(); }});
        window.parent.__attached = true; }</script>""", height=0)
    
    if prompt := st.chat_input("Type here..."):
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full = ""
            session = gemini_service.start_chat(memory_manager.get_history(mode))
            if session:
                for chunk in gemini_service.generate_streaming_response(session, prompt, mode):
                    full += chunk
                    placeholder.markdown(full + "▌")
                placeholder.markdown(full)
                memory_manager.add_message(mode, "user", prompt)
                memory_manager.add_message(mode, "assistant", full)
            else: st.error("Connection failed.")

if __name__ == "__main__":
    mode = render_sidebar()
    render_chat(mode)
    handle_logic(mode)
