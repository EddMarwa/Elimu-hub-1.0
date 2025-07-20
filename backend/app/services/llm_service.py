import subprocess
import os
from app.config import settings

class LLMService:
    def __init__(self, model_path=None, llama_cpp_path=None, llm_name=None):
        self.model_path = model_path or settings.LLM_MODEL_PATH
        self.llama_cpp_path = llama_cpp_path or settings.LLAMA_CPP_PATH
        self.llm_name = llm_name or settings.LLM_NAME

    def call_llm(self, prompt, max_tokens=512, temp=0.2):
        cmd = [
            self.llama_cpp_path,
            "-m", self.model_path,
            "-p", prompt,
            "--temp", str(temp),
            "-n", str(max_tokens)
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            result.check_returncode()
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return "[LLM ERROR] Request timed out"
        except subprocess.CalledProcessError as e:
            return f"[LLM ERROR] Process failed: {e.stderr}"
        except Exception as e:
            return f"[LLM ERROR] {str(e)}" 