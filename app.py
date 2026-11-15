import os
import sys
import json
import datetime

# Force Python to look in the directory where app.py lives for local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import streamlit as st
from dotenv import load_dotenv
from google import genai
from database import SessionLocal
from models import OfficialDoc


# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="CampusAI 2.0",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# Premium design system — Dark Navy + Electric Violet
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    /* Backgrounds */
    --bg-primary: #090D1A;
    --bg-secondary: #10172A;
    --bg-card: #151F35;
    --bg-elevated: #1C2942;
    --bg-input: #0E1427;

    /* Accents */
    --accent-primary: #8B5CF6;
    --accent-primary-hover: #7C3AED;
    --accent-secondary: #38BDF8;
    --accent-highlight: #A78BFA;
    --accent-glow: rgba(139, 92, 246, 0.25);

    /* Text */
    --text-primary: #F8FAFC;
    --text-secondary: #CBD5E1;
    --text-muted: #94A3B8;
    --text-inverse: #090D1A;

    /* Borders & dividers */
    --border: #293750;
    --border-focus: #8B5CF6;

    /* Status colors */
    --success: #34D399;
    --success-bg: rgba(52, 211, 153, 0.10);
    --warning: #FBBF24;
    --warning-bg: rgba(251, 191, 36, 0.10);
    --error: #FB7185;
    --error-bg: rgba(251, 113, 133, 0.10);
    --info: #38BDF8;
    --info-bg: rgba(56, 189, 248, 0.10);

    /* Radii & shadows */
    --radius: 10px;
    --radius-lg: 14px;
    --shadow: 0 4px 20px rgba(0, 0, 0, 0.30);
    --shadow-hover: 0 8px 30px rgba(0, 0, 0, 0.40);
    --shadow-glow: 0 0 24px rgba(139, 92, 246, 0.15);

    /* Transitions */
    --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-base: 220ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1);
}

/* Reset & base */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background-color: var(--bg-primary);
    color: var(--text-primary);
}

.stApp {
    background-color: var(--bg-primary);
}

/* Hide Streamlit branding */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* Main container */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
    background-color: transparent;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary);
    font-weight: 700;
    letter-spacing: -0.02em;
    font-family: 'Inter', sans-serif;
    margin-top: 0;
}

h1 {
    font-size: 2.25rem;
    line-height: 1.15;
    margin-bottom: 0.5rem;
}

h2 {
    font-size: 1.5rem;
    line-height: 1.2;
    margin-bottom: 0.5rem;
}

h3 {
    font-size: 1.125rem;
    line-height: 1.25;
    margin-bottom: 0.5rem;
}

p, .stMarkdown, .stText, .stCaption {
    color: var(--text-secondary);
    line-height: 1.6;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: var(--bg-secondary);
    border-right: 1px solid var(--border);
    width: 260px;
}

section[data-testid="stSidebar"] .stRadio > div,
section[data-testid="stSidebar"] .stSelectbox > div {
    background-color: transparent;
}

section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stRadio label {
    color: var(--text-secondary);
    font-weight: 600;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Sidebar navigation items */
section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: var(--radius);
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    color: var(--text-muted);
    font-weight: 500;
    font-size: 0.9rem;
    transition: all var(--transition-base);
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:hover {
    background-color: var(--bg-card);
    border-color: var(--border);
    color: var(--text-secondary);
}

section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label[data-checked="true"],
section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label[aria-checked="true"] {
    background-color: var(--accent-glow);
    border-color: var(--accent-primary);
    color: var(--accent-primary);
}

/* Sidebar header / logo */
.sidebar-brand {
    padding: 1.5rem 1rem 1rem 1rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid var(--border);
}

.sidebar-brand h1 {
    font-size: 1.25rem;
    margin: 0;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.sidebar-brand .brand-mark {
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    color: var(--text-primary);
    font-size: 0.875rem;
}

.sidebar-user {
    padding: 1rem;
    background-color: var(--bg-card);
    border-radius: var(--radius);
    border: 1px solid var(--border);
    margin: 1rem;
    margin-bottom: 2rem;
}

.sidebar-user .user-name {
    font-weight: 600;
    color: var(--text-primary);
    font-size: 0.9rem;
}

.sidebar-user .user-role {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 0.25rem;
}

.sidebar-divider {
    margin: 1rem 1rem 0.5rem 1rem;
    border: none;
    height: 1px;
    background-color: var(--border);
}

/* Buttons - Primary */
.stButton > button {
    background-color: var(--accent-primary);
    color: var(--text-inverse);
    border: none;
    border-radius: var(--radius);
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    font-size: 0.925rem;
    transition: all var(--transition-base);
    width: 100%;
    box-shadow: 0 4px 12px rgba(139, 92, 246, 0.20);
}

.stButton > button:hover {
    background-color: var(--accent-primary-hover);
    transform: translateY(-1px);
    box-shadow: var(--shadow-glow);
}

.stButton > button:active {
    transform: translateY(0);
}

/* Buttons - Secondary / Outline */
.stButton button[kind="secondary"] {
    background-color: transparent;
    color: var(--accent-primary);
    border: 1px solid var(--accent-primary);
    border-radius: var(--radius);
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    font-size: 0.925rem;
    transition: all var(--transition-base);
    width: 100%;
}

.stButton button[kind="secondary"]:hover {
    background-color: var(--accent-primary);
    color: var(--text-inverse);
}

/* Buttons - Ghost */
.stButton button[kind="ghost"],
.stButton > button[data-kind="ghost"] {
    background-color: transparent;
    color: var(--text-secondary);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 0.625rem 1.25rem;
    font-weight: 500;
    font-size: 0.9rem;
    transition: all var(--transition-base);
    width: auto;
}

.stButton button[kind="ghost"]:hover,
.stButton > button[data-kind="ghost"]:hover {
    background-color: var(--bg-card);
    border-color: var(--border);
    color: var(--text-primary);
}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    background-color: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--text-primary);
    font-size: 0.925rem;
    padding: 0.75rem 1rem;
    transition: all var(--transition-fast);
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div > div:focus {
    border-color: var(--border-focus);
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.10);
    outline: none;
}

