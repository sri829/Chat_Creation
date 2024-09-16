import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai

# Configure the Generative AI API
api_key = "ENTER API KEY"  # Replace with your API key
genai.configure(api_key=api_key)

# Function to extract text from the uploaded PDF
def Pdf_extractor(pdf_file):
    text = ''
    if pdf_file is not None:
        reader = PdfReader(pdf_file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

# Function to interact with Generative AI using PDF content
def generative_ai_with_pdf_context(prompt, pdf_text):
    context = f"Context: {pdf_text[:3000]} \n\nUser Query: {prompt}"
    model = genai.GenerativeModel('gemini-1.5-flash')
    chat = model.start_chat(history=[])
    response = chat.send_message(context)
    return response.text

# Streamlit User Interface

# Set page title and configuration for better UX
st.set_page_config(page_title="🤖 PDF Chatbot", page_icon="🤖", layout="wide")

# Custom CSS for better UI
st.markdown("""
    <style>
    .stFileUpload {
        display: inline-block;
        margin-bottom: 10px;
    }
    .chat-box {
        max-height: 400px;
        overflow-y: auto;
        display: flex;
        flex-direction: column-reverse; /* Reverse chat direction */
    }
    .user-message, .bot-response {
        padding: 10px;
        margin: 5px 0;
        border-radius: 10px;
        max-width: 75%;
    }
    .user-message {
        background-color: #DCF8C6;
        align-self: flex-start;
    }
    .bot-response {
        background-color: #f0f2f5;
        align-self: flex-end;
        border-left: 5px solid #00BFFF;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state for chat history and user query
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'saved_histories' not in st.session_state:
    st.session_state['saved_histories'] = {}
if 'user_query' not in st.session_state:
    st.session_state['user_query'] = ""  # Initialize the user query

# Sidebar for history navigation
with st.sidebar:
    st.title("💾 History")
    
    # Automatically save chat history under a default name if new chats are available
    if st.session_state['chat_history']:
        history_name = f"Chat {len(st.session_state['saved_histories']) + 1}"
        if history_name not in st.session_state['saved_histories']:
            st.session_state['saved_histories'][history_name] = list(st.session_state['chat_history'])
    
    # Slider to select and view saved histories
    saved_keys = list(st.session_state['saved_histories'].keys())
    if saved_keys:
        selected_history = st.selectbox("Select a saved chat", options=saved_keys)
        if selected_history:
            st.write("### Chat Preview")
            for chat in st.session_state['saved_histories'][selected_history]:
                st.write(f"**You:** {chat['user']}")
                st.write(f"**🤖 Bot:** {chat['bot']}")

            # Option to clear the selected saved history
            if st.button("Clear Selected History"):
                del st.session_state['saved_histories'][selected_history]
                st.experimental_rerun()

# Main UI

st.title("📄 PDF Chatbot 🤖")
st.write("Upload a PDF and ask questions about its content!")

# Step 1: PDF File Upload Section
pdf_file = st.file_uploader("", type=['pdf'], label_visibility="collapsed")

if pdf_file:
    # Step 2: Extract PDF content with spinner
    with st.spinner('Extracting text from PDF...'):
        extracted_text = Pdf_extractor(pdf_file)

    # Optional Step: Display the extracted text
    with st.expander("Show Extracted PDF Text (Optional)"):
        st.text_area('Extracted PDF Text', extracted_text, height=150)

    # Step 3: Floating Chat Bar
    st.text_input("Ask something about the PDF:", key="user_query_input", value=st.session_state['user_query'], placeholder="Type your question here")

    if st.session_state['user_query_input']:
        with st.spinner('Generating response...'):
            response = generative_ai_with_pdf_context(st.session_state['user_query_input'], extracted_text)
        
        # Save the conversation in session state
        st.session_state['chat_history'].append({'user': st.session_state['user_query_input'], 'bot': response})
        st.session_state['user_query'] = ""  # Clear input after query is processed

        # Clear the input field after submission
        st.session_state['user_query_input'] = ""

    # Step 4: Display the chat history (scroll from bottom to top)
    st.subheader("Chat History")
    chat_container = st.container()
    with chat_container:
        for chat in reversed(st.session_state['chat_history']):
            st.markdown(f"<div class='user-message'><b>You:</b> {chat['user']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='bot-response'><b>Bot:</b> {chat['bot']}</div>", unsafe_allow_html=True)

    # Step 5: Clear Chat Button
    if st.button("Clear Chat History"):
        st.session_state['chat_history'] = []  # Clear chat history in session state
        st.experimental_rerun()  # Reload the app to reflect changes

else:
    st.info("Please upload a PDF file to start interacting.")

# Footer Section
st.write("----")
st.write("🔍 Powered by Google Gemini 1.5 Flash and Streamlit")
