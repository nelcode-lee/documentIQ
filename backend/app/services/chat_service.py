"""Chat service for handling RAG queries with OpenAI API."""

from openai import OpenAI
from app.config import settings
from typing import List, Dict, Optional
from app.services.vector_store import VectorStoreManager
from app.services.embedding_service import EmbeddingService
from app.services.cache_service import cache_service
import asyncio


class ChatService:
    """Service to handle RAG queries."""
    
    def __init__(self):
        """Initialize services."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.vector_store = VectorStoreManager()
        self.embedding_service = EmbeddingService()
        self.use_cache = settings.enable_query_cache
        self.system_prompt = """You are an AI assistant specializing in company technical standards. 
Use the provided context from the knowledge base to answer questions accurately. 
If the answer isn't in the context, say so clearly.
Always cite the source documents used when available.
Format your responses clearly and professionally."""
    
    def _get_system_prompt(self, language: str = "en") -> str:
        """Get system prompt in the specified language."""
        prompts = {
            "en": """You are an AI assistant specializing in company technical standards. 
Use the provided context from the knowledge base to answer questions accurately. 
If the answer isn't in the context, say so clearly.
Always cite the source documents used when available.
Format your responses clearly and professionally.

CRITICAL LANGUAGE REQUIREMENT: You MUST respond ONLY in English. Every single word, sentence, and paragraph must be in English. Do NOT use any other language under any circumstances.""",
            "pl": """Jesteś asystentem AI specjalizującym się w standardach technicznych firmy.
Używaj podanego kontekstu z bazy wiedzy, aby odpowiadać na pytania dokładnie.
Jeśli odpowiedzi nie ma w kontekście, powiedz to wyraźnie.
Zawsze cytuj używane dokumenty źródłowe, gdy są dostępne.
Formatuj swoje odpowiedzi jasno i profesjonalnie.

KRYTYCZNY WYMÓG JĘZYKOWY: Musisz odpowiadać TYLKO I WYŁĄCZNIE w języku polskim. Każde słowo, zdanie i akapit musi być po polsku. Jeśli kontekst jest w innym języku, musisz go przetłumaczyć i wyjaśnić po polsku. NIGDY nie używaj angielskiego ani żadnego innego języka.""",
            "ro": """Ești un asistent AI specializat în standarde tehnice ale companiei.
Folosește contextul furnizat din baza de cunoștințe pentru a răspunde la întrebări cu precizie.
Dacă răspunsul nu se află în context, spune acest lucru clar.
Citează întotdeauna documentele sursă utilizate când sunt disponibile.
Formatează răspunsurile tale clar și profesional.