.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stFileUploader label {
    color: var(--text-secondary);
    font-weight: 500;
    font-size: 0.875rem;
    margin-bottom: 0.5rem;
}

/* File uploader */
.stFileUploader {
    border: 2px dashed var(--border);
    border-radius: var(--radius-lg);
    padding: 2.5rem;
    text-align: center;
    background-color: var(--bg-card);
    transition: all var(--transition-base);
}

.stFileUploader:hover {
    border-color: var(--accent-primary);
    background-color: var(--bg-elevated);
}

/* Cards */
.premium-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.75rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow);
    transition: all var(--transition-base);
}

.premium-card:hover {
    border-color: var(--accent-primary);
    transform: translateY(-2px);
    box-shadow: var(--shadow-hover);
}

.premium-card h3 {
    color: var(--text-primary);
    font-size: 1.125rem;
    margin-bottom: 0.5rem;
}

.premium-card p {
    color: var(--text-muted);
    font-size: 0.9rem;
    line-height: 1.5;
    margin: 0;
}

/* Metric cards */
.metric-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    box-shadow: var(--shadow);
    transition: all var(--transition-base);
}

.metric-card:hover {
    border-color: var(--accent-primary);
    transform: translateY(-2px);
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
}

.metric-label {
    font-size: 0.8rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 0.5rem;
    margin-bottom: 0;
}

.metric-trend {
    font-size: 0.8rem;
    font-weight: 600;
    margin-top: 0.5rem;
}

.metric-trend.pos {
    color: var(--success);
}

.metric-trend.neg {
    color: var(--error);
}

/* Feature grid */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
}

/* Divider */
.divider {
    border: none;
    height: 1px;
    background-color: var(--border);
    margin: 2.5rem 0;
}

.divider-sm {
    border: none;
    height: 1px;
    background-color: var(--border);
    margin: 1.5rem 0;
}

/* Alerts / Badges */
.alert {
    padding: 1rem 1.25rem;
    border-radius: var(--radius);
    margin-bottom: 1rem;
    font-size: 0.925rem;
    font-weight: 500;
    border: none;
}

.alert-success {
    background-color: var(--success-bg);
    color: var(--success);
    border-left: 4px solid var(--success);
}

.alert-error {
    background-color: var(--error-bg);
    color: var(--error);
    border-left: 4px solid var(--error);
}

.alert-warning {
    background-color: var(--warning-bg);
    color: var(--warning);
    border-left: 4px solid var(--warning);
}

.alert-info {
    background-color: var(--info-bg);
    color: var(--info);
    border-left: 4px solid var(--info);
}

.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.625rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.badge-violet {
    background-color: rgba(139, 92, 246, 0.15);
    color: var(--accent-primary);
    border: 1px solid rgba(139, 92, 246, 0.30);
}

.badge-cyan {
    background-color: rgba(56, 189, 248, 0.15);
    color: var(--accent-secondary);
    border: 1px solid rgba(56, 189, 248, 0.30);
}

.badge-green {
    background-color: rgba(52, 211, 153, 0.15);
    color: var(--success);
    border: 1px solid rgba(52, 211, 153, 0.30);
}

