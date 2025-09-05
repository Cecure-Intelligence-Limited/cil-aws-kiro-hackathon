"""
Document processing service
Handles PDF text extraction and summarization using Hugging Face models
"""

import re
from pathlib import Path
from typing import Dict, Any, Optional
import structlog
from pypdf import PdfReader

from config import settings
from hf_client import HuggingFaceClient, summarize_text

logger = structlog.get_logger(__name__)


class DocumentService:
    """Service for document processing and summarization"""
    
    def __init__(self):
        self.max_text_length = 10000  # Maximum text length for processing
        self.min_text_length = 50     # Minimum text length for meaningful processing
    
    async def summarize(self, path: str, length_type: str = "short") -> Dict[str, Any]:
        """
        Summarize a PDF document
        
        Args:
            path: Path to PDF document
            length_type: Type of summary (short, bullets, tweet)
            
        Returns:
            Dictionary with summarization results
        """
        
        try:
            # Validate file path
            file_path = Path(path)
            if not file_path.exists():
                raise FileNotFoundError(f"PDF file not found: {path}")
            
            # Check file size
            if file_path.stat().st_size > settings.MAX_FILE_SIZE:
                raise ValueError(f"File too large: {file_path.stat().st_size} bytes")
            
            # Extract text from PDF
            text = await self._extract_pdf_text(file_path)
            
            # Validate extracted text
            if len(text.strip()) < self.min_text_length:
                raise ValueError("Document contains insufficient text for summarization")
            
            # Preprocess text
            processed_text = self._preprocess_text(text)
            
            # Generate summary based on length type
            summary = await self._generate_summary(processed_text, length_type)
            
            # Count words in summary
            word_count = len(summary.split())
            
            logger.info("Document summarization completed",
                       path=path,
                       length_type=length_type,
                       original_length=len(text),
                       summary_length=len(summary),
                       word_count=word_count)
            
            return {
                "summary": summary,
                "length_type": length_type,
                "word_count": word_count,
                "original_length": len(text),
                "pages_processed": self._count_pdf_pages(file_path)
            }
            
        except Exception as e:
            logger.error("Document summarization failed", 
                        path=path, 
                        length_type=length_type, 
                        error=str(e))
            raise
    
    async def _extract_pdf_text(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        
        try:
            text = ""
            
            # Try with pypdf first (more modern)
            try:
                reader = PdfReader(str(file_path))
                
                for page_num, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except Exception as e:
                        logger.warning("Failed to extract text from page", 
                                     page=page_num, error=str(e))
                        continue
                        
            except Exception as e:
                logger.warning("pypdf extraction failed, trying PyPDF2", error=str(e))
                
                # Fallback to PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    
                    for page_num in range(len(pdf_reader.pages)):
                        try:
                            page = pdf_reader.pages[page_num]
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + "\n"
                        except Exception as e:
                            logger.warning("Failed to extract text from page", 
                                         page=page_num, error=str(e))
                            continue
            
            if not text.strip():
                raise ValueError("No text could be extracted from the PDF")
            
            logger.info("PDF text extraction completed",
                       path=str(file_path),
                       text_length=len(text),
                       pages=self._count_pdf_pages(file_path))
            
            return text.strip()
            
        except Exception as e:
            logger.error("PDF text extraction failed", path=str(file_path), error=str(e))
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    def _count_pdf_pages(self, file_path: Path) -> int:
        """Count pages in PDF file"""
        try:
            reader = PdfReader(str(file_path))
            return len(reader.pages)
        except:
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    return len(pdf_reader.pages)
            except:
                return 0
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess extracted text for better summarization"""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers (common patterns)
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        text = re.sub(r'\n\s*Page \d+.*?\n', '\n', text, flags=re.IGNORECASE)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Clean up multiple newlines
        text = re.sub(r'\n+', '\n', text)
        
        # Truncate if too long
        if len(text) > self.max_text_length:
            text = text[:self.max_text_length] + "..."
            logger.info("Text truncated for processing", 
                       original_length=len(text),
                       truncated_length=self.max_text_length)
        
        return text.strip()
    
    async def _generate_summary(self, text: str, length_type: str) -> str:
        """Generate summary using Hugging Face models"""
        
        try:
            # Check if HF API is available
            if not settings.HF_API_TOKEN:
                logger.warning("No Hugging Face API token, using fallback summarization")
                return self._fallback_summary(text, length_type)
            
            # Use Hugging Face API for summarization
            summary = await summarize_text(text, length_type)
            
            if not summary or len(summary.strip()) < 10:
                logger.warning("HF API returned insufficient summary, using fallback")
                return self._fallback_summary(text, length_type)
            
            return summary
            
        except Exception as e:
            logger.error("HF summarization failed, using fallback", error=str(e))
            return self._fallback_summary(text, length_type)
    
    def _fallback_summary(self, text: str, length_type: str) -> str:
        """Fallback summarization using simple text processing"""
        
        sentences = self._split_into_sentences(text)
        
        if length_type == "tweet":
            # Return first sentence, truncated to tweet length
            if sentences:
                summary = sentences[0]
                if len(summary) > 280:
                    summary = summary[:277] + "..."
                return summary
            return "Document summary not available."
        
        elif length_type == "bullets":
            # Return first few sentences as bullet points
            bullet_points = []
            for i, sentence in enumerate(sentences[:5]):
                if len(sentence.strip()) > 20:  # Skip very short sentences
                    bullet_points.append(f"• {sentence.strip()}")
                if len(bullet_points) >= 3:
                    break
            
            return "\n".join(bullet_points) if bullet_points else "• Document summary not available."
        
        else:  # short
            # Return first 2-3 sentences
            summary_sentences = []
            total_length = 0
            
            for sentence in sentences:
                if total_length + len(sentence) > 500:  # Limit to ~500 chars
                    break
                summary_sentences.append(sentence.strip())
                total_length += len(sentence)
                
                if len(summary_sentences) >= 3:
                    break
            
            return " ".join(summary_sentences) if summary_sentences else "Document summary not available."
    
    def _split_into_sentences(self, text: str) -> list:
        """Split text into sentences"""
        
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter sentences
        clean_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10 and not sentence.isupper():  # Skip very short or all-caps sentences
                clean_sentences.append(sentence)
        
        return clean_sentences[:20]  # Limit to first 20 sentences