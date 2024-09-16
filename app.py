from flask import Flask, request, render_template, redirect
from PyPDF2 import PdfReader
import google.generativeai as genai

# Configure the Generative AI API
api_key = "Enter API KEY"
genai.configure(api_key=api_key)

app = Flask(__name__)
chat_history = []
conversation_chain = None  # To store extracted PDF text

# Function to extract text from PDFs
def get_pdf_text(pdf_docs):
    text = ''
    for pdf_file in pdf_docs:
        reader = PdfReader(pdf_file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

# Function to interact with Generative AI using PDF content
def generative_ai_with_pdf_context(prompt, pdf_text):
    # Combine the user prompt with the extracted PDF text as context
    context = f"Context: {pdf_text[:3000]} \n\nUser Query: {prompt}"  # Limit to 3000 chars for input size
    model = genai.GenerativeModel('gemini-1.5-flash')
    chat = model.start_chat(history=[])
    response = chat.send_message(context)
    return response.text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_documents():
    global conversation_chain
    pdf_docs = request.files.getlist('pdf_docs')  # Get uploaded PDF files
    raw_text = get_pdf_text(pdf_docs)  # Extract text from PDFs
    
    # Store PDF text in conversation_chain for later use in chat
    conversation_chain = raw_text
    return redirect('/chat')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    global chat_history, conversation_chain
    if request.method == 'POST':
        user_question = request.form['user_question']

        # Debugging: Check if the user question is captured
        print(f"User question: {user_question}")

        # If there's no PDF content yet, inform the user
        if not conversation_chain:
            response = "Please upload a PDF first!"
        else:
            # Generate AI response using both the user's question and PDF content
            response = generative_ai_with_pdf_context(user_question, conversation_chain)

        # Append user question and AI response to chat history
        chat_history.append({'content': f'You: {user_question}'})
        chat_history.append({'content': f'Bot: {response}'})

    return render_template('chat.html', chat_history=chat_history)
@app.route('/clear', methods=['POST'])
def clear_history():
    global chat_history
    chat_history.clear()  # Clear the chat history
    return redirect('/chat')  

if __name__ == '__main__':
    app.run(debug=True)
