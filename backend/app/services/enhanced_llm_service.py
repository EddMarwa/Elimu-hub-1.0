"""
Enhanced LLM Service with Response Tailoring Options
This module provides advanced customization for LLM responses
"""

import os
import json
from typing import Optional, Dict, Any, List
from enum import Enum
import requests

class ResponseTone(Enum):
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    ACADEMIC = "academic"
    CONVERSATIONAL = "conversational"
    ENCOURAGING = "encouraging"
    DETAILED = "detailed"
    CONCISE = "concise"

class ResponseFormat(Enum):
    PARAGRAPH = "paragraph"
    BULLET_POINTS = "bullet_points"
    NUMBERED_LIST = "numbered_list"
    Q_AND_A = "q_and_a"
    STEP_BY_STEP = "step_by_step"
    SUMMARY = "summary"
    EXPLANATION = "explanation"

class AudienceLevel(Enum):
    ELEMENTARY = "elementary"
    MIDDLE_SCHOOL = "middle_school"
    HIGH_SCHOOL = "high_school"
    COLLEGE = "college"
    ADULT = "adult"
    EXPERT = "expert"

class EnhancedLLMService:
    def __init__(self, model=None, provider="groq"):
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
    
    def _build_system_message(
        self,
        tone: ResponseTone = ResponseTone.FRIENDLY,
        format_type: ResponseFormat = ResponseFormat.PARAGRAPH,
        audience_level: AudienceLevel = AudienceLevel.HIGH_SCHOOL,
        subject_area: Optional[str] = None,
        custom_instructions: Optional[str] = None,
        persona: Optional[str] = None
    ) -> str:
        """Build a customized system message based on response requirements"""
        
        # Base persona
        if persona:
            base_persona = persona
        else:
            base_persona = "You are an intelligent educational assistant for Elimu Hub AI"
        
        # Tone instructions
        tone_instructions = {
            ResponseTone.PROFESSIONAL: "Maintain a professional, formal tone while being helpful and informative.",
            ResponseTone.FRIENDLY: "Use a warm, friendly, and approachable tone that makes learning enjoyable.",
            ResponseTone.ACADEMIC: "Adopt a scholarly, precise tone with proper academic language and terminology.",
            ResponseTone.CONVERSATIONAL: "Write in a natural, conversational style as if talking to a friend.",
            ResponseTone.ENCOURAGING: "Be highly encouraging, supportive, and motivating in your responses.",
            ResponseTone.DETAILED: "Provide comprehensive, thorough explanations with extensive detail.",
            ResponseTone.CONCISE: "Keep responses brief, direct, and to the point while being helpful."
        }
        
        # Format instructions
        format_instructions = {
            ResponseFormat.PARAGRAPH: "Structure your response in clear, well-organized paragraphs.",
            ResponseFormat.BULLET_POINTS: "Format your response using bullet points for easy scanning.",
            ResponseFormat.NUMBERED_LIST: "Present information as a numbered list when appropriate.",
            ResponseFormat.Q_AND_A: "Structure as questions and answers to address key points.",
            ResponseFormat.STEP_BY_STEP: "Break down complex topics into clear, sequential steps.",
            ResponseFormat.SUMMARY: "Provide concise summaries of key concepts and main points.",
            ResponseFormat.EXPLANATION: "Focus on detailed explanations with examples and context."
        }
        
        # Audience level instructions
        audience_instructions = {
            AudienceLevel.ELEMENTARY: "Use simple language, basic concepts, and relatable examples suitable for elementary students.",
            AudienceLevel.MIDDLE_SCHOOL: "Adapt language for middle school level with moderate complexity and age-appropriate examples.",
            AudienceLevel.HIGH_SCHOOL: "Use high school level vocabulary and concepts with appropriate academic rigor.",
            AudienceLevel.COLLEGE: "Employ college-level language, advanced concepts, and sophisticated analysis.",
            AudienceLevel.ADULT: "Use professional language suitable for adult learners returning to education.",
            AudienceLevel.EXPERT: "Assume advanced knowledge and use technical terminology appropriate for experts."
        }
        
        system_message = f"""{base_persona}.

TONE: {tone_instructions.get(tone, tone_instructions[ResponseTone.FRIENDLY])}

FORMAT: {format_instructions.get(format_type, format_instructions[ResponseFormat.PARAGRAPH])}

AUDIENCE: {audience_instructions.get(audience_level, audience_instructions[AudienceLevel.HIGH_SCHOOL])}"""

        if subject_area:
            system_message += f"\n\nSUBJECT EXPERTISE: You specialize in {subject_area} and should provide subject-specific insights and examples."
        
        if custom_instructions:
            system_message += f"\n\nADDITIONAL INSTRUCTIONS: {custom_instructions}"
        
        system_message += """

EDUCATIONAL GUIDELINES:
1. Always provide accurate, helpful information
2. Use examples and analogies when beneficial
3. Encourage critical thinking and further exploration
4. Be patient and understanding of different learning styles
5. Adapt complexity based on the apparent understanding level
6. Provide sources or suggest further reading when appropriate"""
        
        return system_message

    def call_llm_tailored(
        self,
        prompt: str,
        tone: ResponseTone = ResponseTone.FRIENDLY,
        format_type: ResponseFormat = ResponseFormat.PARAGRAPH,
        audience_level: AudienceLevel = AudienceLevel.HIGH_SCHOOL,
        subject_area: Optional[str] = None,
        custom_instructions: Optional[str] = None,
        persona: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
        context_documents: Optional[List[Dict]] = None
    ) -> str:
        """
        Generate a tailored LLM response based on specific requirements
        
        Args:
            prompt: The user's question or prompt
            tone: Desired response tone
            format_type: Desired response format
            audience_level: Target audience education level
            subject_area: Subject specialization
            custom_instructions: Additional custom instructions
            persona: Custom persona override
            max_tokens: Maximum response length
            temperature: Response creativity (0.1-2.0)
            context_documents: Relevant documents for RAG
        
        Returns:
            Tailored LLM response
        """
        
        # Build customized system message
        system_message = self._build_system_message(
            tone=tone,
            format_type=format_type,
            audience_level=audience_level,
            subject_area=subject_area,
            custom_instructions=custom_instructions,
            persona=persona
        )
        
        # Enhance prompt with context if provided
        enhanced_prompt = prompt
        if context_documents and len(context_documents) > 0:
            context_text = "\n\n".join([doc.get('content', '') for doc in context_documents[:3]])
            enhanced_prompt = f"""Based on the following educational content, please answer the question:

CONTEXT:
{context_text}

QUESTION: {prompt}

Please provide a comprehensive answer based on the context provided."""
        
        return self._call_llm_api(enhanced_prompt, system_message, max_tokens, temperature)
    
    def _call_llm_api(self, prompt: str, system_message: str, max_tokens: int, temperature: float) -> str:
        """Internal method to call the LLM API"""
        if not self.api_key:
            return f"[ERROR] API key not configured. Please set {self.provider.upper()}_API_KEY in environment variables."
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            if self.provider == "huggingface":
                # Hugging Face format
                full_prompt = f"<|system|>\n{system_message}\n<|user|>\n{prompt}\n<|assistant|>\n"
                payload = {
                    "inputs": full_prompt,
                    "parameters": {
                        "max_new_tokens": max_tokens,
                        "temperature": temperature,
                        "return_full_text": False
                    }
                }
                
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
                response.raise_for_status()
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0:
                    return data[0].get("generated_text", "").strip()
                elif isinstance(data, dict):
                    return data.get("generated_text", "").strip()
                else:
                    return "[ERROR] Unexpected response format from Hugging Face API"
                    
            else:
                # OpenAI-compatible format
                if self.provider == "openrouter":
                    headers.update({
                        "HTTP-Referer": self.site_url,
                        "X-Title": self.app_name
                    })
                
                messages = [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ]
                
                payload = {
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature
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

# Convenience functions for common use cases
def create_student_tutor_response(prompt: str, subject: str, grade_level: str = "high_school") -> str:
    """Create a response tailored for student tutoring"""
    llm = EnhancedLLMService()
    audience_map = {
        "elementary": AudienceLevel.ELEMENTARY,
        "middle_school": AudienceLevel.MIDDLE_SCHOOL,
        "high_school": AudienceLevel.HIGH_SCHOOL,
        "college": AudienceLevel.COLLEGE
    }
    
    return llm.call_llm_tailored(
        prompt=prompt,
        tone=ResponseTone.ENCOURAGING,
        format_type=ResponseFormat.EXPLANATION,
        audience_level=audience_map.get(grade_level, AudienceLevel.HIGH_SCHOOL),
        subject_area=subject,
        custom_instructions="Focus on helping the student understand concepts clearly and encourage learning."
    )

def create_professional_summary(prompt: str, subject: str) -> str:
    """Create a professional summary response"""
    llm = EnhancedLLMService()
    return llm.call_llm_tailored(
        prompt=prompt,
        tone=ResponseTone.PROFESSIONAL,
        format_type=ResponseFormat.SUMMARY,
        audience_level=AudienceLevel.ADULT,
        subject_area=subject
    )

def create_step_by_step_guide(prompt: str, subject: str) -> str:
    """Create a step-by-step instructional response"""
    llm = EnhancedLLMService()
    return llm.call_llm_tailored(
        prompt=prompt,
        tone=ResponseTone.FRIENDLY,
        format_type=ResponseFormat.STEP_BY_STEP,
        audience_level=AudienceLevel.HIGH_SCHOOL,
        subject_area=subject,
        custom_instructions="Break down complex processes into clear, actionable steps with examples."
    )
