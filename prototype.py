import json
import os

class BrastelChatbot:
    def __init__(self, kb_path):
        with open(kb_path, 'r') as f:
            self.kb = json.load(f)
        
    def calculate_transfer(self, amount, currency):
        """Calculates fee and receiving amount based on KB."""
        if currency not in self.kb['exchange_rates']:
            return f"Sorry, we don't support transfers to {currency} yet."
        
        fee = 0
        for tier in self.kb['fees']:
            if tier['min'] <= amount <= tier['max']:
                fee = tier['fee']
                break
        
        if fee == 0 and amount > 800000:
            return "The maximum transfer limit is 800,000 JPY."
        
        rate = self.kb['exchange_rates'][currency]
        receiving_amount = (amount - fee) * rate
        
        return {
            "send_amount": amount,
            "fee": fee,
            "net_amount": amount - fee,
            "rate": rate,
            "receiving_amount": round(receiving_amount, 2),
            "currency": currency
        }

    def get_faq_answer(self, query):
        """Simulates an LLM/RAG retrieval for FAQ."""
        # In a real app, this would use an LLM with the KB as context
        query = query.lower()
        for item in self.kb['faq']:
            if any(word in query for word in item['question'].lower().split()):
                return item['answer']
        
        return "I'm not sure about that. Would you like me to connect you to a live agent?"

    def run_cli(self):
        print("=== Brastel Remit AI Assistant Prototype ===")
        print("Type 'calc' for rates, 'faq' for questions, or 'exit' to quit.")
        
        while True:
            user_input = input("\nYou: ").strip().lower()
            
            if user_input == 'exit':
                break
            elif 'calc' in user_input or 'how much' in user_input:
                try:
                    amt = int(input("Amount in JPY: "))
                    curr = input("Target Currency (PHP, VND, IDR, etc.): ").upper()
                    result = self.calculate_transfer(amt, curr)
                    if isinstance(result, str):
                        print(f"Bot: {result}")
                    else:
                        print(f"Bot: For {amt} JPY, the fee is {result['fee']} JPY.")
                        print(f"Bot: Your recipient will receive approximately {result['receiving_amount']} {result['currency']}.")
                except ValueError:
                    print("Bot: Please enter a valid number for the amount.")
            else:
                answer = self.get_faq_answer(user_input)
                print(f"Bot: {answer}")

if __name__ == "__main__":
    bot = BrastelChatbot('knowledge/knowledge_base.json')
    bot.run_cli()
