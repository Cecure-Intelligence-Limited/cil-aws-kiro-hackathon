"""
Hugging Face Inference API Client with retry logic and error handling
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
import aiohttp
import structlog
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

from config import settings

logger = structlog.get_logger(__name__)


class HuggingFaceAPIError(Exception):
    """Custom exception for Hugging Face API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class HuggingFaceClient:
    """
    Async client for Hugging Face Inference API with retry logic
    """
    
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or settings.HF_API_TOKEN
        self.base_url = settings.HF_API_URL
        self.timeout = aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT)
        
        if not self.api_token:
            logger.warning("No Hugging Face API token provided. Some features may not work.")
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            headers=self._get_headers()
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, 'session'):
            await self.session.close()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Aura-Desktop-Assistant/1.0.0"
        }
        
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        
        return headers
    
    @retry(
        stop=stop_after_attempt(settings.MAX_RETRIES),
        wait=wait_exponential(multiplier=settings.RETRY_DELAY, min=1, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        before_sleep=before_sleep_log(logger, "WARNING")
    )
    async def _make_request(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        
        logger.info("Making HF API request", url=url, payload_keys=list(payload.keys()))
        
        try:
            async with self.session.post(url, json=payload) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    logger.info("HF API request successful", status=response.status)
                    return response_data
                
                elif response.status == 503:
                    # Model is loading, wait and retry
                    estimated_time = response_data.get("estimated_time", 20)
                    logger.info("Model is loading, waiting", estimated_time=estimated_time)
                    await asyncio.sleep(min(estimated_time, 60))  # Cap at 60 seconds
                    raise aiohttp.ClientError("Model loading, retrying")
                
                else:
                    error_msg = response_data.get("error", f"HTTP {response.status}")
                    logger.error("HF API request failed", 
                               status=response.status, 
                               error=error_msg,
                               response_data=response_data)
                    
                    raise HuggingFaceAPIError(
                        message=error_msg,
                        status_code=response.status,
                        response_data=response_data
                    )
                    
        except aiohttp.ClientError as e:
            logger.error("HTTP client error", error=str(e))
            raise
        except asyncio.TimeoutError as e:
            logger.error("Request timeout", error=str(e))
            raise
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON response", error=str(e))
            raise HuggingFaceAPIError("Invalid JSON response from API")
    
    async def summarize_text(
        self, 
        text: str, 
        model: Optional[str] = None,
        max_length: Optional[int] = None,
        min_length: Optional[int] = None
    ) -> str:
        """
        Summarize text using Hugging Face summarization model
        
        Args:
            text: Text to summarize
            model: Model name (defaults to configured model)
            max_length: Maximum summary length
            min_length: Minimum summary length
            
        Returns:
            Summarized text
        """
        
        model = model or settings.HF_SUMMARIZATION_MODEL
        url = f"{self.base_url}/{model}"
        
        # Prepare payload
        payload = {
            "inputs": text,
            "parameters": {}
        }
        
        if max_length:
            payload["parameters"]["max_length"] = max_length
        if min_length:
            payload["parameters"]["min_length"] = min_length
        
        logger.info("Requesting text summarization", 
                   model=model, 
                   text_length=len(text),
                   max_length=max_length,
                   min_length=min_length)
        
        try:
            response_data = await self._make_request(url, payload)
            
            # Extract summary from response
            if isinstance(response_data, list) and len(response_data) > 0:
                summary = response_data[0].get("summary_text", "")
                logger.info("Text summarization completed", 
                           original_length=len(text),
                           summary_length=len(summary))
                return summary
            else:
                raise HuggingFaceAPIError("Unexpected response format for summarization")
                
        except Exception as e:
            logger.error("Text summarization failed", error=str(e))
            raise
    
    async def answer_question(
        self, 
        question: str, 
        context: str, 
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Answer question based on context using QA model
        
        Args:
            question: Question to answer
            context: Context text
            model: Model name (defaults to configured model)
            
        Returns:
            Dictionary with answer, score, start, end
        """
        
        model = model or settings.HF_QA_MODEL
        url = f"{self.base_url}/{model}"
        
        payload = {
            "inputs": {
                "question": question,
                "context": context
            }
        }
        
        logger.info("Requesting question answering", 
                   model=model,
                   question_length=len(question),
                   context_length=len(context))
        
        try:
            response_data = await self._make_request(url, payload)
            
            logger.info("Question answering completed", 
                       answer=response_data.get("answer", "")[:100],
                       score=response_data.get("score", 0))
            
            return response_data
            
        except Exception as e:
            logger.error("Question answering failed", error=str(e))
            raise
    
    async def generate_bullet_summary(self, text: str) -> str:
        """
        Generate bullet-point summary using QA approach
        
        Args:
            text: Text to summarize
            
        Returns:
            Bullet-point formatted summary
        """
        
        # Use QA model to extract key points
        questions = [
            "What are the main points?",
            "What are the key findings?",
            "What are the important details?",
            "What are the conclusions?"
        ]
        
        bullet_points = []
        
        for question in questions:
            try:
                result = await self.answer_question(question, text)
                answer = result.get("answer", "").strip()
                score = result.get("score", 0)
                
                # Only include high-confidence answers
                if answer and score > 0.1 and len(answer) > 10:
                    bullet_points.append(f"• {answer}")
                    
            except Exception as e:
                logger.warning("Failed to answer question for bullet summary", 
                             question=question, error=str(e))
                continue
        
        if not bullet_points:
            # Fallback to regular summarization
            logger.info("Falling back to regular summarization for bullets")
            summary = await self.summarize_text(text, max_length=150, min_length=50)
            # Convert to bullet format
            sentences = summary.split('. ')
            bullet_points = [f"• {sentence.strip()}." for sentence in sentences if sentence.strip()]
        
        return "\n".join(bullet_points[:5])  # Limit to 5 bullet points
    
    async def generate_tweet_summary(self, text: str) -> str:
        """
        Generate tweet-length summary (280 characters max)
        
        Args:
            text: Text to summarize
            
        Returns:
            Tweet-length summary
        """
        
        summary = await self.summarize_text(text, max_length=50, min_length=10)
        
        # Ensure it fits in a tweet
        if len(summary) > 280:
            summary = summary[:277] + "..."
        
        logger.info("Generated tweet summary", 
                   original_length=len(text),
                   summary_length=len(summary))
        
        return summary


# Convenience functions for direct usage
async def summarize_text(text: str, length_type: str = "short") -> str:
    """
    Convenience function to summarize text
    
    Args:
        text: Text to summarize
        length_type: Type of summary (short, bullets, tweet)
        
    Returns:
        Summarized text
    """
    
    async with HuggingFaceClient() as client:
        if length_type == "bullets":
            return await client.generate_bullet_summary(text)
        elif length_type == "tweet":
            return await client.generate_tweet_summary(text)
        else:  # short
            return await client.summarize_text(text, max_length=100, min_length=30)


async def answer_question(question: str, context: str) -> Dict[str, Any]:
    """
    Convenience function to answer questions
    
    Args:
        question: Question to answer
        context: Context text
        
    Returns:
        Answer dictionary
    """
    
    async with HuggingFaceClient() as client:
        return await client.answer_question(question, context)


# Standalone function for backward compatibility
async def summarize_text(text: str, length_type: str = "short") -> str:
    """
    Standalone function to summarize text using Hugging Face API
    
    Args:
        text: Text to summarize
        length_type: Type of summary (short, bullets, tweet)
        
    Returns:
        Summarized text
    """
    try:
        async with HuggingFaceClient() as client:
            return await client.summarize_text(text)
    except Exception as e:
        logger.error("Standalone summarization failed", error=str(e))
        # Return a simple fallback summary
        sentences = text.split('.')[:3]  # First 3 sentences
        return '. '.join(sentences).strip() + '.' if sentences else "Summary not available."