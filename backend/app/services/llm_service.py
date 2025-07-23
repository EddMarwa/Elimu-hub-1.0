
import requests
import os

class LLMService:
    def __init__(self, model=None, provider="huggingface"):
        self.provider = provider
        
        if provider == "openrouter":
            self.api_key = os.getenv("OPENROUTER_API_KEY", "")
            self.model = model or os.getenv("OPENROUTER_MODEL", "qwen/qwen-2.5-72b-instruct")
            self.api_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1") + "/chat/completions"
            self.site_url = os.getenv("SITE_URL", "http://localhost:3000")
            self.app_name = os.getenv("APP_NAME", "Elimu Hub AI")
        elif provider == "huggingface":
            self.api_key = os.getenv("HUGGINGFACE_API_KEY", "")
            self.model = model or os.getenv("HUGGINGFACE_MODEL", "HuggingFaceH4/zephyr-7b-beta")
            self.api_url = f"{os.getenv('HUGGINGFACE_BASE_URL', 'https://api-inference.huggingface.co/models')}/{self.model}"
        else:  # fallback to groq
            self.api_key = os.getenv("GROQ_API_KEY", "")
            self.model = model or os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
            self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def call_llm(self, prompt, max_tokens=512, temp=0.7, system_message=None):
        if not self.api_key:
            return f"[ERROR] API key not configured. Please set {self.provider.upper()}_API_KEY in environment variables."
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            if self.provider == "huggingface":
                # Hugging Face Inference API format
                # Combine system message and prompt for Hugging Face
                full_prompt = prompt
                if system_message:
                    full_prompt = f"<|system|>\n{system_message}\n<|user|>\n{prompt}\n<|assistant|>\n"
                else:
                    full_prompt = f"<|system|>\nYou are a helpful AI assistant for educational purposes. Provide clear, accurate, and educational responses.\n<|user|>\n{prompt}\n<|assistant|>\n"
                
                payload = {
                    "inputs": full_prompt,
                    "parameters": {
                        "max_new_tokens": max_tokens,
                        "temperature": temp,
                        "return_full_text": False
                    }
                }
                
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
                response.raise_for_status()
                data = response.json()
                
                # Handle Hugging Face response format
                if isinstance(data, list) and len(data) > 0:
                    return data[0].get("generated_text", "").strip()
                elif isinstance(data, dict):
                    return data.get("generated_text", "").strip()
                else:
                    return "[ERROR] Unexpected response format from Hugging Face API"
                    
            else:
                # OpenAI-compatible format for OpenRouter and Groq
                # Add OpenRouter specific headers
                if self.provider == "openrouter":
                    headers.update({
                        "HTTP-Referer": self.site_url,
                        "X-Title": self.app_name
                    })
                
                # Prepare messages
                messages = []
                if system_message:
                    messages.append({"role": "system", "content": system_message})
                else:
                    messages.append({"role": "system", "content": "You are a helpful AI assistant for educational purposes. Provide clear, accurate, and educational responses."})
                
                messages.append({"role": "user", "content": prompt})
                
                payload = {
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temp
                }
                
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
                
        except requests.exceptions.RequestException as e:
            error_msg = f"[LLM ERROR] Request failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    if self.provider == "huggingface":
                        error_msg += f" - {error_detail.get('error', 'Unknown error')}"
                    else:
                        error_msg += f" - {error_detail.get('error', {}).get('message', 'Unknown error')}"
                except:
                    error_msg += f" - HTTP {e.response.status_code}"
            return error_msg
        except Exception as e:
            return f"[LLM ERROR] Unexpected error: {str(e)}"
    
    def call_llm_with_context(self, question, context_documents=None, max_tokens=1024, temp=0.7):
        """Call LLM with retrieved context from knowledge base"""
        system_message = """You are an intelligent educational assistant for Elimu Hub AI. Your role is to help students learn by providing accurate, clear, and educational responses.

Guidelines:
1. Use the provided context documents to answer questions when available
2. If context is provided, base your answer primarily on that information
3. If no relevant context is found, use your general knowledge but clearly state this
4. Always provide educational value and encourage learning
5. Break down complex concepts into understandable parts
6. Use examples when helpful
7. Be encouraging and supportive in your tone"""

        if context_documents and len(context_documents) > 0:
            context_text = "\n\n".join([doc.get('content', '') for doc in context_documents[:3]])
            prompt = f"""Based on the following educational content, please answer the student's question:

CONTEXT:
{context_text}

STUDENT'S QUESTION: {question}

Please provide a comprehensive, educational answer based on the context provided. If the context doesn't fully address the question, supplement with your knowledge while clearly indicating what comes from the provided materials versus your general knowledge."""
        else:
            prompt = f"""Please help answer this educational question: {question}

Since no specific course materials were found, please provide a helpful educational response using your knowledge. Encourage the student and provide clear explanations."""

        return self.call_llm(prompt, max_tokens=max_tokens, temp=temp, system_message=system_message) 