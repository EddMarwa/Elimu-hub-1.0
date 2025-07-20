import subprocess
import os

class LLMService:
    def __init__(self, model_path=None, llama_cpp_path=None, llm_name=None):
        self.model_path = model_path or os.environ.get("LLM_MODEL_PATH", "./models/mistral-7b.Q4_K_M.gguf")
        self.llama_cpp_path = llama_cpp_path or os.environ.get("LLAMA_CPP_PATH", "/usr/local/bin/llama.cpp")
        self.llm_name = llm_name or os.environ.get("LLM_NAME", "Mistral 7B")

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
        except Exception as e:
            return f"[LLM ERROR] {str(e)}" 