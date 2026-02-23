import streamlit as st
import os
import time

from config import Config
from services.gemini_service import GeminiService
from memory.conversation_manager import ConversationManager
from utils.logger import logger
from prompts.prompt_templates import get_welcome_message

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Chatbot AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLING ---
st.markdown("""
<style>
    /* Global Background */
    .stApp {
        background-color: #f8f9fb;
        color: #1a1a1a;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e9ecef;
    }
    
    /* Sidebar Content Spacing */
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 2rem;
    }

    /* Sidebar Title */
    .sidebar-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .sidebar-label {
        color: #64748b !important;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.1rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        text-transform: uppercase;
    }

    /* Hide default radio selection box and style as menu items */
    [data-testid="stRadio"] div[role="radiogroup"] {
        background-color: transparent;
    }
    
    [data-testid="stRadio"] label {
        padding: 8px 12px;
        border-radius: 8px;
        color: #1a1a1a !important;
        font-weight: 500;
        transition: all 0.2s;
        cursor: pointer;
    }

    [data-testid="stRadio"] label:hover {
        background-color: #f1f5f9;
    }

    /* Custom Status Card */
    .status-card {
        background-color: #fdfdfe;
        border: 1px solid #edf2f7;
        border-radius: 12px;
        padding: 1.25rem;
        margin-top: auto;
    }
    
    .status-dot {
        height: 8px;
        width: 8px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }
    
    .status-text {
        font-size: 0.875rem;
        color: #10b981;
        font-weight: 500;
    }

    /* Main Area Headers */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a1a;
        text-align: center;
        margin-top: 3rem;
        margin-bottom: 0px;
    }
    
    .main-subheader {
        font-size: 1.125rem;
        color: #4b5563;
        text-align: center;
        margin-bottom: 4rem;
        font-weight: 400;
    }

    /* Chat Elements */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
    }
    
    /* Ensure all chat text is visible (Dark Gray/Black) */
    .stChatMessage div[data-testid="stMarkdownContainer"] p {
        color: #1a202c !important;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* Global markdown text visibility */
    .stMarkdown p, .stMarkdown li, .stMarkdown span {
        color: #1a202c !important;
    }

    /* Input Area Hint - Footer Style Below Input */
    .hint-container {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0.25rem;
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 0.25rem;
    }

    .hint-item {
        color: #94a3b8 !important;
    }

    /* Button Styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
    }

    /* JavaScript Injection Style */
    iframe {
        display: none;
    }

</style>
""", unsafe_allow_html=True)

# --- INITIALIZATION ---
gemini_service = GeminiService()
memory_manager = ConversationManager(st.session_state)

