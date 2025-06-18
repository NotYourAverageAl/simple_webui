from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, session
import os
import json
import requests
from dotenv import load_dotenv
from duckduckgo_search import DDGS
from PyPDF2 import PdfReader
from docx import Document
import re
from urllib.parse import urlparse
import html

load_dotenv()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = os.getenv('SECRET_KEY', 'supersecret')

USERNAME = os.getenv('USERNAME', 'admin')
PASSWORD = os.getenv('PASSWORD', 'password')
FLOWISE_URL = os.getenv('FLOWISE_URL', 'http://localhost:3000')
FLOWISE_API_KEY = os.getenv('FLOWISE_API_KEY', '')

# Theme loader
@app.context_processor
def inject_theme():
    return dict(theme=request.cookies.get('theme', 'dark'))

# Simple login system
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == USERNAME and request.form.get('password') == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.before_request
def require_login():
    if request.endpoint in ('login', 'static', 'uploaded_file'):
        return
    if not session.get('logged_in'):
        return redirect(url_for('login'))

# List Flowise chatflows
@app.route('/api/flows')
def get_flows():
    try:
        headers = {}
        if FLOWISE_API_KEY:
            headers['Authorization'] = f'Bearer {FLOWISE_API_KEY}'
        resp = requests.get(f"{FLOWISE_URL}/chatflows", headers=headers)
        resp.raise_for_status()
        flows = resp.json()
        result = [{
            'id': f.get('_id') or f.get('id'),
            'name': f.get('name', 'Unnamed')
        } for f in flows]
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Process file content
def extract_text_from_file(filepath):
    text = ""
    try:
        if filepath.lower().endswith('.pdf'):
            with open(filepath, 'rb') as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        elif filepath.lower().endswith('.docx'):
            doc = Document(filepath)
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif filepath.lower().endswith('.txt'):
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            text = "[Unsupported file format]"
        
        # Clean and truncate text
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:10000]  # Truncate to 10k characters
    except Exception as e:
        return f"[Error processing file: {str(e)}]"

# Chat endpoint
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        flow_id = data.get('flow')
        messages = data.get('messages', [])
        options = data.get('options', {})
        web_search = data.get('webSearch', False)

        user_messages = [m['content'] for m in messages if m.get('role') == 'user']
        question = user_messages[-1] if user_messages else ''

        payload = {
            "question": question,
            "history": [
                {
                    "role": "userMessage" if m['role'] == 'user' else 'apiMessage',
                    "content": m['content']
                } for m in messages
            ],
            "overrideConfig": {
                "temperature": options.get('temperature', 0.8),
                "top_p": options.get('topP', 0.9),
                "top_k": options.get('topK', 40)
            }
        }

        if 'system' in data:
            payload['history'].insert(0, {"role": "apiMessage", "content": data['system']})
        
        web_search_results = []
        webSearchNote = ""
        if web_search and question:
            try:
                with DDGS() as ddgs:
                    results = ddgs.text(question, max_results=5)
                    web_search_results = [
                        {
                            "title": r["title"],
                            "url": r["href"],
                            "snippet": r["body"],
                            "domain": urlparse(r["href"]).netloc
                        } for r in results
                    ]
            except Exception as e:
                app.logger.error(f"Web search error: {str(e)}")

            if web_search_results:
                webSearchNote = "I found these sources to help answer your question:"
                search_context = "### Current Web Search Results:\n"
                search_context += "Use these search results to provide a direct answer to the user's question. " \
                                 "Cite sources using their domain names in parentheses. " \
                                 "When possible, provide specific facts, figures, or quotes from the sources.\n\n"

                for i, result in enumerate(web_search_results):
                    search_context += f"{i+1}. [{result['title']}]({result['url']})\n"
                    search_context += f"   Summary: {result['snippet']}\n\n"

                payload['history'].insert(0, {"role": "apiMessage", "content": search_context})
        
        # Process file content if referenced in messages
        for msg in messages:
            if msg['role'] == 'user' and '📄 Attached file' in msg['content']:
                # Extract filename from message
                match = re.search(r'📄 Attached file: (.+?)\n', msg['content'])
                if match:
                    filename = match.group(1)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    if os.path.exists(filepath):
                        file_content = extract_text_from_file(filepath)
                        msg['content'] += f"\n\nFile content:\n{file_content}"
        
        headers = {'Content-Type': 'application/json'}
        if FLOWISE_API_KEY:
            headers['Authorization'] = f'Bearer {FLOWISE_API_KEY}'
        response = requests.post(f"{FLOWISE_URL}/prediction/{flow_id}", json=payload, headers=headers)
        response.raise_for_status()

        response_data = response.json()
        if web_search_results:
            response_data['web_search_results'] = web_search_results
            response_data['webSearchNote'] = webSearchNote
            
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# System prompt handler
@app.route('/api/prompt', methods=['POST'])
def update_prompt():
    try:
        new_prompt = request.json.get('prompt')
        # Save to file
        with open('system_prompt.txt', 'w') as f:
            f.write(new_prompt)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get current system prompt
@app.route('/api/prompt', methods=['GET'])
def get_prompt():
    try:
        if os.path.exists('system_prompt.txt'):
            with open('system_prompt.txt', 'r') as f:
                prompt = f.read()
            return jsonify({'prompt': prompt})
        return jsonify({'prompt': 'You are a helpful AI assistant.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# File upload handler
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        # Extract text content for AI
        file_content = extract_text_from_file(file_path)
        
        return jsonify({
            'filename': file.filename,
            'path': file_path,
            'content': file_content
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# History management
@app.route('/api/history', methods=['DELETE'])
def clear_history():
    try:
        open('history.json', 'w').close()
        return jsonify({'status': 'cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    theme = request.cookies.get('theme', 'dark')
    return render_template('index.html', theme=theme)

if __name__ == '__main__':
    app.run(debug=True, port=5001)