.badge-amber {
    background-color: rgba(251, 191, 36, 0.15);
    color: var(--warning);
    border: 1px solid rgba(251, 191, 36, 0.30);
}

.badge-rose {
    background-color: rgba(251, 113, 133, 0.15);
    color: var(--error);
    border: 1px solid rgba(251, 113, 133, 0.30);
}

/* Animations */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

@keyframes slideInRight {
    from { opacity: 0; transform: translateX(20px); }
    to   { opacity: 1; transform: translateX(0); }
}

@keyframes typing {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-4px); }
}

.animate-fade-in {
    animation: fadeInUp var(--transition-slow) ease-out forwards;
}

.animate-slide-in {
    animation: slideInRight var(--transition-slow) ease-out forwards;
}

.animate-pulse {
    animation: pulse 2s ease-in-out infinite;
}

.stagger-1 { animation-delay: 0.1s; }
.stagger-2 { animation-delay: 0.2s; }
.stagger-3 { animation-delay: 0.3s; }
.stagger-4 { animation-delay: 0.4s; }

/* Login containers */
.login-wrapper {
    max-width: 440px;
    margin: 4rem auto;
    padding: 0 1rem;
}

.login-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 2.5rem;
    box-shadow: var(--shadow-hover);
}

.login-header {
    margin-bottom: 2rem;
}

.login-header h1 {
    font-size: 1.875rem;
    margin-bottom: 0.25rem;
}

.login-header p {
    color: var(--text-muted);
    font-size: 0.925rem;
    margin: 0;
}

/* Chat messages */
.message-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 2rem;
}

.message {
    display: flex;
    gap: 0.75rem;
    margin-bottom: 1rem;
}

.message-avatar {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.875rem;
    flex-shrink: 0;
}

.message-avatar.user {
    background-color: var(--accent-secondary);
    color: var(--text-inverse);
}

.message-avatar.ai {
    background-color: var(--accent-primary);
    color: var(--text-inverse);
}

.message-bubble {
    max-width: 75%;
    padding: 1rem 1.25rem;
    border-radius: var(--radius-lg);
    font-size: 0.925rem;
    line-height: 1.6;
    color: var(--text-primary);
}

.message-bubble.user {
    background-color: var(--accent-primary);
    color: var(--text-inverse);
    border-bottom-right-radius: 4px;
    margin-left: auto;
}

.message-bubble.ai {
    background-color: var(--bg-card);
    border: 1px solid var(--border);
    border-bottom-left-radius: 4px;
}

.citation {
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-top: 0.5rem;
    padding-top: 0.5rem;
    border-top: 1px solid var(--border);
}

.typing-indicator {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    padding: 1rem 1.25rem;
    background-color: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    border-bottom-left-radius: 4px;
    max-width: 120px;
}

.typing-dot {
    width: 6px;
    height: 6px;
    background-color: var(--text-muted);
    border-radius: 50%;
    animation: typing 1.4s ease-in-out infinite both;
}

.typing-dot:nth-child(1) { animation-delay: 0.2s; }
.typing-dot:nth-child(2) { animation-delay: 0.3s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

/* Skeleton loader */
.skeleton {
    background: linear-gradient(90deg, var(--bg-card) 25%, var(--bg-elevated) 50%, var(--bg-card) 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: var(--radius);
    height: 1rem;
}

.skeleton-title {
    height: 1.25rem;
    width: 60%;
}

.skeleton-text {
    height: 1rem;
    width: 100%;
    margin-top: 0.5rem;
}

.skeleton-text.short {
    width: 40%;
}

@keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

/* Quiz question card */
.quiz-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.75rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow);
    transition: all var(--transition-base);
}

.quiz-card:hover {
    border-color: var(--accent-primary);
}

.quiz-progress {
    height: 6px;
    background-color: var(--bg-input);
    border-radius: 9999px;
    overflow: hidden;
    margin-bottom: 1rem;
}

.quiz-progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
    border-radius: 9999px;
    transition: width var(--transition-base);
}

