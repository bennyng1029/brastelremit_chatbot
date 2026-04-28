import os
import openai
import re
from typing import List

class BrastelAgenticBot:
    def __init__(self, kb_files: List[str], base_url: str, api_key: str):
        self.client = openai.OpenAI(base_url=base_url, api_key=api_key)
        
        # Skill definitions for Read-on-Demand
        self.skills = {
            "registration": {"file": "registration_guide.md", "desc": "Steps to register, documents needed, and verification time."},
            "fees_rates": {"file": "knowledge_base.md", "desc": "Current exchange rates and transfer fee tiers."},
            "sending": {"file": "sending_money.md", "desc": "How to send money, limits, and delivery times."},
            "deposit": {"file": "deposit_locations.md", "desc": "Where and how to deposit money (JP Bank, Lawson, etc.)."},
            "partners": {"file": "partnership_network.md", "desc": "List of payout banks and agents in Philippines and Vietnam."},
            "legal": {"file": "legal_compliance.md", "desc": "AML policies, My Number requirements, and ID updates."},
            "cards": {"file": "card_management.md", "desc": "Difference between Yucho and Remit cards, and card fees."},
            "about": {"file": "about_brastel.md", "desc": "Company history, license details, and office location."}
        }

    def _estimate_tokens(self, text: str) -> int:
        """Rough estimate of token count (4 chars = 1 token)."""
        return len(text) // 4

    def _compress_history(self, history: List[dict], model_name: str) -> List[dict]:
        """Summarize the history to stay within token limits."""
        print("🗜️ History exceeds 32k tokens. Compressing...")
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in history])
        
        compression_prompt = f"""
Summarize the following conversation between a user and the Brastel Remit AI Assistant.
Extract the key facts (destination, amount, purpose) and the current status of the inquiry.
Keep the summary under 500 words.

Conversation:
{history_text}
"""
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[{"role": "system", "content": "You are a concise summarization assistant."},
                      {"role": "user", "content": compression_prompt}],
            temperature=0,
            max_tokens=800
        )
        summary = response.choices[0].message.content.strip()
        return [{"role": "system", "content": f"Previous conversation summary: {summary}"}]

    def _get_documentation(self, category: str) -> str:
        """Tool function to load documentation."""
        if category not in self.skills:
            return "Error: Category not found."
        
        file_path = self.skills[category]["file"]
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f"\n\n--- DOCUMENT: {category} ---\n{f.read()}"
        except FileNotFoundError:
            return f"Error: File {file_path} not found."

    def ask(self, user_query: str, model_name: str = "local-model", history: List[dict] = None):
        """Tool-Calling Agentic RAG."""
        if history is None:
            history = []
            
        # 1. Token Management (32k limit)
        full_history_text = "".join([m["content"] for m in history])
        if self._estimate_tokens(full_history_text) > 32000:
            history = self._compress_history(history, model_name)

        # 2. Tool Definition
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_documentation",
                    "description": "Retrieve official Brastel Remit documentation for a specific category to ensure accuracy.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "enum": list(self.skills.keys()),
                                "description": "The category of documentation to retrieve (e.g., 'fees_rates', 'registration')."
                            }
                        },
                        "required": ["category"]
                    }
                }
            }
        ]

        # 3. System Prompt
        system_prompt = f"""
You are the official Brastel Remit AI Support Assistant.
You have access to a tool to retrieve official documentation.

CRITICAL RULES:
1. USE TOOLS: Always call 'get_documentation' before answering specific questions about fees, rates, limits, or procedures. NEVER rely on your internal knowledge for these topics.
2. STRICT GROUNDING: If the documentation does not contain the answer, tell the user to contact support at 0120-983-891.
3. NO HALLUCINATION: Never invent numbers or requirements.
4. CONCISENESS: Be brief and direct.
5. LANGUAGE: Match the user's language.
6. FOLLOW-UP QUESTIONS: At the end of your FINAL response, always provide 2-3 extremely concise follow-up questions (3-5 words) written FROM THE CUSTOMER'S PERSPECTIVE. These should be natural questions a user would ask next (e.g., "What are the fees?", "How to register?", "Track my transfer"). Format them exactly like this:
Questions:
- Question 1
- Question 2
- Question 3
"""
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        if not history or history[-1]["content"] != user_query:
            messages.append({"role": "user", "content": user_query})

        # 4. Multi-turn Tool Interaction
        max_turns = 3
        for _ in range(max_turns):
            response = self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.0,
                max_tokens=1000
            )
            
            msg = response.choices[0].message
            messages.append(msg)
            
            if not msg.tool_calls:
                break
                
            for tool_call in msg.tool_calls:
                import json
                args = json.loads(tool_call.function.arguments)
                category = args.get("category")
                print(f"🛠️ AI is using tool to read: {category}")
                doc_content = self._get_documentation(category)
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": doc_content
                })

        # 5. Process Final Response
        content = messages[-1].content or ""
        
        # Clean up tags
        content = re.sub(r'<thought>.*?</thought>', '', content, flags=re.DOTALL)
        content = re.sub(r'Thinking Process:.*?\n', '', content)
        
        # Extract Follow-up questions
        follow_ups = []
        if "Questions:" in content:
            parts = content.split("Questions:")
            answer = parts[0].strip()
            questions_part = parts[1].strip()
            for line in questions_part.split("\n"):
                line = line.strip()
                match = re.match(r'^(?:[-*•]|\d+\.)\s*(.+)$', line)
                if match:
                    follow_ups.append(match.group(1).strip(" []\"'"))
        else:
            answer = content.strip()

        return {
            "answer": answer,
            "follow_ups": follow_ups[:3]
        }

if __name__ == "__main__":
    # LOCAL TEST CONFIG
    CONFIG = {
        "baseURL": "http://192.168.10.83:8000/v1",
        "apiKey": "omlx-z3phyzfx0gs0t2hy",
        "model": "Qwen3.5-4B-MLX-8bit"
    }

    bot = BrastelAgenticBot([], CONFIG["baseURL"], CONFIG["apiKey"])
    print("Welcome to the Hybrid Agentic Bot. Type 'exit' to quit.")
    while True:
        q = input("\nYou: ")
        if q.lower() == 'exit': break
        result = bot.ask(q, CONFIG["model"])
        print(f"Bot: {result['answer']}")
        if result['follow_ups']:
            print(f"Follow-ups: {result['follow_ups']}")