CERINȚĂ CRITICĂ DE LIMBĂ: Trebuie să răspunzi DOAR ȘI EXCLUSIV în limba română. Fiecare cuvânt, propoziție și paragraf trebuie să fie în română. Dacă contextul este într-o altă limbă, trebuie să-l traduci și să-l explici în română. NICIODATĂ nu folosi engleza sau orice altă limbă."""
        }
        return prompts.get(language, prompts["en"])
    
    async def chat(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        language: str = "en",
        top_k: int = 7,  # Optimized: reduced from 10 for faster processing (still enough context)
        temperature: float = 0.7,
        max_tokens: int = 700  # Optimized: reduced from 1000 for faster response generation
    ) -> Dict:
        """
        Handle a chat query with RAG.
        
        Args:
            query: User's question
            conversation_id: Optional conversation ID for context
            language: Language code ("en", "pl", "ro") for response language
            top_k: Number of relevant chunks to retrieve
            temperature: Model temperature (0-1)
            max_tokens: Maximum tokens in response
            
        Returns:
            Dictionary with response, sources, and conversation_id
        """
        try:
            print(f"[DEBUG] ChatService.chat() - Language: {language}, Query: {query[:50]}...")
            
            # Check cache first (if enabled)
            if self.use_cache:
                cached_response = cache_service.get_query_response(
                    query=query,
                    language=language,
                    top_k=top_k
                )
                if cached_response is not None:
                    print(f"[CACHE HIT] Query response cached: {query[:50]}...")
                    return cached_response
            
            print(f"[CACHE MISS] Generating new response for: {query[:50]}...")
            
            # Generate embedding for query (run in executor to avoid blocking event loop)
            loop = asyncio.get_event_loop()
            query_embedding = await loop.run_in_executor(
                None,
                self.embedding_service.generate_embedding,
                query
            )
            
            # Search for relevant documents (hybrid search: vector + keyword for better accuracy)
            search_results = await self.vector_store.search(
                query_embedding=query_embedding,
                top_k=top_k,
                query_text=query  # Use query text for hybrid search to improve relevance
            )
            
            # Build context from search results
            context_chunks = []
            sources = []
            
            for result in search_results:
                context_chunks.append(result.get('content', ''))
                if 'title' in result or 'documentId' in result:
                    source_name = result.get('title', result.get('documentId', 'Unknown'))
                    if source_name not in sources:
                        sources.append(source_name)
            
            # Combine context (optimize: limit total context length)
            context = "\n\n".join(context_chunks)
            
            # Truncate context if too long (prevents excessive token usage)
            # Each 500-token chunk = ~375 words, 7 chunks max = ~2625 words = ~3500 tokens
            # Limit to ~4000 tokens to leave room for prompt + response
            if len(context) > 16000:  # ~4000 tokens (4 chars per token estimate)
                context_chunks_limited = context_chunks[:6]  # Use top 6 chunks if too long
                context = "\n\n".join(context_chunks_limited)
            
            # Build messages for OpenAI with language-specific prompt
            system_prompt = self._get_system_prompt(language)
            
            # Add explicit language instruction based on selected language
            # Make it very clear and prominent - place at the END for emphasis
            lang_instruction = ""
            if language == "pl":
                lang_instruction = "\n\n" + "="*50 + "\n⚠️ KRYTYCZNE INSTRUKCJE JĘZYKOWE ⚠️\n" + "="*50 + "\nOdpowiedz TYLKO I WYŁĄCZNIE w języku polskim.\n- Wszystkie słowa, zdania i cała odpowiedź MUSI być po polsku\n- Jeśli kontekst z bazy wiedzy jest po angielsku, PRZETŁUMACZ go na polski w swojej odpowiedzi\n- NIE używaj angielskiego ani żadnego innego języka\n- Każde zdanie musi być napisane po polsku\n" + "="*50
            elif language == "ro":
                lang_instruction = "\n\n" + "="*50 + "\n⚠️ INSTRUCȚIUNI CRITICE DE LIMBĂ ⚠️\n" + "="*50 + "\nRăspunde DOAR ȘI EXCLUSIV în limba română.\n- Toate cuvintele, propozițiile și întregul răspuns TREBUIE să fie în română\n- Dacă contextul din baza de cunoștințe este în engleză, TRADUCE-L în română în răspunsul tău\n- NU folosi engleză sau orice altă limbă\n- Fiecare propoziție trebuie să fie scrisă în română\n" + "="*50
            elif language == "en":
                lang_instruction = "\n\n" + "="*50 + "\n⚠️ CRITICAL LANGUAGE INSTRUCTIONS ⚠️\n" + "="*50 + "\nRespond ONLY in English.\n- Every word, sentence, and the entire response MUST be in English\n- If the context from the knowledge base is in another language, TRANSLATE it to English in your response\n- Do NOT use any other language\n- Every sentence must be written in English\n" + "="*50
            
            user_content = f"Context from knowledge base (may be in any language):\n\n{context}\n\n\nUser question: {query}{lang_instruction}"
            
            # Build messages - add language as a separate system message for emphasis
            language_requirement = ""
            if language == "pl":
                language_requirement = "ODPOWIADAJ TYLKO PO POLSKU. Wszystko w języku polskim."
            elif language == "ro":
                language_requirement = "RĂSPUNDE DOAR ÎN ROMÂNĂ. Totul în limba română."
            elif language == "en":
                language_requirement = "RESPOND ONLY IN ENGLISH. Everything in English."
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "system", "content": f"LANGUAGE REQUIREMENT: {language_requirement}"},
                {"role": "user", "content": user_content}
            ]
            
            print(f"[DEBUG] Sending to OpenAI with language={language}, system prompts={len(messages)} messages")
            
            # Get response from OpenAI (run in executor to avoid blocking event loop)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=30.0  # Add timeout to avoid hanging
                )
            )
            
            assistant_message = response.choices[0].message.content
            
            result = {
                "response": assistant_message,
                "sources": sources,
                "conversation_id": conversation_id or "new",
            }
            
            # Cache the response (if enabled)
            if self.use_cache:
                cache_service.set_query_response(
                    query=query,
                    response=result,
                    language=language,
                    top_k=top_k,
                    ttl=settings.cache_query_ttl
                )
            
            return result
            
        except Exception as e:
            print(f"Error in chat service: {e}")
            import traceback
            traceback.print_exc()
            raise
