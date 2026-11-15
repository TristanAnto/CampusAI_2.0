import os
import sys

# Force Python to look in the directory where app.py lives for local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import json
import streamlit as st
from dotenv import load_dotenv
from google import genai
from database import SessionLocal
from models import OfficialDoc



# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="CampusAI 2.0",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS - Modern Indigo/Slate theme
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --primary: #3730A3;
    --primary-hover: #312E81;
    --primary-light: #EDE9FE;
    --secondary: #4338CA;
    --accent: #0EA5E9;
    --bg: #F8FAFC;
    --surface: #FFFFFF;
    --surface-hover: #F1F5F9;
    --text: #0F172A;
    --text-muted: #64748B;
    --border: #E2E8F0;
    --success: #10B981;
    --success-bg: #ECFDF5;
    --error: #EF4444;
    --error-bg: #FEF2F2;
    --warning: #F59E0B;
    --warning-bg: #FFFBEB;
    --radius: 12px;
    --shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
    --shadow-hover: 0 8px 30px rgba(0, 0, 0, 0.10);
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

.stApp {
    background-color: var(--bg);
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Typography */
h1, h2, h3, h4, h5, h6 {
    color: var(--text);
    font-weight: 700;
    letter-spacing: -0.02em;
    font-family: 'Inter', sans-serif;
}

h1 {
    font-size: 2.75rem;
    margin-bottom: 0.5rem;
    line-height: 1.1;
}

h2 {
    font-size: 1.875rem;
    margin-bottom: 0.75rem;
}

h3 {
    font-size: 1.375rem;
    margin-bottom: 0.5rem;
}

p, .stMarkdown, .stText {
    color: var(--text);
    line-height: 1.6;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: var(--surface);
    border-right: 1px solid var(--border);
}

section[data-testid="stSidebar"] .stRadio > div,
section[data-testid="stSidebar"] .stSelectbox > div {
    background-color: transparent;
}

section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stRadio label {
    color: var(--text);
    font-weight: 600;
}

/* Main content padding */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

/* Buttons - Primary */
.stButton > button {
    background-color: var(--primary);
    color: var(--surface);
    border: none;
    border-radius: var(--radius);
    padding: 0.875rem 1.75rem;
    font-weight: 600;
    font-size: 0.95rem;
    transition: all 0.2s ease;
    width: 100%;
    box-shadow: 0 2px 8px rgba(55, 48, 163, 0.15);
}

.stButton > button:hover {
    background-color: var(--primary-hover);
    transform: translateY(-1px);
    box-shadow: var(--shadow-hover);
}

/* Buttons - Secondary (outline) */
.stButton button[kind="secondary"] {
    background-color: var(--surface);
    color: var(--primary);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 0.875rem 1.75rem;
    font-weight: 600;
    font-size: 0.95rem;
    transition: all 0.2s ease;
    width: 100%;
}

.stButton button[kind="secondary"]:hover {
    background-color: var(--primary-light);
    border-color: var(--primary);
}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    background-color: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--text);
    font-size: 0.95rem;
    padding: 0.75rem 1rem;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div > div:focus {
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(55, 48, 163, 0.1);
}

/* File uploader */
.stFileUploader {
    border: 2px dashed var(--border);
    border-radius: var(--radius);
    padding: 2.5rem;
    text-align: center;
    background-color: var(--surface);
    transition: all 0.2s ease;
}

.stFileUploader:hover {
    border-color: var(--primary);
    background-color: var(--primary-light);
}

/* Cards */
.stContainer, .stMarkdown > div {
    background-color: var(--surface);
    border-radius: var(--radius);
    padding: 1.75rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
}

/* Metrics */
.stMetric {
    background-color: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem;
    box-shadow: var(--shadow);
}

.stMetric [data-testid="stMetricValue"] {
    color: var(--primary);
    font-weight: 700;
    font-size: 1.75rem;
}

.stMetric [data-testid="stMetricLabel"] {
    color: var(--text-muted);
    font-weight: 500;
    font-size: 0.875rem;
}

/* Alerts */
.stAlert {
    border-radius: var(--radius);
    border: none;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
}

.stSuccess {
    background-color: var(--success-bg);
    color: var(--success);
    border-left: 4px solid var(--success);
}

.stError {
    background-color: var(--error-bg);
    color: var(--error);
    border-left: 4px solid var(--error);
}

.stWarning {
    background-color: var(--warning-bg);
    color: var(--warning);
    border-left: 4px solid var(--warning);
}

