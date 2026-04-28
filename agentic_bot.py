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

    def _triage_query(self, user_query: str, model_name: str) -> List[str]:
        """PASS 1: Identify which skills are needed (Fast, specialized call)."""
        skill_descriptions = "\n".join([f"- {k}: {v['desc']}" for k, v in self.skills.items()])
        
        triage_prompt = f"""
Identify which skills match this query. 
Skills: {", ".join(self.skills.keys())}

Query: "{user_query}"
Output only the skill names:"""
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[{"role": "system", "content": "You are a specialized triage agent. Your ONLY job is to output a comma-separated list of skill names from the available list. NEVER provide explanations, thoughts, or greetings. If no skill applies, output only 'none'."},
                      {"role": "user", "content": triage_prompt}],
            temperature=0,
            max_tokens=100,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}}
        )
        
        raw_output = response.choices[0].message.content.lower().strip()
        print(f"DEBUG: Triage AI returned: '{raw_output}'")
        
        # Robust parsing: check if any skill key is present in the raw output
        found = []
        for skill_key in self.skills.keys():
            if skill_key in raw_output:
                found.append(skill_key)
        
        return found if found else ["none"]

    def _load_skills(self, skill_names: List[str]) -> str:
        """Load the full content of the selected skills."""
        context = ""
        for name in skill_names:
            file_path = self.skills[name]["file"]
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    context += f"\n\n--- DOCUMENT: {name} ---\n{f.read()}"
            except FileNotFoundError:
                continue
        return context

    def ask(self, user_query: str, model_name: str = "local-model", history: List[dict] = None):
        """High-Performance Triage RAG."""
        if history is None:
            history = []
            
        # 1. Token Management (32k limit)
        full_history_text = "".join([m["content"] for m in history])
        if self._estimate_tokens(full_history_text) > 32000:
            history = self._compress_history(history, model_name)

        # 2. Triage (Which documents do we need?)
        # Use context for triage if query is short
        contextual_query = user_query
        if len(history) >= 2:
            last_user_msg = history[-2]["content"] if history[-2]["role"] == "user" else ""
            contextual_query = f"{last_user_msg} -> {user_query}"
            
        needed_skills = self._triage_query(contextual_query, model_name)
        
        # 3. Read selected skills
        if not needed_skills or "none" in needed_skills:
            print("⚠️ No specific documentation matched. Loading general knowledge base.")
            context = self._load_skills(["fees_rates"])
        else:
            print(f"🔄 AI is reading documentation for: {', '.join(needed_skills)}")
            context = self._load_skills(needed_skills)

        # 4. Answer Generation
        system_prompt = f"""
You are the official Brastel Remit AI Support Assistant.
Your ONLY source of truth is the provided SOURCE DOCUMENTATION.

CRITICAL RULES:
1. STRICT GROUNDING: Use ONLY the provided SOURCE DOCUMENTATION to answer. If the answer is not there, ask the user to contact support at 0120-983-891.
2. NO HALLUCINATION: Never invent numbers or requirements.
3. CONCISENESS: Be brief and direct.
4. LANGUAGE: Match the user's language.
5. FOLLOW-UP QUESTIONS: At the end of your response, always provide 2-3 extremely concise follow-up questions (3-5 words) written FROM THE CUSTOMER'S PERSPECTIVE (e.g., "What are the fees?", "How to register?"). Format them exactly like this:
Questions:
- Question 1
- Question 2
- Question 3

--- SOURCE DOCUMENTATION ---
{context}
--- END OF SOURCE DOCUMENTATION ---
"""
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        if not history or history[-1]["content"] != user_query:
            messages.append({"role": "user", "content": user_query})

        response = self.client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.0,
            max_tokens=500,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}}
        )
        
        content = response.choices[0].message.content or ""
        
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
        "baseURL": "http://192.168.40.76:1234/v1",
        "apiKey": "omlx-z3phyzfx0gs0t2hy",
        "model": "qwen-3.5-4b"
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
