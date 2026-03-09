from google import genai
API_KEY =st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)