.stInfo {
    background-color: var(--primary-light);
    color: var(--primary);
    border-left: 4px solid var(--primary);
}

/* Divider */
hr {
    border: none;
    height: 1px;
    background-color: var(--border);
    margin: 2.5rem 0;
}

/* Animations */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(25px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.animate-fade-in {
    animation: fadeInUp 0.7s ease-out forwards;
}

/* Login page center */
.login-container {
    max-width: 440px;
    margin: 4rem auto;
    padding: 3rem;
    background: var(--surface);
    border-radius: 16px;
    border: 1px solid var(--border);
    box-shadow: var(--shadow-hover);
}

.admin-login-container {
    max-width: 440px;
    margin: 4rem auto;
    padding: 3rem;
    background: var(--surface);
    border-radius: 16px;
    border: 1px solid var(--border);
    box-shadow: var(--shadow-hover);
}

/* Feature cards on dashboard */
.feature-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 2rem;
    height: 220px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
    transition: all 0.3s ease;
    cursor: pointer;
}

.feature-card:hover {
    border-color: var(--primary);
    transform: translateY(-4px);
    box-shadow: var(--shadow-hover);
}

.feature-card h3 {
    margin-bottom: 0.5rem;
    font-size: 1.25rem;
}

.feature-card p {
    color: var(--text-muted);
    font-size: 0.95rem;
    margin: 0;
}

/* Radio button styling */
.stRadio > div[role="radiogroup"] > label {
    background-color: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    transition: all 0.2s ease;
}

.stRadio > div[role="radiogroup"] > label:hover {
    border-color: var(--primary);
    background-color: var(--primary-light);
}

/* Selectbox focus */
.stSelectbox > div > div {
    border-radius: var(--radius);
}

/* Slider styling */
.stSlider > div[data-baseweb="slider"] > div {
    color: var(--primary);
}
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.user_role = "student"

