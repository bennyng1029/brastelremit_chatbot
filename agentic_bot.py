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
Analyze the user query and identify ALL relevant documentation skills needed to provide a 100% accurate answer.
Be inclusive: if a query might need information from multiple documents, list them all.
Return ONLY the skill names as a comma-separated list. If it is just a general greeting or non-Brastel question, return 'none'.

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

    def ask(self, user_query: str, model_name: str = "local-model", history: List[dict] = None):
        """Hybrid Agentic RAG: Triage -> Read-on-Demand -> Answer."""
        if history is None:
            history = []
            
        # 1. Triage (Which documents do we need?)
        contextual_query = user_query
        if len(history) >= 2:
            last_user_msg = history[-2]["content"] if history[-2]["role"] == "user" else ""
            contextual_query = f"{last_user_msg} -> {user_query}"
            
        needed_skills = self._triage_query(contextual_query, model_name)
        
        # 2. Read selected skills
        if not needed_skills or "none" in needed_skills:
            print("⚠️ No specific documentation matched. Loading general knowledge base for safety.")
            context = self._load_skills(["fees_rates"])
        else:
            print(f"🔄 AI is reading documentation for: {', '.join(needed_skills)}")
            context = self._load_skills(needed_skills)

        # 3. Token Management (32k limit)
        full_history_text = "".join([m["content"] for m in history])
        if self._estimate_tokens(full_history_text) > 32000:
            history = self._compress_history(history, model_name)

        # 4. Answer Generation
        system_prompt = f"""
You are the official Brastel Remit AI Support Assistant.
Your ONLY source of truth is the provided SOURCE DOCUMENTATION.

CRITICAL RULES:
1. STRICT GROUNDING: You MUST NOT use your own knowledge or training data to answer questions about fees, rates, limits, or procedures. If the exact answer is not in the SOURCE DOCUMENTATION below, you MUST state: "I'm sorry, I don't have the specific information for that. Please contact our support team at 0120-983-891 or visit our website."
2. NO HALLUCINATION: Never invent numbers, percentages, or dates.
3. ADMIT IGNORANCE: It is better to say "I don't know" or refer to support than to give a wrong answer.
4. CONCISENESS: Be brief and direct. Do not repeat the same information.
5. LANGUAGE: Match the user's language.
6. Tone: Professional and helpful.
7. FOLLOW-UP QUESTIONS: At the end of your response, always provide 2-3 extremely concise follow-up questions (maximum 3-5 words) written from the USER'S perspective (e.g., "Check rates", "How to register?", "Update my ID"). Format them exactly like this:
Questions:
- Follow up question 1
- Follow up question 2
- Follow up question 3

--- SOURCE DOCUMENTATION ---
{context}
--- END OF SOURCE DOCUMENTATION ---
"""
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        
        # Add current query if not already in history
        if not history or history[-1]["content"] != user_query:
            messages.append({"role": "user", "content": user_query})

        response = self.client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.0,
            max_tokens=500,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}}
        )
        
        msg_data = response.choices[0].message.model_dump()
        content = msg_data.get('content', '')
        
        # Clean up any residual tags
        content = re.sub(r'<thought>.*?</thought>', '', content, flags=re.DOTALL)
        content = re.sub(r'Thinking Process:.*?\n', '', content)
        
        # Extract Follow-up questions
        follow_ups = []
        if "Questions:" in content:
            parts = content.split("Questions:")
            answer = parts[0].strip()
            questions_part = parts[1].strip()
            
            # More robust parsing for different bullet styles
            for line in questions_part.split("\n"):
                line = line.strip()
                # Matches "- Question", "* Question", "1. Question", etc.
                match = re.match(r'^(?:[-*•]|\d+\.)\s*(.+)$', line)
                if match:
                    follow_ups.append(match.group(1).strip())
        else:
            answer = content.strip()

        return {
            "answer": answer,
            "follow_ups": follow_ups[:3] # Limit to 3
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
