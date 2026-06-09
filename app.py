import streamlit as st
import json
from pathlib import Path

# Set premium page config
st.set_page_config(
    page_title="Community RAG Chatbot Dashboard",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling (Dark Mode/Glassmorphism feel)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
        
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Outfit', sans-serif;
            background: linear-gradient(135deg, #090d16 0%, #111029 100%);
            color: #f8fafc;
        }
        
        /* Premium sidebar */
        [data-testid="stSidebar"] {
            background-color: rgba(9, 13, 22, 0.85) !important;
            backdrop-filter: blur(12px);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }
        
        /* Header titles styling */
        .main-title {
            font-size: 2.8rem;
            font-weight: 800;
            background: linear-gradient(to right, #a78bfa, #f43f5e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
        }
        
        .subtitle {
            color: #94a3b8;
            font-size: 1.05rem;
            margin-bottom: 1.5rem;
            font-weight: 300;
        }
        
        /* Glassmorphic cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.02);
            border-radius: 12px;
            padding: 1.2rem;
            border: 1px solid rgba(255, 255, 255, 0.06);
            margin-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar - Select Chatbot
with st.sidebar:
    st.image("https://img.icons8.com/nolan/128/chat.png", width=70)
    st.markdown("### 🤖 Select Chatbot")
    
    # Selection of active chatbot
    selected_bot = st.radio(
        "Choose Community Archive:",
        ["Vagad Patrika Chatbot", "KVO Patrika Chatbot"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 📊 Archive Status")
    
    # Dataset count
    extracted_path = Path("extracted_json")
    json_count = len(list(extracted_path.glob("*.json"))) if extracted_path.exists() else 0
    st.info(f"📁 Vagad Patrika JSONs: {json_count}")
    st.info("📁 KVO Patrika JSONs: 0 (Unprocessed)")

# Change title based on selection
if selected_bot == "Vagad Patrika Chatbot":
    st.markdown('<h1 class="main-title">📖 Vagad Patrika Chatbot</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Mock Chatbot Interface for Vagad Patrika archives (Gujarat/Kutch)</p>', unsafe_allow_html=True)
else:
    st.markdown('<h1 class="main-title">📖 KVO Patrika Chatbot</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Mock Chatbot Interface for Kutchi Visa Oswal (KVO) archives</p>', unsafe_allow_html=True)

# Chat Interface
st.markdown("### 💬 Conversational Chat")
st.write(f"This is a basic interface. Ask any question, and the chatbot will echo your query as a placeholder.")

# Session state initialization for chat messages separate for each chatbot
state_key = f"messages_{selected_bot.lower().replace(' ', '_')}"
if state_key not in st.session_state:
    st.session_state[state_key] = []

# Display chat messages
for msg in st.session_state[state_key]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User Chat Input
user_chat = st.chat_input(f"Type a message for {selected_bot}...")
if user_chat:
    # Append user message
    st.session_state[state_key].append({"role": "user", "content": user_chat})
    with st.chat_message("user"):
        st.write(user_chat)
        
    # Echo back response (No AI logic yet as requested)
    response_text = f"🤖 **{selected_bot} (Mock Echo Response)**\n\nYou asked: *\"{user_chat}\"*\n\n*(Note: This is a placeholder response. Once embeddings and RAG backend logic are implemented, this will answer query using real document retrieval!)*"
    
    st.session_state[state_key].append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.write(response_text)
