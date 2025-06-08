import streamlit as st
from transformers import pipeline
from docx import Document
from PyPDF2 import PdfReader
import firebase_admin
from firebase_admin import credentials, auth, firestore
import time
from datetime import datetime

# Initialize Firebase only if not already initialized
if not firebase_admin._apps:
  cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)

# Firestore database reference
db = firestore.client()

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None

# Function to split long text into chunks
def split_text(text, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# Function to register users
def register_user(username, email, password):
    try:
        user = auth.create_user(email=email, password=password)
        db.collection("users").document(user.uid).set({"username": username, "email": email})
        st.success("✅ Registration successful! You can now log in.")
    except Exception as e:
        st.error(f"❌ Error: {e}")

# Function to verify login
def login_user(email, password):
    try:
        user = auth.get_user_by_email(email)
        user_doc = db.collection("users").document(user.uid).get()
        if user_doc.exists:
            st.session_state['logged_in'] = True
            st.session_state['user_email'] = email
            st.session_state['username'] = user_doc.to_dict().get("username")
            st.session_state['user_id'] = user.uid  # Store user ID
            st.success("✅ Login successful! Redirecting...")
            time.sleep(1)
            st.rerun()
        else:
            st.error("❌ User data not found in database!")
    except Exception as e:
        st.error(f"❌ Invalid login credentials: {e}")

# Function to log out
def logout_user():
    st.session_state['logged_in'] = False
    st.session_state.pop('user_email', None)
    st.session_state.pop('user_id', None)
    st.success("✅ Logged out successfully! Redirecting to login page...")
    time.sleep(1)
    st.rerun()

# Function to save summary in Firebase
def save_summary(user_id, original_text, summary):
    try:
        summary_data = {
            "text": original_text,
            "summary": summary,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        db.collection("users").document(user_id).collection("summaries").add(summary_data)
        st.success("✅ Summary saved successfully!")
    except Exception as e:
        st.error(f"❌ Error saving summary: {e}")

# Function to retrieve saved summaries
def get_saved_summaries(user_id):
    try:
        summaries_ref = db.collection("users").document(user_id).collection("summaries").order_by("timestamp", direction=firestore.Query.DESCENDING)
        summaries = summaries_ref.stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in summaries]
    except Exception as e:
        st.error(f"❌ Error fetching summaries: {e}")
        return []

# Registration Page
def register_page():
    st.markdown("<h2 style='text-align: center;'>🔐 Register</h2>", unsafe_allow_html=True)
    username = st.text_input("👤 Enter Username")
    email = st.text_input("📧 Enter Email")
    password = st.text_input("🔑 Enter Password", type="password")
    confirm_password = st.text_input("🔑 Confirm Password", type="password")
    
    if st.button("📝 Register", use_container_width=True):
        if password != confirm_password:
            st.error("❌ Passwords do not match!")
        elif username and email and password:
            register_user(username, email, password)
        else:
            st.error("❌ All fields are required!")

# Login Page
def login_page():
    st.markdown("<h2 style='text-align: center;'>🔑 Login</h2>", unsafe_allow_html=True)
    email = st.text_input("📧 Enter Email")
    password = st.text_input("🔑 Enter Password", type="password")
    
    if st.button("➡️ Login", use_container_width=True):
        if email and password:
            login_user(email, password)
        else:
            st.error("❌ All fields are required!")

# Document Summarizer Page
def summarizer_app():
    st.markdown("<h1 style='text-align: center;'>📄 SmartDocSummarizer</h1>", unsafe_allow_html=True)
    st.write("Upload a document to receive a summarized version.")

    st.subheader(f"👋 Welcome, {st.session_state.get('username', 'User')}!")
    if st.button("🚪 Logout", use_container_width=True):
        logout_user()

    st.markdown("---")
    
    uploaded_file = st.file_uploader("📂 Choose a document (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
    if uploaded_file:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        text = ""

        with st.spinner("📜 Extracting text from document..."):
            if file_extension == "pdf":
                pdf_reader = PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""
            elif file_extension == "docx":
                doc = Document(uploaded_file)
                for para in doc.paragraphs:
                    text += para.text + "\n"
            elif file_extension == "txt":
                text = uploaded_file.read().decode("utf-8")

        if text:
            summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            text_chunks = split_text(text)
            summary = ""

            with st.spinner("🔄 Summarizing your document... Please wait."):
                for chunk in text_chunks:
                    summary += summarizer(chunk, max_length=200, min_length=50, do_sample=False)[0]["summary_text"] + "\n"

            st.markdown("<h3>📝 Summary:</h3>", unsafe_allow_html=True)
            st.write(summary)

            if st.button("💾 Save Summary", use_container_width=True):
                save_summary(st.session_state["user_id"], text, summary)

            st.download_button("📥 Download Summary as Text File", summary, file_name="summary.txt", mime="text/plain")

    st.markdown("---")
    st.subheader("📜 Saved Summaries")
    summaries = get_saved_summaries(st.session_state["user_id"])
    for item in summaries:
        with st.expander(f"📅 {item['timestamp']}"):
            st.write(item["summary"])

# Main App Logic
st.sidebar.markdown("<h2>📌 Navigation</h2>", unsafe_allow_html=True)
if st.session_state["logged_in"]:
    summarizer_app()
else:
    page = st.sidebar.radio("🔍 Choose Page", ["Login", "Register"])
    if page == "Login":
        login_page()
    elif page == "Register":
        register_page()
