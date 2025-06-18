

# 💬 Flowise Chat - Web Interface

A modern web-based chat interface for interacting with Flowise agents. It supports agent selection, file uploads, web search integration and customizable themes.

---

## ✨ Features

- 🔍 **Agent Selection** — Choose from your available Flowise chatflows
- 📎 **File Uploads** — Process PDF, DOCX, and TXT files  
- 🌐 **Web Search** — Integrated DuckDuckGo search for enhanced research not responce  
- 🎨 **Theming** — 7 unique visual themes including:
  - 🌑 Dark
  - 🌕 Light  
  - 🤖 Cyberpunk  
  - 🖥️ Retro Terminal  
  - 📇 Vintage Typewriter  
  - 📚 Comic Book style
  
- 🎛️ **Model Parameters** — Fine-tune temperature, top-p, top-k, and more  
- 🧠 **System Prompts** — Customize AI behavior with system instructions  
- 🕓 **Conversation History** — Manage chat sessions with history tracking  
- 💡 **Code Highlighting** — Automatic syntax highlighting for code snippets  

---
## preview
🎬 [Click here to watch the demo on YouTube](https://youtu.be/SpfmQEIuSuE)



---
## ⚙️ Prerequisites

- 🐍 Python 3.8+  
- 🧠 Flowise running (`FLOWISE_URL` should point to your instance)
- 🧰 Node.js (for development mode)

---

## 🚀 Installation

### 1. 📥 Clone the repository

```bash
git clone https://github.com/Laszlobeer/ollama_simple_webui.git

cd ollama_simple_webui.git
````

### 2. 🧪 Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Linux/macOS
venv\Scripts\activate     # On Windows
```

### 3. 📦 Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🛠️ Configuration

Create a `.env` file in the project root with optional settings:

```env
FLASK_DEBUG=1
UPLOAD_FOLDER=uploads
PORT=5001
USERNAME=admin
PASSWORD=changeme
FLOWISE_URL=http://localhost:3000
FLOWISE_API_KEY=
```

---

## ▶️ Usage

### 1. 🔧 Start the Flask server

```bash
python app.py
```

### Docker

```bash
docker build -t flowise-chat .
docker run -p 5001:5001 --env-file .env flowise-chat
```

### 2. 🌐 Access the web interface

Open your browser and go to:

```
http://localhost:5001
```

### 3. 🖱️ Interact with the interface

* 📎 Attach files using the paperclip icon
* 🔍 Enable/disable web search from the sidebar
* 🎨 Switch themes using the theme selector
* 🎛️ Adjust model parameters live during chat

---

## 📁 File Processing

Supported file formats:

* 📄 **PDF** — Extracts text
* 📝 **DOCX** — Microsoft Word documents
* 📃 **TXT** — Plain text files

Uploaded files are parsed and their content becomes available to the chat model.

---

## 🗂️ Project Structure

```
ollama-web-chat/
├── app.py               # Flask application
├── requirements.txt     # Python dependencies
├── static/              # Static assets (CSS, JS)
│   └── js/
│       └── fileProcessor.js
├── templates/           # HTML templates
│   └── index.html
├── uploads/             # Uploaded files
└── system_prompt.txt    # Custom system prompt template
```

---

## 📡 API Endpoints

| Endpoint       | Method   | Description                    |
| -------------- | -------- | ------------------------------ |
| `/api/models`  | GET      | 🧠 List available models       |
| `/api/chat`    | POST     | 💬 Main chat endpoint          |
| `/api/prompt`  | GET/POST | ✍️ Manage system prompts       |
| `/upload`      | POST     | 📎 File upload handler         |
| `/api/history` | DELETE   | 🗑️ Clear conversation history |

---

## 🧩 Troubleshooting

### Common Issues

* ❌ **"No agents found"**
  Ensure your Flowise instance is running and accessible

* ⚠️ **File upload errors**
  Check if the `uploads/` directory exists and has proper write permissions

* 🌐 **Web search not working**
  Confirm your internet connection is active

---

## 🤝 Contributing

Contributions are welcome! 🙌

1. 🍴 Fork the repository
2. 🛠️ Create a new branch

```bash
git checkout -b feature/your-feature
```

3. ✅ Commit your changes

```bash
git commit -am "Add some feature"
```

4. 🚀 Push your branch

```bash
git push origin feature/your-feature
```

5. 🔁 Open a Pull Request

---

## 📜 License

This project is licensed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

---

> ⚠️ **Note**: This project is not officially affiliated with Flowise. It is a community-created interface designed to interact with Flowise agents via a web interface.

## ☕ Support My Work

If you find this project helpful, consider buying me a coffee!  
Your support keeps the code flowing! 🙏💻

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-%E2%98%95-orange?style=for-the-badge)](https://ko-fi.com/laszlobeer)

👉 [ko-fi.com/laszlobeer](https://ko-fi.com/laszlobeer)

