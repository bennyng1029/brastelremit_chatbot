# Brastel Remit AI Chatbot (Agentic RAG)

A premium, AI-powered chatbot designed for **Brastel Remit** (International Money Transfer). This project demonstrates a modern **Agentic RAG** approach, using local LLMs to provide grounded and accurate support for international remittances.

---

## 🌟 Features
- **Premium UI**: Sleek, glassmorphism-based chat widget tailored to Brastel's branding.
- **Agentic RAG**: Unlike traditional RAG, this bot reads complete Markdown source files to ensure context is never lost.
- **Strict Grounding**: The AI is instructed to only answer using provided documentation, preventing hallucinations regarding fees or KYC requirements.
- **Local LLM Integration**: Fully compatible with OpenAI-style local APIs (Ollama, LM Studio, etc.).

---

## 🧠 Working Logic
This bot uses an **Agentic / Long-Context** approach:
1. **Knowledge Extraction**: All Brastel Remit data is stored in clean Markdown files in the `knowledge/` directory (`registration_guide.md`, `sending_money.md`, etc.).
2. **System Grounding**: When a user asks a question, the backend loads these files into the LLM's system prompt.
3. **Reasoning Loop**: The LLM acts as an agent, scanning the source material to find the specific rule or fee tier that applies to the user's query.
4. **Accuracy Enforcement**: If the answer isn't in the documents, the bot is programmed to say "I don't know" rather than guessing.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.8+
- A running local LLM server (OpenAI compatible API)

### 2. Installation
```powershell
# Clone the repository
git clone https://github.com/bennyng1029/brastelremit_chatbot.git
cd brastelremit_chatbot

# Install dependencies
pip install flask openai
```

### 3. Start the Server
```powershell
python server.py
```
Visit **`http://localhost:5005`** in your browser to interact with the bot.

---

## ⚙️ Configuration & Changing the LLM

All configurations are located at the top of `server.py`.

### Changing the Model or IP
To point the bot to a different LLM or change the model name, edit the `LOCAL_CONFIG` and `MODEL_NAME` variables in `server.py`:

```python
# In server.py
LOCAL_CONFIG = {
    "baseURL": "http://192.168.10.83:8000/v1", # Change to your LLM's IP/Port
    "apiKey": "omlx-z3phyzfx0gs0t2hy"          # Your API Key
}

# ... inside the ask() function ...
MODEL_NAME = "Qwen3.5-4B-MLX-8bit"             # Change to your preferred model
```

### Adding New Knowledge
To expand the bot's intelligence, simply create a new `.md` file in the `knowledge/` directory and add its filename to the `KNOWLEDGE_FILES` list in `server.py`.

---

## 📂 Project Structure
- `server.py`: Flask web server & API bridge.
- `agentic_bot.py`: Core AI logic and prompt engineering.
- `index.html` / `style.css` / `app.js`: Premium frontend chat widget.
- `knowledge/`: Folder containing knowledge base source files (`*.md`, `*.json`).
