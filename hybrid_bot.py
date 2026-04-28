import os
import openai
import re
from typing import List

class BrastelHybridBot:
    def __init__(self, base_url: str, api_key: str, model_name: str):
        self.client = openai.OpenAI(base_url=base_url, api_key=api_key)
        self.model_name = model_name
        
        # Define the available "Skills" (Read-on-Demand files)
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

    def _triage_query(self, user_query: str) -> List[str]:
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
            model=self.model_name,
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
            with open(file_path, "r", encoding="utf-8") as f:
                context += f"\n\n--- DOCUMENT: {file_path} ---\n{f.read()}"
        return context

    def ask(self, user_query: str):
        """PASS 2: Read the selected skills and answer."""
        # 1. Triage
        needed_skills = self._triage_query(user_query)
        
        if not needed_skills or "none" in needed_skills:
            # Fallback if no specific skill is found
            context = "No specific documentation found for this query."
        else:
            # 2. Read on Demand
            print(f"🔄 Loading Skills: {', '.join(needed_skills)}...")
            context = self._load_skills(needed_skills)

        # 3. Answer Generation
        system_prompt = f"""
You are the Brastel AI Assistant. Use the provided SOURCE DOCUMENTATION to answer the user.
Answer accurately and professionally.

--- SOURCE DOCUMENTATION ---
{context}
--- END OF SOURCE DOCUMENTATION ---
"""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "user", "content": user_query}],
            temperature=0.1,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}}
        )
        
        return response.choices[0].message.content

if __name__ == "__main__":
    # CONFIGURATION
    CONFIG = {
        "baseURL": "http://192.168.10.83:8000/v1",
        "apiKey": "omlx-z3phyzfx0gs0t2hy",
        "model": "Qwen3.5-4B-MLX-8bit"
    }

    bot = BrastelHybridBot(CONFIG["baseURL"], CONFIG["apiKey"], CONFIG["model"])
    
    print("\n🚀 Brastel Hybrid Agentic RAG PoC is Ready")
    print("This bot 'Reads on Demand' from a library of 8 specialized files.")
    print("-" * 60)
    
    while True:
        q = input("\nYou: ")
        if q.lower() in ['exit', 'quit']: break
        
        print("Bot is thinking (Triaging query)...")
        answer = bot.ask(q)
        print(f"\nAssistant: {answer}")