def render_sidebar():
    with st.sidebar:
        # Force all sidebar text to be deep black for clarity
        st.markdown("""
        <style>
            [data-testid="stSidebar"] p, 
            [data-testid="stSidebar"] span, 
            [data-testid="stSidebar"] label, 
            [data-testid="stSidebar"] div {
                color: #000000 !important;
            }
            .sidebar-title-text {
                font-size: 1.5rem;
                font-weight: 700;
                color: #000000 !important;
                margin-bottom: 1rem;
            }
            .sidebar-label-text {
                color: #64748b !important;
                font-size: 0.75rem;
                font-weight: 700;
                letter-spacing: 0.1rem;
                margin-top: 2rem;
                margin-bottom: 1rem;
                text-transform: uppercase;
            }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-title-text">✨ Chatbot AI</div>', unsafe_allow_html=True)
        
        st.markdown('<p class="sidebar-label-text">NAVIGATION</p>', unsafe_allow_html=True)
        
        modes = {
            "Career Mode": "💬",
            "Resume Review Mode": "📄",
            "Skill Gap Mode": "🎯",
            "Mock Interview Mode": "👤"
        }
        
        selected_mode = st.radio(
            "Navigation",
            options=list(modes.keys()),
            label_visibility="collapsed",
            index=0,
            key="active_mode"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Function to clear history for callback
        def clear_current_mode():
            memory_manager.clear_history(st.session_state.active_mode)
            st.toast(f"✅ History cleared for {st.session_state.active_mode}", icon="🗑️")
            
        if st.button("🗑️ Clear Chat History", use_container_width=True, on_click=clear_current_mode):
            st.rerun()
            
        # Push to bottom
        st.markdown('<div style="height: 15vh;"></div>', unsafe_allow_html=True)
        
        # System Status Card
        st.markdown(f"""
        <div class="status-card">
            <p style="font-size: 0.7rem; font-weight: 700; color: #475569 !important; margin-bottom: 0.75rem; letter-spacing: 0.05rem;">SYSTEM STATUS</p>
            <div style="display: flex; align-items: center;">
                <span class="status-dot"></span>
                <span class="status-text" style="color: #10b981 !important;">Gemini 1.5 Flash Active</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        return selected_mode

def render_chat(current_mode):
    # Dynamic Headers
    headers = {
        "Career Mode": ("Career", "Ask me anything about your career path or industry trends."),
        "Resume Review Mode": ("Resume Review", "Upload your resume text for AI-powered feedback and ATS optimization."),
        "Skill Gap Mode": ("Skill Gap Analysis", "Identify the delta between your current skills and your target role."),
        "Mock Interview Mode": ("Mock Interview", "Practice your interview skills with real-time feedback and coaching.")
    }
    
    title, subtext = headers.get(current_mode, ("Assistant", "How can I help you today?"))
    
    st.markdown(f'<div class="main-header">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="main-subheader">{subtext}</div>', unsafe_allow_html=True)
    
    # Message Display
    history = memory_manager.get_history(current_mode)
    
    # Auto-add welcome message if history is empty
    if not history:
        welcome = get_welcome_message(current_mode)
        memory_manager.add_message(current_mode, "assistant", welcome)
        history = memory_manager.get_history(current_mode)
        
    for message in history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def handle_mode_logic(current_mode):
    chat_placeholders = {
        "Career Mode": "Type your message...",
        "Resume Review Mode": "Paste resume text here...",
        "Skill Gap Mode": "Describe your skills and target role...",
        "Mock Interview Mode": "Role you're interviewing for..."
    }
    
    # Fixed position footer for hints to ensure they appear BELOW the chat input
    st.markdown("""
    <div class="fixed-footer-hints">
        <span><b>Shift + Enter</b> for new line, <b>Enter</b> to send</span>
        <span><b>Ctrl+K</b> to clear history</span>
    </div>
    <style>
        .fixed-footer-hints {
            position: fixed;
            bottom: 12px;
            right: 45px;
            left: 310px; /* Sidebar width + padding */
            display: flex;
            justify-content: space-between;
            font-size: 0.75rem;
            color: #94a3b8 !important;
            z-index: 10000;
            pointer-events: none;
            background: transparent;
        }
        /* Extra padding for chat input to make room for hints if needed */
        .stChatInput {
            margin-bottom: 10px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Keyboard Shortcuts Logic (JS Injection)
    # We use a flag on window.parent to prevent multiple listeners
    st.components.v1.html(f"""
    <script>
    const parentDoc = window.parent.document;
    const parentWindow = window.parent;
    
    if (!parentWindow.__chatbot_shortcuts_attached) {{
        console.log("Chatbot AI: Attaching keyboard shortcuts...");
        
        parentDoc.addEventListener('keydown', function(e) {{
            // Ctrl+K to clear history
            if (e.ctrlKey && e.key.toLowerCase() === 'k') {{
                console.log("Chatbot AI: Ctrl+K detected");
                e.preventDefault();
                
                // Find the clear button by text content
                const buttons = Array.from(parentDoc.querySelectorAll('button'));
                const clearBtn = buttons.find(b => b.textContent && b.textContent.includes('Clear Chat History'));
                
                if (clearBtn) {{
                    console.log("Chatbot AI: Triggering clear button");
                    clearBtn.click();
                }} else {{
                    console.warn("Chatbot AI: Clear button not found");
                }}
            }}
        }});
        
        parentWindow.__chatbot_shortcuts_attached = true;
    }}
    </script>
    """, height=0)
    
    if prompt := st.chat_input(chat_placeholders.get(current_mode, "Type here...")):
        # User message
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Assistant Response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            history = memory_manager.get_history(current_mode)
            chat_session = gemini_service.start_chat(history)
            
            if chat_session:
                for chunk in gemini_service.generate_streaming_response(
                    chat_session, 
                    prompt, 
                    current_mode
                ):
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
                # Save to specific mode history
                memory_manager.add_message(current_mode, "user", prompt)
                memory_manager.add_message(current_mode, "assistant", full_response)
            else:
                st.error("Connection failed. Please check your API configuration.")

# --- MAIN RENDER ---
def main():
    selected_mode = render_sidebar()
    render_chat(selected_mode)
    handle_mode_logic(selected_mode)

if __name__ == "__main__":
    main()

# End of app logic
