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

    def _triage_query(self, user_query: str, model_name: str) -> List[str]:
        """PASS 1: Identify which skills are needed."""
        skill_descriptions = "\n".join([f"- {k}: {v['desc']}" for k, v in self.skills.items()])
        
        triage_prompt = f"""
Identify which documentation skills are needed to answer this user query.
Return ONLY the skill names as a comma-separated list. If none apply, return 'none'.

User Query: "{user_query}"

Available Skills:
{skill_descriptions}
"""
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[{"role": "system", "content": "You are a triage agent. Output only skill names."},
                      {"role": "user", "content": triage_prompt}],
            temperature=0,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}}
        )
        
        skills_found = response.choices[0].message.content.lower().strip().split(",")
        return [s.strip() for s in skills_found if s.strip() in self.skills]

    def _load_skills(self, skill_names: List[str]) -> str:
        """Load the full content of the selected skills."""
        context = ""
        for name in skill_names:
            file_path = self.skills[name]["file"]
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    context += f"\n\n--- DOCUMENT: {file_path} ---\n{f.read()}"
            except FileNotFoundError:
                continue
        return context

    def ask(self, user_query: str, model_name: str = "local-model"):
        """Hybrid Agentic RAG: Triage -> Read-on-Demand -> Answer."""
        
        # 1. Triage (Which documents do we need?)
        needed_skills = self._triage_query(user_query, model_name)
        
        # 2. Read selected skills
        if not needed_skills or "none" in needed_skills:
            context = "General assistance needed. Use available knowledge."
        else:
            print(f"🔄 AI is reading documentation for: {', '.join(needed_skills)}")
            context = self._load_skills(needed_skills)

        # 3. Answer Generation
        system_prompt = f"""
You are the official Brastel Remit AI Support Assistant.
Use the provided SOURCE DOCUMENTATION to answer the user accurately.

RULES:
1. Accuracy: Never hallucinate fees, limits, or requirements.
2. Grounding: If the answer is not in the source, ask them to contact support at 0120-983-891.
3. Language: Match the user's language.
4. Tone: Professional and helpful.

--- SOURCE DOCUMENTATION ---
{context}
--- END OF SOURCE DOCUMENTATION ---
"""
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "user", "content": user_query}],
            temperature=0.1,
            max_tokens=1000,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}}
        )
        
        msg_data = response.choices[0].message.model_dump()
        content = msg_data.get('content', '')
        
        # Clean up any residual tags
        content = re.sub(r'<thought>.*?</thought>', '', content, flags=re.DOTALL)
        content = re.sub(r'Thinking Process:.*?\n', '', content)
        
        return content.strip()

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
        print(bot.ask(q, CONFIG["model"]))
