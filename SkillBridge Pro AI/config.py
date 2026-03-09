from google import genai
import os

def get_client():
    try:
        import streamlit as st
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = os.environ.get("GEMINI_API_KEY", "")
    return genai.Client(api_key=api_key)

# ── Backwards compatible: keep `client` working for existing imports ─────────
client = None  # will be initialised on first use

def _get_or_init():
    global client
    if client is None:
        client = get_client()
    return client

# Proxy so existing code like `client.models.generate_content(...)` still works
class _ClientProxy:
    def __getattr__(self, name):
        return getattr(_get_or_init(), name)

client = _ClientProxy()
