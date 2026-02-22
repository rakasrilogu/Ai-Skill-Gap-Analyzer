import streamlit as st
from google import genai
import fitz  # PyMuPDF
import json

# --- CONFIGURATION ---
st.set_page_config(page_title="SkillBridge Pro AI", page_icon="🎯", layout="wide")

# API Setup
# Replace with your actual API Key
API_KEY = "Api key"
client = genai.Client(api_key=API_KEY)

# --- GLOBAL CUSTOM CSS ---
st.markdown("""
    <style>
    /* Global Dark Theme */
    .stApp { background: #0f172a; color: #ffffff !important; }
    h1, h2, h3, p, label, span, .stMarkdown { color: #ffffff !important; font-weight: 500; }
    
    /* SIDEBAR STYLING */
    [data-testid="stSidebar"] h1 { color: #a78bfa !important; font-size: 24px !important; }
    section[data-testid="stSidebar"] { background-color: #1e293b !important; }

    /* PAGE 1 ONLY: White Background for File Uploader */
    .white-upload-container [data-testid="stFileUploadDropzone"] {
        background-color: #ffffff !important;
        border: 2px dashed #7c3aed !important;
        border-radius: 12px;
    }
    .white-upload-container [data-testid="stFileUploadDropzone"] div div { color: #4c1d95 !important; font-weight: bold !important; }
    .white-upload-container [data-testid="stFileUploadDropzone"] button p { color: #000000 !important; }
    .white-upload-container [data-testid="stFileUploadDropzone"] small { color: #4b5563 !important; }

    /* CARD STYLING */
    .skill-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(124, 58, 237, 0.3);
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 20px;
    }

    /* BUTTONS */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #4f46e5, #7c3aed) !important;
        color: white !important;
        border-radius: 10px !important;
        height: 3.5em;
        border: none !important;
        font-weight: bold;
        font-size: 16px;
    }

    /* DOWNLOAD BUTTON FIX (Violet/White contrast) */
    .stDownloadButton button {
        background: #ffffff !important;
        color: #7c3aed !important;
        border: 2px solid #7c3aed !important;
        font-weight: bold !important;
        width: auto !important;
        padding: 0px 30px !important;
    }

    /* EXPANDER STYLING (Dark with Violet Glow) */
    .streamlit-expanderHeader {
        background-color: rgba(124, 58, 237, 0.1) !important;
        color: white !important;
        border-radius: 8px;
        border: 1px solid rgba(124, 58, 237, 0.2);
    }
    
    /* LINK COLORING */
    a { color: #38bdf8 !important; text-decoration: underline !important; }
    </style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def extract_text_from_pdf(uploaded_file):
    if uploaded_file:
        try:
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            return "".join([page.get_text() for page in doc])
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
    return ""

# --- NAVIGATION SIDEBAR ---
with st.sidebar:
    st.title("🚀 SkillBridge AI")
    st.markdown("---")
    page = st.radio(
        "NAVIGATION MENU", 
        ["1. Dashboard Home", "2. Skill Analysis", "3. Export Strategy"],
        captions=["Upload Profile", "View Insights", "Download Roadmap"]
    )

# Session state initialization
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None

# --- PAGE 1: DASHBOARD HOME ---
if page == "1. Dashboard Home":
    st.title("🎯 Analysis Center")
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown('<div class="skill-card">', unsafe_allow_html=True)
        st.subheader("📁 Profile Upload")
        # Apply white background class here
        st.markdown('<div class="white-upload-container">', unsafe_allow_html=True)
        res_file = st.file_uploader("Upload Resume (PDF ONLY)")
        st.markdown('</div>', unsafe_allow_html=True)
        skills_input = st.text_area("Manual Skills Entry:", height=100, placeholder="e.g. Python, SQL, Docker...")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="skill-card">', unsafe_allow_html=True)
        st.subheader("💼 Job Details")
        job_input = st.text_area("Paste Job Description:", height=275, placeholder="Paste the full job requirements...")
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("EXECUTE AI ANALYSIS"):
        if not job_input:
            st.error("Please provide a Job Description.")
        else:
            with st.spinner("Gemini 2.5 is building your roadmap..."):
                resume_text = extract_text_from_pdf(res_file)
                profile_context = f"Resume: {resume_text} | Additional Skills: {skills_input}"
                
                # Strict prompt for JSON and Clickable Markdown Links
                prompt = f"""
                Compare Profile: {profile_context} vs Job: {job_input}. 
                Return ONLY valid JSON: 
                {{
                  "score": 0-100, 
                  "matched": ["list"], 
                  "missing": ["list"], 
                  "roadmap": {{
                    "Week 1": "Master [Skill] with [Course Name](URL)", 
                    "Week 2": "Learn [Skill] with [Course Name](URL)", 
                    "Week 3": "Practice [Skill] with [Course Name](URL)", 
                    "Week 4": "Certify in [Skill] with [Course Name](URL)"
                  }}
                }}
                CRITICAL: You MUST provide real, clickable Markdown links for every week in the roadmap.
                """
                
                try:
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                    raw_json = response.text.replace("```json", "").replace("```", "").strip()
                    st.session_state.analysis_data = json.loads(raw_json)
                    st.success("Analysis Complete! Open 'Skill Analysis' to view.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Analysis Failed. Ensure your API key is active.")

# --- PAGE 2: SKILL ANALYSIS ---
elif page == "2. Skill Analysis":
    st.title("🧠 Skill Intelligence")
    if st.session_state.analysis_data:
        data = st.session_state.analysis_data
        st.metric("Compatibility Score", f"{data['score']}%")
        
        c1, c2 = st.columns(2)
        with c1:
            st.success("✅ Matched Competencies")
            for s in data['matched']: st.write(f"- {s}")
        with c2:
            st.warning("🚨 Identified Skill Gaps")
            for s in data['missing']: st.write(f"- {s}")
    else:
        st.info("⚠️ No analysis data found. Please run the analysis on the Home page.")

# --- PAGE 3: EXPORT STRATEGY ---
elif page == "3. Export Strategy":
    st.title("📥 Career Strategy & Roadmap")
    if st.session_state.analysis_data:
        data = st.session_state.analysis_data
        
        # Roadmap with Expanders
        st.subheader("📅 Your 4-Week Learning Roadmap")
        for wk, plan in data['roadmap'].items():
            with st.expander(f"📖 {wk.upper()}"):
                st.markdown(plan) # Clickable links show up here
        
        st.divider()
        
        # Save Report Section
        st.subheader("💾 Save Your Strategy")
        st.markdown('<div class="skill-card">', unsafe_allow_html=True)
        st.write("Generate a text version of your gaps and learning path.")
        
        report_txt = f"SKILLBRIDGE CAREER REPORT\nScore: {data['score']}%\n\n"
        report_txt += "MISSING SKILLS:\n" + ", ".join(data['missing']) + "\n\n"
        report_txt += "ROADMAP:\n"
        for wk, plan in data['roadmap'].items():
            report_txt += f"{wk}: {plan}\n"

        st.download_button(
            label="📥 DOWNLOAD REPORT (TXT)",
            data=report_txt,
            file_name="SkillBridge_Strategy.txt",
            mime="text/plain"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("⚠️ Please complete the analysis on Page 1 to generate your roadmap.")
