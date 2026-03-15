
class APITracker:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(APITracker, cls).__new__(cls)
            cls._instance.counts = {
                "Gemini (Vision)": 0,
                "Gemini (Text)": 0,
                "Groq": 0,
                "DuckDuckGo": 0
            }
            # Estimated Cost per Call (assuming avg tokens, checking Free Tier possibility)
            # Gemini 1.5 Flash is effectively free/very cheap. Pro is paid.
            # Let's assume a "Pay-as-you-go" worst case scenario for awareness.
            # 1 call ~= 1000 in / 1000 out tokens approx.
            cls._instance.prices = {
                "Gemini (Vision)": 0.002, # $0.002 per image approx
                "Gemini (Text)": 0.0005,  # Flash is cheap, Pro is higher. Avg $0.0005
                "Groq": 0.001,            # Llama 70B approx
                "DuckDuckGo": 0.0         # Free
            }
        return cls._instance

    def increment(self, service_name):
        if service_name in self.counts:
            self.counts[service_name] += 1
        else:
            self.counts[service_name] = 1

    def get_report(self):
        total_usd = 0.0
        report = "--- 💰 API Cost Estimate (Session) ---\n"
        
        for service, count in self.counts.items():
            cost = count * self.prices.get(service, 0)
            total_usd += cost
            report += f"{service}: {count} calls (~${cost:.4f})\n"
            
        total_jpy = total_usd * 150 # $1 = 150 JPY
        
        report += "--------------------------------------\n"
        report += f"Total Est. Cost: ${total_usd:.4f} (approx. ¥{total_jpy:.2f})\n"
        report += "※あくまで目安です。無料枠(Free Tier)適用内であれば ¥0 です。\n"
        return report
