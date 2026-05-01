import os
from flask import Flask, request, jsonify, send_from_directory
from agentic_bot import BrastelAgenticBot

# Get the absolute path of the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=BASE_DIR)

# Configuration
LOCAL_CONFIG = {
    "baseURL": "http://192.168.10.83:8000/v1",
    "apiKey": "omlx-z3phyzfx0gs0t2hy"
}

KNOWLEDGE_FILES = [
    os.path.join(BASE_DIR, "knowledge/knowledge_base.md"),
    os.path.join(BASE_DIR, "knowledge/registration_guide.md"),
    os.path.join(BASE_DIR, "knowledge/sending_money.md"),
    os.path.join(BASE_DIR, "knowledge/deposit_locations.md")
]

# Initialize the Bot with absolute paths
bot = BrastelAgenticBot(
    kb_files=KNOWLEDGE_FILES,
    base_url=LOCAL_CONFIG["baseURL"],
    api_key=LOCAL_CONFIG["apiKey"]
)

@app.route('/')
def index():
    """Serve the main HTML file."""
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve CSS, JS, and other assets from the same directory."""
    return send_from_directory(BASE_DIR, filename)

@app.route('/ask', methods=['POST'])
def ask():
    """API endpoint for the chatbot logic."""
    data = request.json
    user_query = data.get('query', '')
    history = data.get('history', [])
    session_knowledge = data.get('session_knowledge', [])
    
    if not user_query:
        return jsonify({"error": "No query provided"}), 400
    
    # Use the specific model available on your server
    MODEL_NAME = "Qwen3.5-4B-MLX-8bit"
    
    print(f"User Asked: {user_query} (History Length: {len(history)}, Knowledge Chunks: {len(session_knowledge)})")
    result = bot.ask(user_query, model_name=MODEL_NAME, history=history, session_knowledge=session_knowledge)
    return jsonify({
        "answer": result["answer"],
        "follow_ups": result["follow_ups"],
        "session_knowledge": result["session_knowledge"]
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("BRASTEL CHATBOT SERVER IS RUNNING")
    print(f"FILES: {BASE_DIR}")
    print("URL: http://localhost:5005")
    print("="*60 + "\n")
    # Using host='0.0.0.0' so it's accessible on your local network
    app.run(host='0.0.0.0', port=5005, debug=True)