if not st.session_state.logged_in:
    st.markdown('<div class="animate-fade-in">', unsafe_allow_html=True)
    st.title("CampusAI 2.0")
    st.markdown("---")

    portal = st.radio(
        "Select Portal",
        ["Student Portal", "Admin Portal"],
        horizontal=True
    )

    if portal == "Student Portal":
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown("### Student Login")
        email = st.text_input("Email Address", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login as Student", use_container_width=True):
            if email and password:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.user_role = "student"
                st.success("Logged in successfully as student!")
                st.rerun()
            else:
                st.warning("Please enter your email and password.")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="admin-login-container">', unsafe_allow_html=True)
        st.markdown("### Admin Login")
        admin_key = st.text_input("Admin Security Key", type="password", key="admin_key")
        if st.button("Login as Admin", use_container_width=True):
            if admin_key == "admin123":
                st.session_state.logged_in = True
                st.session_state.user_email = "admin@campus.ai"
                st.session_state.user_role = "admin"
                st.success("Logged in successfully as admin!")
                st.rerun()
            elif admin_key:
                st.error("Incorrect admin key. Hint for local dev: use admin123")
            else:
                st.warning("Please enter the admin security key.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()  # Stops the rest of the app from loading until logged in

# Initialize Gemini Client
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

# Sidebar Navigation - Workspace Selection (role-based)
st.sidebar.title("CampusAI Navigation")
st.sidebar.caption(f"Logged in as: {st.session_state.user_email} ({st.session_state.user_role})")

if st.session_state.user_role == "admin":
    workspace = "Admin Workstation"
    st.sidebar.radio("Workspace", ["Admin Workstation"], index=0, disabled=True)
    app_mode = "Admin Portal"
else:
    workspace = "Student Area"
    st.sidebar.radio("Workspace", ["Student Area"], index=0, disabled=True)
    app_mode = st.sidebar.selectbox(
        "Student Module",
        ["Home Dashboard", "AI Notes Studio", "College Assistant", "Quiz Arena"]
    )

st.sidebar.divider()
if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.user_role = "student"
    st.rerun()

# ----------------------------------------------------
# HOME DASHBOARD
# ----------------------------------------------------
if app_mode == "Home Dashboard":
    st.markdown('<div class="animate-fade-in">', unsafe_allow_html=True)
    st.title("CampusAI 2.0")
    st.subheader("Your College. Your Notes. Your AI Learning Companion.")

    st.write(
        "Welcome to your personal AI-powered academic platform. Choose a module from the sidebar or below to get started."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### AI Notes Studio")
        st.write("Upload notes, simplify concepts and prepare for exams.")
        if st.button("Open Notes Studio", key="open_notes", use_container_width=True):
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### Quiz Arena")
        st.write("Challenge yourself with AI-generated quizzes.")
        if st.button("Enter Quiz Arena", key="enter_quiz", use_container_width=True):
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    st.markdown("### College Assistant")
    st.write("Get verified answers straight from official college circulars and PDFs.")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# AI NOTES STUDIO (Student Module)
# ----------------------------------------------------
elif app_mode == "AI Notes Studio":
    st.markdown('<div class="animate-fade-in">', unsafe_allow_html=True)
    st.title("AI Notes Studio")
    st.write("Upload your typed or handwritten study materials (PDF, DOCX, TXT, PNG, JPG) to generate simplified summaries and exam-oriented notes.")

    uploaded_file = st.file_uploader("Upload your study notes", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])

    if uploaded_file is not None:
        # Save uploaded file temporarily
        os.makedirs("storage/uploads/students", exist_ok=True)
        file_path = os.path.join("storage/uploads/students", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"Successfully uploaded: {uploaded_file.name}")

        if st.button("Generate Simplified & Exam Notes", key="generate_notes"):
            with st.spinner("Analyzing notes with Gemini..."):
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
                    st.markdown("### Simplified Notes")
                    st.write(simp_response.text if simp_response else "Unable to generate simplified notes. Please try again.")
                with col_b:
                    st.markdown("### Exam-Oriented Notes")
                    st.write(exam_response.text if exam_response else "Unable to generate exam notes. Please try again.")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# COLLEGE ASSISTANT (RAG Module)
# ----------------------------------------------------
elif app_mode == "College Assistant":
    st.markdown('<div class="animate-fade-in">', unsafe_allow_html=True)
    st.title("College Assistant")
    st.write("Ask questions about official college policies, timetables, and circulars with exact page citations.")

    user_query = st.text_input("Ask a question about official college rules:")

    if user_query:
        with st.spinner("Searching official college documents..."):
            from services.college_rag import query_college_assistant
            result = query_college_assistant(user_query)

            st.markdown("### Answer")
            st.write(result["answer"])

            if result["citations"]:
                st.markdown("### Verified Citations")
                for cite in result["citations"]:
                    st.caption(cite)
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# QUIZ ARENA
# ----------------------------------------------------
elif app_mode == "Quiz Arena":
    st.markdown('<div class="animate-fade-in">', unsafe_allow_html=True)
    st.title("Quiz Arena")
    st.write("Test your knowledge with AI-generated quizzes, earn XP, and track your performance!")

    # Initialize session state for quiz
    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data = None
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False

    quiz_topic = st.text_input("Enter a topic, subject, or paste study notes for your quiz:")
    quiz_type = st.selectbox("Select Question Types", ["Multiple Choice (MCQ)", "True / False", "Descriptive & Short Answer"])
    num_questions = st.slider("Number of Questions", min_value=3, max_value=10, value=5)

    if st.button("Generate AI Quiz", key="generate_quiz"):
        if not quiz_topic.strip():
            st.warning("Please enter a topic or notes first!")
        else:
            with st.spinner("Generating your custom quiz with Gemini..."):
                prompt = f"""
                Generate a {num_questions}-question quiz on the topic: '{quiz_topic}'.
                Quiz Format: {quiz_type}.
                Return ONLY a valid JSON object matching this exact structure, with no extra markdown formatting or backticks around the JSON:
                {{
                  "questions": [
                    {{
                      "id": 1,
                      "question": "Question text here?",
                      "options": ["Option A", "Option B", "Option C", "Option D"],  # Omit or leave empty if True/False or Descriptive
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
                    st.error("Failed to generate quiz due to high server demand. Please try again in a moment.")
                else:
                    try:
                        # Clean response text in case markdown blocks were included
                        raw_text = response.text.replace("```json", "").replace("```", "").strip()
                        st.session_state.quiz_data = json.loads(raw_text)
                        st.session_state.quiz_submitted = False
                        st.success("Quiz generated successfully! Scroll down to play.")
                    except Exception as e:
                        st.error(f"Failed to parse quiz format. Please try generating again. Details: {e}")

    # Render Active Quiz if available
    if st.session_state.quiz_data and "questions" in st.session_state.quiz_data:
        st.divider()
        st.markdown("### Answer the Questions")
        
        user_answers = {}
        for idx, q in enumerate(st.session_state.quiz_data["questions"]):
            st.markdown(f"**Question {idx+1}: {q['question']}**")
            
            if "options" in q and q["options"]:
                user_answers[q["id"]] = st.radio(
                    f"Select your answer for Question {idx+1}:", 
                    q["options"], 
                    key=f"q_{q['id']}"
                )
            else:
                user_answers[q["id"]] = st.text_input(f"Your answer for Question {idx+1}:", key=f"q_{q['id']}")
            
            st.write("")

        if not st.session_state.quiz_submitted:
            if st.button("Submit Quiz & Get Feedback", key="submit_quiz"):
                st.session_state.quiz_submitted = True
                score = 0
                total = len(st.session_state.quiz_data["questions"])

                st.divider()
                st.markdown("### Quiz Results & Feedback")

                for q in st.session_state.quiz_data["questions"]:
                    user_ans = user_answers.get(q["id"])
                    correct_ans = q["correct_answer"]
                    
                    is_correct = str(user_ans).strip().lower() == str(correct_ans).strip().lower()
                    if is_correct:
                        score += 1
                        st.success(f"Question {q['id']}: Correct!")
                    else:
                        st.error(f"Question {q['id']}: Incorrect. Your answer: *{user_ans}* | Correct answer: *{correct_ans}*")
                    
                    st.info(f"Explanation: {q['explanation']}")
                
                percentage = (score / total) * 100
                st.metric(label="Final Score", value=f"{score}/{total} ({percentage:.0f}%)")
                
                if percentage >= 80:
                    st.success("Awesome job! You earned 50 XP.")
                else:
                    st.warning("Keep practicing! Review your notes and try again to improve your score.")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# ADMIN PORTAL (Official Document Management)
# ----------------------------------------------------
elif app_mode == "Admin Portal":
    st.markdown('<div class="animate-fade-in">', unsafe_allow_html=True)
    st.title("Admin Portal")
    st.write("Upload official college PDFs, circulars, and timetables to index them into ChromaDB for the College Assistant.")

    admin_password = st.text_input("Admin Security Key", type="password")

    if admin_password == "admin123":
        st.success("Admin authenticated successfully.")

        # Show existing indexed documents
        db = SessionLocal()
        existing_docs = db.query(OfficialDoc).all()
        db.close()

        if existing_docs:
            st.markdown("### Indexed Documents")
            for doc in existing_docs:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{doc.title}** ({doc.filename})")
                    st.caption(f"Uploaded: {doc.upload_date.strftime('%Y-%m-%d %H:%M')} | Status: {doc.status}")
                with col2:
                    if st.button(f"Remove", key=f"remove_{doc.id}"):
                        try:
                            from services.college_rag import official_collection
                            official_collection.delete(where={"filename": doc.filename})
                            db = SessionLocal()
                            db.query(OfficialDoc).filter(OfficialDoc.id == doc.id).delete()
                            db.commit()
                            db.close()
                            st.success(f"Removed '{doc.title}'")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to remove document: {e}")
            st.divider()

        pdf_title = st.text_input("Document Title (e.g., Academic Calendar 2026-2027)")
        admin_file = st.file_uploader("Upload Official PDF", type=["pdf"])

        if admin_file is not None and pdf_title:
            # Check for duplicate filename
            db_check = SessionLocal()
            existing = db_check.query(OfficialDoc).filter(OfficialDoc.filename == admin_file.name).first()
            db_check.close()
            if existing:
                st.warning(f"Document '{admin_file.name}' is already indexed.")
            else:
                os.makedirs("storage/uploads/official", exist_ok=True)
                official_path = os.path.join("storage/uploads/official", admin_file.name)
                with open(official_path, "wb") as f:
                    f.write(admin_file.getbuffer())

                st.info(f"File saved: {admin_file.name}")

                if st.button("Index Document into College RAG", key="index_doc"):
                    with st.spinner("Parsing and indexing document into ChromaDB..."):
                        try:
                            from services.college_rag import index_official_pdf
                            index_official_pdf(official_path, pdf_title)

                            db = SessionLocal()
                            new_doc = OfficialDoc(title=pdf_title, filename=admin_file.name, status="indexed")
                            db.add(new_doc)
                            db.commit()
                            db.close()

                            st.success(f"Successfully indexed '{pdf_title}'! Students can now query this document in the College Assistant.")
                        except Exception as e:
                            st.error(f"Failed to index document: {e}")
    elif admin_password:
        st.error("Incorrect admin key. Hint for local dev: use admin123")
    st.markdown('</div>', unsafe_allow_html=True)