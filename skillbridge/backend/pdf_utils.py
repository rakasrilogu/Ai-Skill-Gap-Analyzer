import fitz  # PyMuPDF


def extract_text_from_bytes(pdf_bytes: bytes) -> str:
    text = ""
    try:
        pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page in pdf:
            text += page.get_text()
    except Exception as e:
        raise ValueError(f"Failed to extract PDF text: {e}")
    return text
