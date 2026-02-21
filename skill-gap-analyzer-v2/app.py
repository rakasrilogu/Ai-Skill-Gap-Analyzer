import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
from streamlit_lottie import st_lottie
from pypdf import PdfReader

# -------------------------------
# 1. Sidebar Controls (Theme Toggle)
# -------------------------------
st.sidebar.title("App Settings")
dark_mode = st.sidebar.toggle("🌙 Dark Mode")

# -------------------------------
# 2. Page Config & Dynamic Theme CSS
# -------------------------------
st.set_page_config(page_title="Skill Gap Analyzer v2", layout="wide")

# Theme Variables
bg_opacity = "0.8" if dark_mode else "0.75"
glass_color = "rgba(15, 15, 15, " + bg_opacity + ")" if dark_mode else "rgba(255, 255, 255, " + bg_opacity + ")"
text_color = "#FFFFFF" if dark_mode else "#000000"
border_color = "rgba(255, 255, 255, 0.1)" if dark_mode else "rgba(255, 255, 255, 0.4)"

st.markdown(f"""
<style>
/* HIDE RUNNING STATUS */
[data-testid="stStatusWidget"], .stStatusWidget, div[data-testid="stStatusWidget"] {{
    visibility: hidden !important;
    display: none !important;
}}

/* CLEAN HEADER */
[data-testid="stHeader"] {{ background: rgba(0,0,0,0) !important; }}
[data-testid="stToolbar"] {{ visibility: hidden !important; }}

/* DYNAMIC BACKGROUND */
[data-testid="stAppViewContainer"] {{
    background: url("http://googleusercontent.com/image_collection/image_retrieval/6490322677960104988_0");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

/* DYNAMIC GLASS CONTAINER */
.main .block-container {{
    background: {glass_color}; 
    backdrop-filter: blur(40px);
    -webkit-backdrop-filter: blur(40px);
    border-radius: 30px;
    padding: 5rem;
    margin-top: 2rem;
    border: 1px solid {border_color};
    box-shadow: 0 15px 35px 0 rgba(0, 0, 0, 0.6);
}}

/* DYNAMIC TEXT COLOR */
h1, h2, h3, p, span, label, li, .stMarkdown, .stTable td, .stTable th, [data-testid="stMetricLabel"] {{
    color: {text_color} !important;
    font-weight: 600 !important;
}}

/* BUTTON STYLING */
.stButton>button {{
    background: #00ffd5;
    color: #000000 !important;
    font-weight: bold;
    border-radius: 12px;
    border: none;
    width: 100%;
    padding: 15px;
    transition: 0.3s;
}}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 3. Database & Logic
# -------------------------------
RESOURCES = {
    "java": "https://docs.oracle.com/en/java/",
    "spring boot": "https://spring.io/projects/spring-boot",
    "rest api": "https://restfulapi.net/",
    "sql": "https://www.w3schools.com/sql/",
    "python": "https://docs.python.org/3/",
    "machine learning": "https://www.coursera.org/learn/machine-learning",
    "aws": "https://aws.amazon.com/training/",
    "docker": "https://docs.docker.com/get-started/"
}

job_database = {
    "Backend Developer": {"core": ["java", "spring boot", "rest api", "sql"], "secondary": ["docker", "aws"]},
    "Data Scientist": {"core": ["python", "machine learning", "statistics"], "secondary": ["pandas", "numpy"]},
    "Cloud Engineer": {"core": ["aws", "ec2", "s3"], "secondary": ["docker", "devops"]}
}

@st.cache_data
def load_lottie(url):
    try: return requests.get(url).json()
    except: return None

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return " ".join([page.extract_text() for page in reader.pages]).lower()

def create_pdf(score, job, missing_skills):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(190, 10, txt="Skill Gap Analysis Report", ln=True, align='C')
    pdf.set_font("Helvetica", size=12)
    pdf.ln(10)
    pdf.cell(190, 10, txt=f"Target Role: {job} | Readiness: {score}%", ln=True)
    pdf.ln(10)
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(190, 10, txt="Priority Roadmap:", ln=True)
    pdf.set_font("Helvetica", size=10)
    for skill in missing_skills:
        link = RESOURCES.get(skill.lower(), "Search for tutorials online")
        pdf.multi_cell(190, 8, txt=f"- {skill.upper()}: {link}")
    return bytes(pdf.output(dest='S'))
lottie_ani = load_lottie("https://assets2.lottiefiles.com/packages/lf20_p8bfn5to.json")

# -------------------------------
# 4. Navigation
# -------------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Dashboard", "Skill Analysis", "Roadmap"])

# -------------------------------
# 5. Dashboard (Centered)
# -------------------------------
if page == "Dashboard":
    _, center_col, _ = st.columns([1, 6, 1])
    with center_col:
        st.markdown("<h1 style='text-align: center; font-size: 3rem;'>🧠 AI Skill Analyzer</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Bridge the gap between your resume and your dream job.</h3>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if lottie_ani:
                st_lottie(lottie_ani, height=250, key="dash")
            if st.button("🚀 Start Analysis"):
                st.info("👈 Use the sidebar to go to 'Skill Analysis'!")

# -------------------------------
# 6. Analysis
# -------------------------------
elif page == "Skill Analysis":
    st.title("🔍 Gap Analysis")
    role = st.selectbox("Target Job Role", list(job_database.keys()))
    
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
    user_input = st.text_area("Or enter skills manually", "")

    if st.button("Analyze My Skills"):
        resume_text = extract_text_from_pdf(uploaded_file) if uploaded_file else ""
        full_text = resume_text + " " + user_input.lower()
        
        db = job_database[role]
        m_core = [s for s in db["core"] if s not in full_text]
        m_sec = [s for s in db["secondary"] if s not in full_text]
        
        found_core = len(db["core"]) - len(m_core)
        score = int((found_core / len(db["core"])) * 100)
        
        st.session_state['m_core'], st.session_state['m_sec'] = m_core, m_sec
        
        st.markdown(f"### Skill Match: {score}%")
        st.progress(score / 100)
        
        st.table(pd.DataFrame({
            "Priority": ["🔴 Missing Core", "🟡 Missing Secondary"],
            "Skills": [", ".join(m_core).upper() if m_core else "✓ Complete", 
                       ", ".join(m_sec).upper() if m_sec else "✓ Complete"]
        }))
        
        pdf = create_pdf(score, role, m_core + m_sec)
        st.download_button("📥 Download Report", pdf, "Gap_Analysis.pdf", "application/pdf")

# -------------------------------
# 7. Roadmap
# -------------------------------
elif page == "Roadmap":
    st.title("📅 Learning Roadmap")
    m_core = st.session_state.get('m_core', [])
    m_sec = st.session_state.get('m_sec', [])
    
    if not (m_core or m_sec) and 'm_core' not in st.session_state:
        st.warning("Please run the analysis first!")
    elif not m_core and not m_sec:
        st.success("You're fully ready! Keep polishing your projects.")
    else:
        for i, skill in enumerate(m_core + m_sec):
            with st.expander(f"WEEK {i+1}: Master {skill.upper()}"):

                st.write(f"Resource: [Access Here]({RESOURCES.get(skill.lower(), '#')})")
