import requests
import os

class LLMService:
    def __init__(self, model="qwen/qwen-2.5-72b-instruct"):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.model = os.getenv("OPENROUTER_MODEL", model)
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.llm_name = os.getenv("LLM_NAME", "Qwen 2.5 72B")
        self.model_path = f"OpenRouter: {self.model}"

    def call_llm(self, prompt, max_tokens=512, temp=0.7):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",  # Required by OpenRouter
            "X-Title": "Elimu Hub AI"  # Optional: helps identify your app in OpenRouter dashboard
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant for educational content. Provide clear, accurate, and engaging responses to help with learning."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temp
        }
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"[LLM ERROR] {str(e)}"
