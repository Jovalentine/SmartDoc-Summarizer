import os
import streamlit as st
from transformers import pipeline
from PyPDF2 import PdfReader
from docx import Document
import base64
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(r"G:\SmartDoc Summarize\Assets\ai-document-summerize-firebase-adminsdk-fbsvc-4db17133d2.json")
    firebase_admin.initialize_app(cred)

# Firestore database reference
db = firestore.client()

# Load the pre-trained BART summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Function to extract text from files
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def summarize_text(text, min_length=50, max_length=150):
    if not text.strip():
        return "No text found in the document to summarize."
    
    try:
        summary = summarizer(text, min_length=min_length, max_length=max_length, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return f"Error during summarization: {str(e)}"

def save_summary_to_firestore(user_email, file_name, summary):
    """Save summary to Firebase under user's email."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.collection("users").document(user_email).collection("summaries").add({
            "file_name": file_name,
            "summary": summary,
            "timestamp": timestamp
        })
        st.success("✅ Summary saved successfully!")
    except Exception as e:
        st.error(f"⚠️ Error saving summary: {e}")

def get_saved_summaries(user_email):
    """Retrieve saved summaries from Firebase."""
    summaries = []
    try:
        docs = db.collection("users").document(user_email).collection("summaries").order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
        for doc in docs:
            summaries.append(doc.to_dict())
    except Exception as e:
        st.error(f"⚠️ Error fetching saved summaries: {e}")
    return summaries

# Streamlit Sidebar for Navigation
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Choose an option", ["Home", "Previous Works"])

# Streamlit UI
if app_mode == "Home":
    st.title("📄 AI Document Summarizer")

    # Check if user is logged in
    if "user_email" not in st.session_state or not st.session_state["user_email"]:
        st.error("⚠️ Please log in to summarize and save your documents.")
    else:
        st.subheader(f"Welcome, {st.session_state['username']}!")
        
        if st.button("🚪 Logout"):
            st.session_state["user_email"] = None
            st.rerun()

        uploaded_file = st.file_uploader("📂 Upload your document", type=["pdf", "docx", "txt"])

        if uploaded_file:
            file_name = uploaded_file.name
            file_extension = os.path.splitext(file_name)[1].lower()
            
            with st.spinner("⏳ Summarizing your document..."):
                if file_extension == ".pdf":
                    text = extract_text_from_pdf(uploaded_file)
                elif file_extension == ".docx":
                    text = extract_text_from_docx(uploaded_file)
                elif file_extension == ".txt":
                    text = uploaded_file.read().decode("utf-8")
                else:
                    st.error("❌ Unsupported file type. Please upload a PDF, Word, or text file.")
                    text = None

                if text:
                    summary = summarize_text(text)
                    st.subheader("📝 Summary:")
                    st.write(summary)

                    # Automatically save summary to Firebase
                    save_summary_to_firestore(st.session_state["user_email"], file_name, summary)

                    # Download button for summary
                    b64 = base64.b64encode(summary.encode()).decode()
                    href = f'<a href="data:file/txt;base64,{b64}" download="summary.txt">📥 Download Summary as .txt</a>'
                    st.markdown(href, unsafe_allow_html=True)
                else:
                    st.error("❌ No text found in the document.")

elif app_mode == "Previous Works":
    st.title("📜 Your Previous Works")

    # Check if user is logged in
    if "user_email" not in st.session_state or not st.session_state["user_email"]:
        st.error("⚠️ Please log in to view your previous works.")
    else:
        # Display saved summaries
        summaries = get_saved_summaries(st.session_state["user_email"])
        if summaries:
            for item in summaries:
                with st.expander(f"📅 {item['timestamp']} - {item['file_name']}"):
                    st.write(item["summary"])
        else:
            st.info("ℹ️ No summaries found. Upload a document to generate and save a summary!")