/* Radio options in quiz */
.stRadio > div[role="radiogroup"] > label {
    background-color: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    color: var(--text-secondary);
    font-weight: 500;
    font-size: 0.925rem;
    transition: all var(--transition-fast);
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.stRadio > div[role="radiogroup"] > label:hover {
    border-color: var(--accent-primary);
    background-color: var(--bg-elevated);
    color: var(--text-primary);
}

/* Selectbox */
.stSelectbox > div > div {
    border-radius: var(--radius);
    background-color: var(--bg-input);
}

/* Slider */
.stSlider > div[data-baseweb="slider"] > div {
    color: var(--accent-primary);
}

/* Textarea */
.stTextArea > div > div > textarea {
    background-color: var(--bg-input);
}

/* Responsive */
@media (max-width: 768px) {
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .login-wrapper {
        margin: 2rem auto;
    }
    .message-bubble {
        max-width: 85%;
    }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.user_role = "student"

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "quiz_current_index" not in st.session_state:
    st.session_state.quiz_current_index = 0
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------------------------------------------------------------------
# Login page (not logged in)
# ---------------------------------------------------------------------------
if not st.session_state.logged_in:
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)

    # Brand header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #8B5CF6, #38BDF8);
                    border-radius: 12px; display: inline-flex; align-items: center;
                    justify-content: center; margin-bottom: 1rem; font-weight: 800; color: #090D1A; font-size: 1.125rem;">
            CA
        </div>
        <h1 style="font-size: 2rem; margin: 0; color: #F8FAFC;">CampusAI</h1>
        <p style="color: #94A3B8; font-size: 0.95rem; margin-top: 0.5rem;">Your Academic Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)

    portal = st.radio(
        "Select Portal",
        ["Student Portal", "Admin Portal"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if portal == "Student Portal":
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="login-header">
            <h2>Student Sign In</h2>
            <p>Access your notes, quizzes, and academic assistant.</p>
        </div>
        """, unsafe_allow_html=True)

        email = st.text_input("Email Address", key="login_email", placeholder="name@college.edu")
        password = st.text_input("Password", type="password", key="login_pass", placeholder="••••••••")

        col_btn, col_link = st.columns([3, 1])
        with col_btn:
            if st.button("Sign In", key="btn_student_login", use_container_width=True):
                if email and password:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.session_state.user_role = "student"
                    st.rerun()
                else:
                    st.markdown('<div class="alert alert-error">Please enter your email and password.</div>', unsafe_allow_html=True)
        with col_link:
            st.write("")  # spacer

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="login-header">
            <h2>Admin Sign In</h2>
            <p>Manage official documents and the knowledge base.</p>
        </div>
        """, unsafe_allow_html=True)

        admin_key = st.text_input("Admin Security Key", type="password", key="admin_key", placeholder="••••••••")

        if st.button("Sign In as Admin", key="btn_admin_login", use_container_width=True):
            if admin_key == "admin123":
                st.session_state.logged_in = True
                st.session_state.user_email = "admin@campus.ai"
                st.session_state.user_role = "admin"
                st.rerun()
            elif admin_key:
                st.markdown('<div class="alert alert-error">Incorrect admin security key.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert alert-error">Please enter the admin security key.</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ---------------------------------------------------------------------------
# Initialize Gemini client (only after login)
# ---------------------------------------------------------------------------
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_with_retry(model, contents, max_retries=1):
    """Generate content with fallback models (library handles internal retries for 503)."""
    last_error = None
    models_to_try = [model] + [m for m in ["gemini-3.6-flash", "gemini-3.5-flash"] if m != model]

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents
            )
            if response and getattr(response, 'text', None):
                return response
        except Exception as e:
            last_error = e
            continue
    return None

# ---------------------------------------------------------------------------
# Sidebar navigation shell
# ---------------------------------------------------------------------------
st.sidebar.markdown("""
<div class="sidebar-brand">
    <div class="brand-mark">CA</div>
    <h1>CampusAI</h1>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"""
<div class="sidebar-user">
    <div class="user-name">{st.session_state.user_email}</div>
    <div class="user-role">{st.session_state.user_role.title()}</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

# Navigation based on role
if st.session_state.user_role == "admin":
    app_mode = st.sidebar.radio(
        "Navigation",
        ["Admin Workstation"],
        index=0,
        label_visibility="collapsed",
    )
else:
    app_mode = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "AI Notes Studio", "College Assistant", "Quiz Arena"],
        index=0,
        label_visibility="collapsed",
    )

st.sidebar.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

