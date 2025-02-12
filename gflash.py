import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os
from dotenv import load_dotenv

# Apply dark theme and custom styling
st.markdown("""
    <style>
    /* Main app styling */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* Input fields */
    .stTextInput input {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
        border: 1px solid #3A3A3A !important;
        border-radius: 5px;
    }
    
    /* File uploader */
    .stFileUploader {
        background-color: #1E1E1E;
        border: 1px solid #3A3A3A;
        border-radius: 5px;
        padding: 15px;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #00FFAA !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 5px !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton button:hover {
        background-color: #00CC88 !important;
        box-shadow: 0 4px 6px rgba(0, 255, 170, 0.2) !important;
    }
    
    /* Success messages */
    .success-message {
        background-color: #1E1E1E;
        border-left: 4px solid #00FFAA;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    /* Progress bar */
    .stProgress .st-bo {
        background-color: #00FFAA !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #00FFAA !important;
    }
    
    /* Response container */
    .response-container {
        background-color: #1E1E1E;
        border: 1px solid #3A3A3A;
        border-radius: 5px;
        padding: 1rem;
        margin-top: 1rem;
    }

    /* Sidebar styles */
    .sidebar-content {
        background-color: #1E1E1E;
        border: 1px solid #3A3A3A;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .instruction-step {
        color: #E0E0E0;
        margin: 0.5rem 0;
        padding: 0.5rem;
        background-color: #2A2A2A;
        border-radius: 4px;
        border-left: 3px solid #00FFAA;
    }
    </style>
    """, unsafe_allow_html=True)

import streamlit as st
import google.generativeai as genai

# Load API Key from Streamlit Secrets
GOOGLE_API_KEY = st.secrets["general"]["GOOGLE_API_KEY"]

if not GOOGLE_API_KEY:
    st.error("Google API Key not found. Please configure it in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)


# Load environment variables from .env file
# load_dotenv()

# # Set your Google API key
# GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# if not GOOGLE_API_KEY:
#     st.error("Please set the GOOGLE_API_KEY environment variable.")
#     st.stop()

# genai.configure(api_key=GOOGLE_API_KEY)

# Initialize session state for PDF content
if 'pdf_content' not in st.session_state:
    st.session_state.pdf_content = None

def load_gemini_pro_model():
    return genai.GenerativeModel('gemini-1.5-flash-latest')

def extract_text_from_pdf(pdf_file):
    text = ""
    pdf_reader = PdfReader(pdf_file)
    total_pages = len(pdf_reader.pages)
    
    # Create a progress bar
    progress_bar = st.progress(0)
    
    for i, page in enumerate(pdf_reader.pages):
        text += page.extract_text()
        # Update progress bar
        progress = (i + 1) / total_pages
        progress_bar.progress(progress)
    
    # Clear progress bar after completion
    progress_bar.empty()
    return text

def generate_response(model, prompt, context):
    try:
        with st.spinner("🤖 Generating response..."):
            response = model.generate_content(f"""
            Based on the following context, please provide a clear and concise answer to the question.
            If the answer cannot be found in the context, please say so.
            
            Question: {prompt}
            
            Context: {context}
            """)
            return response.text
    except Exception as e:
        return f"Error generating response: {e}"

def clear_data():
    st.session_state.pdf_content = None
    st.success("✨ All data cleared successfully!")

def main():
    # App header
    st.title("📚 Smart PDF Assistant")
    st.markdown("### Powered by aiIntercept.online")
    st.markdown("---")

    # Clear data button in sidebar
    with st.sidebar:
        st.title("🛠️ Controls")
        if st.button("🗑️ Clear Data", key="clear_data"):
            clear_data()
        
        st.markdown("---")
        st.markdown("### 📋 Instructions")
        st.markdown(
            '<div class="sidebar-content">'
            '<div class="instruction-step">1. Upload your PDF document</div>'
            '<div class="instruction-step">2. Wait for the text extraction</div>'
            '<div class="instruction-step">3. Ask questions about the content</div>'
            '<div class="instruction-step">4. Use \'Clear Data\' to upload a new PDF</div>'
            '</div>',
            unsafe_allow_html=True
        )

    # Main content area
    if st.session_state.pdf_content is None:
        uploaded_file = st.file_uploader(
            "📎 Upload your PDF document",
            type="pdf",
            help="Select a PDF file to analyze"
        )

        if uploaded_file is not None:
            with st.spinner("📄 Extracting text from PDF..."):
                pdf_text = extract_text_from_pdf(uploaded_file)
                st.session_state.pdf_content = pdf_text
                st.markdown(
                    '<div class="success-message">✅ PDF processed successfully! You can now ask questions.</div>',
                    unsafe_allow_html=True
                )

    # Question input and response section
    if st.session_state.pdf_content is not None:
        model = load_gemini_pro_model()
        
        user_question = st.text_input(
            "🔍 Ask a question about your document:",
            placeholder="Type your question here..."
        )

        if user_question:
            response = generate_response(model, user_question, st.session_state.pdf_content)
            
            st.markdown(
                '<div class="response-container">'
                '<h3 style="color: #00FFAA;">🤖 Answer:</h3>'
                f'<p>{response}</p>'
                '</div>',
                unsafe_allow_html=True
            )

if __name__ == "__main__":
    main()