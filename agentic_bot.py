import os
import openai
import re
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
You are the official Brastel Remit AI Support Assistant.
Your goal is to answer questions using ONLY the information in the provided SOURCE material.

RULES:
1. Grounding: If the answer is not in the SOURCE material, say: "I'm sorry, I don't have that information in my current documentation. Please contact Brastel Support at 0120-983-891."
2. Accuracy: Never hallucinate fees, limits, or document requirements.
3. Language: Respond in the same language the user uses.
4. Tone: Professional and helpful.

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
                max_tokens=1000 # Increased to allow for internal thinking + answer
            )
            
            content = response.choices[0].message.content
            
            # Filter out <thought> tags (common in reasoning models)
            content = re.sub(r'<thought>.*?</thought>', '', content, flags=re.DOTALL)
            
            # Filter out "Thinking Process:" or "Analysis:" blocks
            content = re.sub(r'Thinking Process:.*?\n', '', content)
            content = re.sub(r'Analysis:.*?\n', '', content)
            
            return content.strip()
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