if st.sidebar.button("Sign Out", key="btn_logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.user_role = "student"
    st.session_state.quiz_data = None
    st.session_state.quiz_submitted = False
    st.session_state.quiz_current_index = 0
    st.session_state.quiz_answers = {}
    st.rerun()

# ---------------------------------------------------------------------------
# HOME DASHBOARD (Student)
# ---------------------------------------------------------------------------
if st.session_state.user_role == "student" and app_mode == "Dashboard":
    st.markdown('<div class="animate-fade-in stagger-1">', unsafe_allow_html=True)

    # Welcome hero
    today = datetime.datetime.now().strftime("%A, %B %d")
    st.markdown(f"""
    <div style="margin-bottom: 2.5rem;">
        <h1 style="font-size: 2rem; margin-bottom: 0.25rem;">Welcome back, {st.session_state.user_email.split('@')[0]}.</h1>
        <p style="color: #94A3B8; font-size: 0.95rem; margin: 0;">{today} &#8226; Level 1 &#8226; 0 XP</p>
    </div>
    """, unsafe_allow_html=True)

    # Statistics row
    st.markdown('<div class="feature-grid">', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="metric-card stagger-1">
            <p class="metric-label">Notes Created</p>
            <p class="metric-value">0</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card stagger-2">
            <p class="metric-label">Quizzes Completed</p>
            <p class="metric-value">0</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card stagger-3">
            <p class="metric-label">Average Score</p>
            <p class="metric-value">--%</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-card stagger-4">
            <p class="metric-label">Current XP</p>
            <p class="metric-value">0</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider-sm">', unsafe_allow_html=True)

    # Feature cards
    st.markdown('<h2 style="margin-bottom: 1.5rem;">Explore CampusAI</h2>', unsafe_allow_html=True)
    st.markdown('<div class="feature-grid">', unsafe_allow_html=True)

    with st.container():
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div class="premium-card stagger-1">
                <h3 style="color: #8B5CF6;">AI Notes Studio</h3>
                <p>Transform your study materials into simplified and exam-oriented notes using AI.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Notes Studio", key="btn_dash_notes", use_container_width=True):
                st.rerun()

        with col2:
            st.markdown("""
            <div class="premium-card stagger-2">
                <h3 style="color: #38BDF8;">College Assistant</h3>
                <p>Get accurate answers from official college documents with page citations.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open College Assistant", key="btn_dash_rag", use_container_width=True):
                st.rerun()

        with col3:
            st.markdown("""
            <div class="premium-card stagger-3">
                <h3 style="color: #A78BFA;">Quiz Arena</h3>
                <p>Test your knowledge with AI-generated quizzes and track your performance.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Enter Quiz Arena", key="btn_dash_quiz", use_container_width=True):
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# AI NOTES STUDIO (Student)
# ---------------------------------------------------------------------------
elif st.session_state.user_role == "student" and app_mode == "AI Notes Studio":
    st.markdown('<div class="animate-fade-in stagger-1">', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1>AI Notes Studio</h1>
        <p style="color: #94A3B8; font-size: 0.95rem;">Upload your study materials and generate AI-powered simplified and exam-oriented notes.</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload your study notes",
        type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        os.makedirs("storage/uploads/students", exist_ok=True)
        file_path = os.path.join("storage/uploads/students", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.markdown(f"""
        <div class="alert alert-success">
            <strong>Upload complete:</strong> {uploaded_file.name}
        </div>
        """, unsafe_allow_html=True)

        if st.button("Generate Notes", key="btn_generate_notes", use_container_width=True):
            with st.spinner("Analyzing your document with AI..."):
                from services.document_parser import parse_document

                parsed_pages = parse_document(file_path)
                full_text = "\n".join([p["text"] for p in parsed_pages])

                simp_response = generate_with_retry(
                    model="gemini-3.5-flash",
                    contents=f"Simplify these notes into clear, easy-to-understand bullet points for a student:\n\n{full_text}"
                )

                exam_response = generate_with_retry(
                    model="gemini-3.5-flash",
                    contents=f"Extract high-yield exam points, key definitions, and likely questions from these notes:\n\n{full_text}"
                )

                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
                    st.markdown("### Simplified Notes")
                    st.write(simp_response.text if simp_response else "Unable to generate simplified notes. Please try again.")
                    st.markdown('</div>', unsafe_allow_html=True)
                with col_b:
                    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
                    st.markdown("### Exam-Oriented Notes")
                    st.write(exam_response.text if exam_response else "Unable to generate exam notes. Please try again.")
                    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# COLLEGE ASSISTANT (Student)
# ---------------------------------------------------------------------------
elif st.session_state.user_role == "student" and app_mode == "College Assistant":
    st.markdown('<div class="animate-fade-in stagger-1">', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1>College Assistant</h1>
        <p style="color: #94A3B8; font-size: 0.95rem;">Ask questions about official college policies, timetables, and circulars with verified page citations.</p>
    </div>
    """, unsafe_allow_html=True)

    # Suggested questions
    st.markdown("### Suggested Questions")
    sugg_col1, sugg_col2, sugg_col3 = st.columns(3)
    with sugg_col1:
        if st.button("Academic calendar dates?", key="sugg_1", use_container_width=True):
            st.session_state.chat_history.append(("user", "What are the key dates in the academic calendar?"))
    with sugg_col2:
        if st.button("Exam schedule?", key="sugg_2", use_container_width=True):
            st.session_state.chat_history.append(("user", "When are the end semester examinations?"))
    with sugg_col3:
        if st.button("Holiday list?", key="sugg_3", use_container_width=True):
            st.session_state.chat_history.append(("user", "What are the declared institutional holidays?"))

    st.markdown('<hr class="divider-sm">', unsafe_allow_html=True)

    # Chat display
    st.markdown('<div class="message-container">', unsafe_allow_html=True)

    for role, content in st.session_state.chat_history:
        if role == "user":
            st.markdown(f"""
            <div class="message">
                <div class="message-avatar user">U</div>
                <div class="message-bubble user">{content}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="message">
                <div class="message-avatar ai">A</div>
                <div class="message-bubble ai">{content}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # User input
    user_query = st.text_input("Ask a question about official college rules:", key="rag_input", placeholder="Type your question here...")

    col_send, col_clear = st.columns([4, 1])
    with col_send:
        send_clicked = st.button("Send", key="btn_rag_send", use_container_width=True)
    with col_clear:
        clear_clicked = st.button("Clear", key="btn_rag_clear", use_container_width=True)

    if clear_clicked:
        st.session_state.chat_history = []
        st.rerun()

    if send_clicked and user_query.strip():
        st.session_state.chat_history.append(("user", user_query))

        # Show typing indicator
        typing_placeholder = st.empty()
        with typing_placeholder.container():
            st.markdown("""
            <div class="message">
                <div class="message-avatar ai">A</div>
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        from services.college_rag import query_college_assistant
        result = query_college_assistant(user_query)

        typing_placeholder.empty()

        ai_answer = result["answer"]
        citations = result.get("citations", [])

        # Build AI message with citations
        ai_html = ai_answer
        if citations:
            cites_html = "".join(f'<span class="badge badge-cyan" style="margin-right: 0.5rem;">{c}</span>' for c in citations)
            ai_html += f'<div class="citation">Sources: {cites_html}</div>'

        st.session_state.chat_history.append(("assistant", ai_html))
        st.rerun()

    elif send_clicked and not user_query.strip():
        st.markdown('<div class="alert alert-error">Please enter a question.</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# QUIZ ARENA (Student)
# ---------------------------------------------------------------------------
elif st.session_state.user_role == "student" and app_mode == "Quiz Arena":
    st.markdown('<div class="animate-fade-in stagger-1">', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1>Quiz Arena</h1>
        <p style="color: #94A3B8; font-size: 0.95rem;">Test your knowledge with AI-generated quizzes and track your academic performance.</p>
    </div>
    """, unsafe_allow_html=True)

    # Quiz setup (only if no active quiz)
    if st.session_state.quiz_data is None:
        st.markdown("### Create Quiz")

        quiz_topic = st.text_input("Topic or subject", key="quiz_topic", placeholder="e.g., Database Management Systems")
        quiz_type = st.selectbox(
            "Question Type",
            ["Multiple Choice (MCQ)", "True / False", "Descriptive & Short Answer"],
            key="quiz_type",
        )
        num_questions = st.slider("Number of Questions", min_value=3, max_value=10, value=5, key="quiz_num")

        if st.button("Generate Quiz", key="btn_generate_quiz", use_container_width=True):
            if not quiz_topic.strip():
                st.markdown('<div class="alert alert-error">Please enter a topic or notes first.</div>', unsafe_allow_html=True)
            else:
                with st.spinner("Generating your quiz with AI..."):
                    prompt = f"""
                    Generate a {num_questions}-question quiz on the topic: '{quiz_topic}'.
                    Quiz Format: {quiz_type}.
                    Return ONLY a valid JSON object matching this exact structure, with no extra markdown formatting or backticks around the JSON:
                    {{
                      "questions": [
                        {{
                          "id": 1,
                          "question": "Question text here?",
                          "options": ["Option A", "Option B", "Option C", "Option D"],
                          "correct_answer": "Exact correct answer or option text",
                          "explanation": "Why this answer is correct."
                        }}
                      ]
                    }}
                    """

                    response = generate_with_retry(
                        model="gemini-3.5-flash",
                        contents=prompt
                    )

                    if response is None:
                        st.markdown('<div class="alert alert-error">Failed to generate quiz due to high server demand. Please try again.</div>', unsafe_allow_html=True)
                    else:
                        try:
                            raw_text = response.text.replace("```json", "").replace("```", "").strip()
                            st.session_state.quiz_data = json.loads(raw_text)
                            st.session_state.quiz_submitted = False
                            st.session_state.quiz_current_index = 0
                            st.session_state.quiz_answers = {}
                            st.rerun()
                        except Exception as e:
                            st.markdown(f'<div class="alert alert-error">Failed to parse quiz format. Please try again.</div>', unsafe_allow_html=True)

    # Active quiz
    elif st.session_state.quiz_data and "questions" in st.session_state.quiz_data:
        questions = st.session_state.quiz_data["questions"]
        total = len(questions)
        current_idx = st.session_state.quiz_current_index
        current_q = questions[current_idx]

        # Progress
        progress_pct = int(((current_idx + 1) / total) * 100)
        st.markdown(f"""
        <div class="quiz-progress">
            <div class="quiz-progress-fill" style="width: {progress_pct}%;"></div>
        </div>
        <p style="color: #94A3B8; font-size: 0.875rem; margin-top: 0.5rem; text-align: right;">Question {current_idx + 1} of {total}</p>
        """, unsafe_allow_html=True)

        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        st.markdown(f"### Question {current_idx + 1}")
        st.markdown(f"#### {current_q['question']}")

        if "options" in current_q and current_q["options"]:
            user_ans = st.radio(
                "Select your answer:",
                current_q["options"],
                key=f"quiz_q_{current_q['id']}",
                label_visibility="collapsed",
            )
            st.session_state.quiz_answers[current_q["id"]] = user_ans
        else:
            user_ans = st.text_input(
                "Your answer:",
                key=f"quiz_q_{current_q['id']}",
                placeholder="Type your answer here...",
            )
            st.session_state.quiz_answers[current_q["id"]] = user_ans

        st.markdown('</div>', unsafe_allow_html=True)

        # Navigation
        col_prev, col_next = st.columns(2)
        with col_prev:
            if current_idx > 0:
                if st.button("Previous", key="btn_quiz_prev", use_container_width=True):
                    st.session_state.quiz_current_index -= 1
                    st.rerun()
            else:
                st.button("Previous", key="btn_quiz_prev_disabled", disabled=True, use_container_width=True)

        with col_next:
            if current_idx < total - 1:
                if st.button("Next Question", key="btn_quiz_next", use_container_width=True):
                    st.session_state.quiz_current_index += 1
                    st.rerun()
            else:
                if st.button("Submit Quiz", key="btn_quiz_submit_final", use_container_width=True):
                    st.session_state.quiz_submitted = True
                    st.rerun()

    # Quiz results
    if st.session_state.quiz_submitted and st.session_state.quiz_data:
        questions = st.session_state.quiz_data["questions"]
        total = len(questions)
        score = 0

        st.markdown("### Quiz Results")

        for q in questions:
            user_ans = st.session_state.quiz_answers.get(q["id"])
            correct_ans = q["correct_answer"]
            is_correct = str(user_ans).strip().lower() == str(correct_ans).strip().lower()
            if is_correct:
                score += 1

        percentage = (score / total) * 100

        col_score1, col_score2 = st.columns(2)
        with col_score1:
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-label">Final Score</p>
                <p class="metric-value">{score} / {total}</p>
            </div>
            """, unsafe_allow_html=True)
        with col_score2:
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-label">Percentage</p>
                <p class="metric-value">{percentage:.0f}%</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<hr class="divider-sm">', unsafe_allow_html=True)

        for q in questions:
            user_ans = st.session_state.quiz_answers.get(q["id"])
            correct_ans = q["correct_answer"]
            is_correct = str(user_ans).strip().lower() == str(correct_ans).strip().lower()

            status_color = "#34D399" if is_correct else "#FB7185"
            status_text = "Correct" if is_correct else "Incorrect"

            st.markdown(f"""
            <div class="premium-card" style="margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
                    <span class="badge {'badge-green' if is_correct else 'badge-rose'}">{status_text}</span>
                    <span style="font-size: 0.85rem; color: #94A3B8;">Question {q['id']}</span>
                </div>
                <p style="margin: 0 0 0.75rem 0; color: #F8FAFC;"><strong>{q['question']}</strong></p>
                <p style="margin: 0; color: #94A3B8; font-size: 0.9rem;"><strong>Your answer:</strong> {user_ans}</p>
                <p style="margin: 0.5rem 0 0 0; color: #94A3B8; font-size: 0.9rem;"><strong>Correct answer:</strong> {correct_ans}</p>
                <p style="margin: 0.5rem 0 0 0; color: #CBD5E1; font-size: 0.9rem;"><strong>Explanation:</strong> {q['explanation']}</p>
            </div>
            """, unsafe_allow_html=True)

        if percentage >= 80:
            st.markdown(f"""
            <div class="alert alert-success">
                Excellent work! You earned 50 XP.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="alert alert-warning">
                Keep practicing! Review your notes and try again to improve your score.
            </div>
            """, unsafe_allow_html=True)

        col_retry, col_new = st.columns(2)
        with col_retry:
            if st.button("Retry Quiz", key="btn_quiz_retry", use_container_width=True):
                st.session_state.quiz_submitted = False
                st.session_state.quiz_current_index = 0
                st.session_state.quiz_answers = {}
                st.rerun()
        with col_new:
            if st.button("Create New Quiz", key="btn_quiz_new", use_container_width=True):
                st.session_state.quiz_data = None
                st.session_state.quiz_submitted = False
                st.session_state.quiz_current_index = 0
                st.session_state.quiz_answers = {}
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# ADMIN WORKSTATION (Admin)
# ---------------------------------------------------------------------------
elif st.session_state.user_role == "admin" and app_mode == "Admin Workstation":
    st.markdown('<div class="animate-fade-in stagger-1">', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1>Admin Workstation</h1>
        <p style="color: #94A3B8; font-size: 0.95rem;">Manage official college documents and the knowledge base for the College Assistant.</p>
    </div>
    """, unsafe_allow_html=True)

    # Admin re-authentication
    admin_password = st.text_input("Admin Security Key", type="password", key="admin_workstation_key", placeholder="Enter admin key")

    if admin_password == "admin123":
        st.markdown('<div class="alert alert-success">Admin authenticated successfully.</div>', unsafe_allow_html=True)

        # Document listing
        db = SessionLocal()
        existing_docs = db.query(OfficialDoc).all()
        db.close()

        if existing_docs:
            st.markdown("### Indexed Documents")
            st.markdown('<hr class="divider-sm">', unsafe_allow_html=True)

            for doc in existing_docs:
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.markdown(f"""
                    <div class="premium-card" style="padding: 1rem; margin-bottom: 1rem;">
                        <p style="margin: 0; color: #F8FAFC; font-weight: 600;">{doc.title}</p>
                        <p style="margin: 0.25rem 0 0 0; color: #94A3B8; font-size: 0.85rem;">{doc.filename}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div style="padding: 1rem; margin-bottom: 1rem;">
                        <p style="margin: 0; color: #94A3B8; font-size: 0.85rem;">Uploaded: {doc.upload_date.strftime('%Y-%m-%d %H:%M')}</p>
                        <p style="margin: 0; color: #CBD5E1; font-size: 0.85rem;">Status: {doc.status}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    if st.button("Remove", key=f"btn_remove_{doc.id}", use_container_width=True):
                        try:
                            from services.college_rag import official_collection
                            official_collection.delete(where={"filename": doc.filename})
                            db = SessionLocal()
                            db.query(OfficialDoc).filter(OfficialDoc.id == doc.id).delete()
                            db.commit()
                            db.close()
                            st.rerun()
                        except Exception as e:
                            st.markdown(f'<div class="alert alert-error">Failed to remove document: {e}</div>', unsafe_allow_html=True)

        st.markdown('<hr class="divider-sm">', unsafe_allow_html=True)

        # Upload form
        st.markdown("### Upload Official Document")

        pdf_title = st.text_input("Document Title", key="admin_pdf_title", placeholder="e.g., Academic Calendar 2026-2027")
        admin_file = st.file_uploader("Upload Official PDF", type=["pdf"], key="admin_pdf_upload")

        if admin_file is not None and pdf_title:
            db_check = SessionLocal()
            existing = db_check.query(OfficialDoc).filter(OfficialDoc.filename == admin_file.name).first()
            db_check.close()

            if existing:
                st.markdown(f'<div class="alert alert-warning">Document "{admin_file.name}" is already indexed.</div>', unsafe_allow_html=True)
            else:
                os.makedirs("storage/uploads/official", exist_ok=True)
                official_path = os.path.join("storage/uploads/official", admin_file.name)
                with open(official_path, "wb") as f:
                    f.write(admin_file.getbuffer())

                st.markdown(f'<div class="alert alert-info">File saved: {admin_file.name}</div>', unsafe_allow_html=True)

                if st.button("Index Document", key="btn_index_doc", use_container_width=True):
                    with st.spinner("Parsing and indexing document..."):
                        try:
                            from services.college_rag import index_official_pdf
                            index_official_pdf(official_path, pdf_title)

                            db = SessionLocal()
                            new_doc = OfficialDoc(title=pdf_title, filename=admin_file.name, status="indexed")
                            db.add(new_doc)
                            db.commit()
                            db.close()

                            st.markdown('<div class="alert alert-success">Document successfully indexed!</div>', unsafe_allow_html=True)
                            st.rerun()
                        except Exception as e:
                            st.markdown(f'<div class="alert alert-error">Failed to index document: {e}</div>', unsafe_allow_html=True)
    elif admin_password:
        st.markdown('<div class="alert alert-error">Incorrect admin security key.</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
