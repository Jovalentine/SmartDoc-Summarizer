# 📄 SmartDoc Summarizer

SmartDoc Summarizer is an intelligent document summarization web application built using Streamlit and Transformer-based NLP models like BART. It allows users to upload `.pdf`, `.docx`, or `.txt` files and receive a concise summary of the document content. All summaries are stored securely in Firebase, allowing users to log in and access their previously summarized work.

---

## 🔧 Features

- ✨ **Automatic Document Summarization** using Facebook's BART (`facebook/bart-large-cnn`) model.
- 🔐 **User Authentication** with Firebase (Email & Password).
- 💾 **Secure Summary Storage** in Firestore under each user's profile.
- 📝 **Supports PDF, DOCX, and TXT files**.
- 🕘 **Access History of Summaries** from the sidebar.
- 📥 **Download Summary as `.txt`**.
- ☁️ Hosted locally or on Streamlit Cloud.

---

## ⚙️ Tech Stack

| Layer        | Technology Used                      |
|--------------|--------------------------------------|
| Frontend     | Streamlit                            |
| Backend      | Python, Hugging Face Transformers    |
| Authentication | Firebase Authentication           |
| Database     | Firestore (Firebase)                 |
| NLP Model    | `facebook/bart-large-cnn` (Transformers) |
| OCR Support  | `pytesseract` (for scanned images - optional future upgrade) |

---

## 🛠 Installation & Setup

1. **Clone the Repository**
git clone https://github.com/Jovalentine/SmartDoc-Summarizer.git
cd SmartDoc-Summarizer
2. **Create & Activate Virtual Environment**
python -m venv env
env\Scripts\activate  # Windows
source env/bin/activate  # Linux/macOS
3. **Install Dependencies**
pip install -r requirements.txt
4. **Add Firebase Admin SDK**
Place your Firebase service account key JSON file inside the Assets/ folder.
Make sure the file is .gitignored to prevent pushing secrets to GitHub.
4. **Run the App**
streamlit run app.py

🔐 Security Considerations
Password authentication via Firebase.
Secret keys are excluded using .gitignore.
Add OAuth (Google/GitHub) login support for production-grade auth (future work).
Session handling with timeout alerts (optional enhancement).

📂 Folder Structure

SmartDoc-Summarizer/
│
├── Assets/                         # Firebase key and assets
├── app.py                          # Main application (Streamlit)
├── summarizer.py                   # Optional summary processing module
├── auth.py                         # Optional modular auth helper
├── requirements.txt                # Python dependencies
├── .gitignore                      # Ignored files
└── README.md                       # Project documentation
📈 Future Enhancements

🔐 Google/GitHub OAuth authentication
🧠 Switch to T5 / Pegasus for improved abstractive summaries
🗃 File versioning and advanced history dashboard
📊 Summary evaluation (e.g., ROUGE score visualization)

👨‍💻 Developed By
Francis Johan M
Abishek I
Mentor: E. Manohar
Institution: Francis Xavier Engineering College

