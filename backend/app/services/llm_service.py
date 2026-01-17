from openai import OpenAI
import google.generativeai as genai
import cohere
import os
from typing import Optional, Dict
from dotenv import load_dotenv
import httpx

load_dotenv()

class LLMService:
    def __init__(self):
        # Initialize OpenAI only if API key is provided
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.openai_client = OpenAI(api_key=openai_key)
        else:
            self.openai_client = None
        
        # Initialize Google Gemini only if API key is provided
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            genai.configure(api_key=google_key)
        self.google_key = google_key
        
        # Initialize Cohere only if API key is provided
        cohere_key = os.getenv("COHERE_API_KEY")
        if cohere_key:
            self.cohere_client = cohere.Client(api_key=cohere_key)
        else:
            self.cohere_client = None
        
        self.serpapi_key = os.getenv("SERPAPI_API_KEY")
        self.brave_api_key = os.getenv("BRAVE_API_KEY")
    
    def generate_response_openai(self, query: str, context: Optional[str] = None, custom_prompt: Optional[str] = None, model: str = "gpt-3.5-turbo") -> str:
        """Generate response using OpenAI GPT"""
        if not self.openai_client:
            raise ValueError("OpenAI API key is not configured. Please set OPENAI_API_KEY environment variable.")
        
        messages = []
        
        # Build system prompt that includes BOTH custom prompt AND context
        system_content_parts = []
        
        if custom_prompt:
            system_content_parts.append(custom_prompt)
        else:
            system_content_parts.append("You are a helpful assistant.")
        
        if context:
            system_content_parts.append(f"\nUse the following context to answer the question. Answer based on this context:\n\n{context}")
        
        messages.append({"role": "system", "content": "\n".join(system_content_parts)})
        messages.append({"role": "user", "content": query})
        
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    def generate_response_gemini(self, query: str, context: Optional[str] = None, custom_prompt: Optional[str] = None, model: str = "gemini-pro") -> str:
        """Generate response using Google Gemini"""
        if not self.google_key:
            raise ValueError("Google API key is not configured. Please set GOOGLE_API_KEY environment variable.")
        
        gemini_model = genai.GenerativeModel(model)
        
        prompt_parts = []
        
        # Include custom prompt if provided
        if custom_prompt:
            prompt_parts.append(custom_prompt)
        
        # ALWAYS include context if available
        if context:
            prompt_parts.append(f"\nContext to use for answering:\n{context}\n")
        
        prompt_parts.append(f"Question: {query}\n\nAnswer based on the context above:")
        
        prompt = "\n".join(prompt_parts)
        
        response = gemini_model.generate_content(prompt)
        return response.text
    
    def generate_response_cohere(self, query: str, context: Optional[str] = None, custom_prompt: Optional[str] = None, model: str = "command-r-plus") -> str:
        """Generate response using Cohere"""
        if not self.cohere_client:
            raise ValueError("Cohere API key is not configured. Please set COHERE_API_KEY environment variable.")
        
        # Build preamble that includes BOTH custom prompt AND context
        preamble_parts = []
        
        if custom_prompt:
            preamble_parts.append(custom_prompt)
        else:
            preamble_parts.append("You are a helpful assistant.")
        
        if context:
            preamble_parts.append(f"\nUse the following context to answer questions:\n\n{context}")
        
        preamble = "\n".join(preamble_parts)
        
        response = self.cohere_client.chat(
            model=model,
            message=query,
            preamble=preamble,
            temperature=0.7
        )
        
        return response.text
    
    def web_search_serpapi(self, query: str) -> str:
        """Search the web using SerpAPI"""
        if not self.serpapi_key:
            return ""
        
        try:
            from serpapi import GoogleSearch
            
            params = {
                "q": query,
                "api_key": self.serpapi_key
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            # Extract top results
            web_results = []
            if "organic_results" in results:
                for result in results["organic_results"][:5]:
                    web_results.append(f"{result.get('title', '')}: {result.get('snippet', '')}")
            
            return "\n".join(web_results)
        except Exception as e:
            print(f"SerpAPI error: {str(e)}")
            return ""
    
    def web_search_brave(self, query: str) -> str:
        """Search the web using Brave Search API"""
        if not self.brave_api_key:
            return ""
        
        try:
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.brave_api_key
            }
            
            params = {
                "q": query,
                "count": 5
            }
            
            response = httpx.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params,
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            web_results = []
            if "web" in data and "results" in data["web"]:
                for result in data["web"]["results"]:
                    web_results.append(f"{result.get('title', '')}: {result.get('description', '')}")
            
            return "\n".join(web_results)
        except Exception as e:
            print(f"Brave Search error: {str(e)}")
            return ""
    
    def generate_with_web_search(self, query: str, llm_provider: str, context: Optional[str] = None, 
                                 custom_prompt: Optional[str] = None, web_search_provider: Optional[str] = None,
                                 model: Optional[str] = None) -> Dict:
        """Generate response with optional web search"""
        web_context = ""
        
        if web_search_provider:
            if web_search_provider == "serpapi":
                web_context = self.web_search_serpapi(query)
            elif web_search_provider == "brave":
                web_context = self.web_search_brave(query)
        
        # Combine contexts
        full_context = context
        if web_context:
            if full_context:
                full_context = f"{full_context}\n\nWeb Search Results:\n{web_context}"
            else:
                full_context = f"Web Search Results:\n{web_context}"
        
        # Generate response based on provider
        if llm_provider == "openai":
            response = self.generate_response_openai(
                query, 
                full_context, 
                custom_prompt,
                model=model or "gpt-3.5-turbo"
            )
        elif llm_provider == "gemini":
            response = self.generate_response_gemini(
                query, 
                full_context, 
                custom_prompt,
                model=model or "gemini-pro"
            )
        elif llm_provider == "cohere":
            response = self.generate_response_cohere(
                query, 
                full_context, 
                custom_prompt,
                model=model or "command-r-08-2024"
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}. Supported providers: openai, gemini, cohere")
        
        return {
            "response": response,
            "web_context_used": bool(web_context),
            "context_used": bool(context),
            "provider": llm_provider
        }
    
    def get_available_providers(self) -> list:
        """Return list of available LLM providers based on configured API keys"""
        providers = []
        if self.openai_client:
            providers.append("openai")
        if self.google_key:
            providers.append("gemini")
        if self.cohere_client:
            providers.append("cohere")
        return providers
    
    def is_provider_available(self, provider: str) -> bool:
        """Check if a specific provider is available"""
        return provider in self.get_available_providers()