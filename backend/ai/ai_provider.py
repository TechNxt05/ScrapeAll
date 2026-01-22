"""
Multi-AI Provider with automatic fallback
Priority: Groq -> Google Gemini -> HuggingFace -> OpenAI
"""
import os
from typing import Optional, List, Dict
from groq import Groq
import google.generativeai as genai
from huggingface_hub import InferenceClient
from openai import OpenAI

class AIProvider:
    def __init__(self):
        # Initialize all available providers
        self.groq_client = None
        self.gemini_model = None
        self.hf_client = None
        self.openai_client = None
        
        # Track which providers are available
        self.available_providers = []
        
        self._init_providers()
    
    def _init_providers(self):
        """Initialize all AI providers based on available API keys"""
        
        # 1. Groq (Primary - FREE)
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            try:
                self.groq_client = Groq(api_key=groq_key)
                self.available_providers.append("groq")
                print("✅ Groq initialized (Primary)")
            except Exception as e:
                print(f"⚠️ Groq initialization failed: {e}")
        
        # 2. Google Gemini (Backup - FREE)
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            try:
                genai.configure(api_key=google_key)
                self.gemini_model = None # Initialized on demand
                self.available_providers.append("gemini")
                print("✅ Google Gemini initialized (Backup)")
            except Exception as e:
                print(f"⚠️ Gemini initialization failed: {e}")
        
        # 3. HuggingFace (Tertiary - FREE)
        hf_key = os.getenv("HUGGINGFACE_API_KEY")
        if hf_key:
            try:
                self.hf_client = InferenceClient(token=hf_key)
                self.available_providers.append("huggingface")
                print("✅ HuggingFace initialized (Tertiary)")
            except Exception as e:
                print(f"⚠️ HuggingFace initialization failed: {e}")
        
        # 4. OpenAI (Emergency Fallback - PAID)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                self.openai_client = OpenAI(api_key=openai_key)
                self.available_providers.append("openai")
                print("✅ OpenAI initialized (Emergency Fallback)")
            except Exception as e:
                print(f"⚠️ OpenAI initialization failed: {e}")
        
        if not self.available_providers:
            raise Exception("❌ No AI providers available! Please add at least one API key.")
        
        print(f"🎯 Available AI providers: {', '.join(self.available_providers)}")
    
    def generate_completion(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.3
    ) -> str:
        """
        Generate completion with automatic fallback
        Tries providers in priority order until one succeeds
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        errors = []
        
        # Try each provider in order
        for provider in self.available_providers:
            try:
                if provider == "groq":
                    return self._groq_completion(messages, max_tokens, temperature)
                elif provider == "gemini":
                    return self._gemini_completion(prompt, system_prompt)
                elif provider == "huggingface":
                    return self._hf_completion(messages, max_tokens, temperature)
                elif provider == "openai":
                    return self._openai_completion(messages, max_tokens, temperature)
            except Exception as e:
                error_msg = f"{provider} failed: {str(e)}"
                errors.append(error_msg)
                print(f"⚠️ {error_msg}, trying next provider...")
                continue
        
        # All providers failed
        raise Exception(f"All AI providers failed: {'; '.join(errors)}")
    
    def _groq_completion(self, messages: List[Dict], max_tokens: int, temperature: float) -> str:
        """Groq API completion"""
        response = self.groq_client.chat.completions.create(
            # Updated to latest supported model
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def _gemini_completion(self, prompt: str, system_prompt: Optional[str]) -> str:
        """Google Gemini completion"""
        # Updated to pro model for better stability
        self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')
        
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        response = self.gemini_model.generate_content(full_prompt)
        return response.text
    
    def _hf_completion(self, messages: List[Dict], max_tokens: int, temperature: float) -> str:
        """HuggingFace completion"""
        # Updated to Llama 3 8B which is usually available on free tier
        response = self.hf_client.chat_completion(
            messages=messages,
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def _openai_completion(self, messages: List[Dict], max_tokens: int, temperature: float) -> str:
        """OpenAI completion (fallback)"""
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def get_active_provider(self) -> str:
        """Return the currently active (first available) provider"""
        return self.available_providers[0] if self.available_providers else "none"

# Global instance
ai_provider = AIProvider()
