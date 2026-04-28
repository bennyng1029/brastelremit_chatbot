import os
import openai
from typing import List

class BrastelAgenticBot:
    def __init__(self, kb_files: List[str], base_url: str, api_key: str):
        self.kb_files = kb_files
        self.client = openai.OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        self.full_context = self._load_all_kbs()

    def _load_all_kbs(self):
        """Reads and combines all markdown knowledge base files."""
        combined_content = ""
        for file_path in self.kb_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    combined_content += f"\n\n--- SOURCE: {os.path.basename(file_path)} ---\n"
                    combined_content += f.read()
            except FileNotFoundError:
                print(f"Warning: {file_path} not found.")
        return combined_content

    def get_system_prompt(self):
        """Constructs a direct system prompt for speed."""
        return f"""
You are the Brastel AI Assistant. Answer accurately using ONLY the SOURCE MATERIAL below.
CRITICAL: Do NOT include any "Thinking Process", "Thought", or "Analysis" sections. 
CRITICAL: Do NOT explain your reasoning. Start your response IMMEDIATELY with the final answer.
Be extremely concise.

--- SOURCE MATERIAL ---
{self.full_context}
--- END OF SOURCE MATERIAL ---
"""

    def ask(self, user_query, model_name="local-model"):
        """Sends the query to the local LLM server with a context limit check."""
        system_prompt = self.get_system_prompt()
        total_length = len(system_prompt) + len(user_query)

        # 4k Token Limit Check (Approx 16,000 characters)
        if total_length > 16000:
            return "Sorry, we might need some assistant, the context window exceeds 4k limit."

        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.1,
                max_tokens=500,
                stop=["Thinking Process:", "Thought:", "Analysis:"] # Force-stop reasoning headers
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error connecting to LLM: {str(e)}"

if __name__ == "__main__":
    # USER CONFIGURATION
    LOCAL_CONFIG = {
        "baseURL": "http://192.168.10.83:8000/v1",
        "apiKey": "omlx-z3phyzfx0gs0t2hy"
    }
    
    KNOWLEDGE_FILES = [
        "knowledge_base.md",
        "registration_guide.md",
        "sending_money.md",
        "deposit_locations.md"
    ]

    bot = BrastelAgenticBot(
        kb_files=KNOWLEDGE_FILES,
        base_url=LOCAL_CONFIG["baseURL"],
        api_key=LOCAL_CONFIG["apiKey"]
    )
    
    print("\n🚀 Brastel Agentic Bot is Ready (Connected to Local LLM)")
    print("-" * 50)
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ['exit', 'quit']:
            break
        
        print("Bot is thinking...")
        answer = bot.ask(user_input)
        print(f"\nAssistant: {answer}")
