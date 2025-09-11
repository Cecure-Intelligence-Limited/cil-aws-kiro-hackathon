"""
Document processing service
Handles PDF text extraction and summarization using Hugging Face models
"""

import re
from pathlib import Path
from typing import Dict, Any, Optional
import structlog
from pypdf import PdfReader

# Fallback import for PyPDF2
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

from config import settings

# Import HuggingFace client with fallback
try:
    from hf_client import HuggingFaceClient
    HF_CLIENT_AVAILABLE = True
except ImportError as e:
    logger.warning("HuggingFace client not available", error=str(e))
    HuggingFaceClient = None
    HF_CLIENT_AVAILABLE = False

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
            # Check if HF client is available
            if not HF_CLIENT_AVAILABLE or not HuggingFaceClient:
                logger.info("HuggingFace client not available, using fallback summarization")
                return self._fallback_summary(text, length_type)
            
            # Check if HF API token is configured
            if not hasattr(settings, 'HF_API_TOKEN') or not settings.HF_API_TOKEN:
                logger.info("No Hugging Face API token configured, using fallback summarization")
                return self._fallback_summary(text, length_type)
            
            # Use Hugging Face API for summarization
            async with HuggingFaceClient() as hf_client:
                if length_type == "bullets":
                    summary = await hf_client.generate_bullet_summary(text)
                elif length_type == "tweet":
                    summary = await hf_client.generate_tweet_summary(text)
                else:
                    summary = await hf_client.summarize_text(text)
            
            if not summary or len(summary.strip()) < 10:
                logger.warning("HF API returned insufficient summary, using fallback")
                return self._fallback_summary(text, length_type)
            
            logger.info("HuggingFace summarization successful", length_type=length_type)
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
 
    async def classify_document(self, file_path: str) -> Dict[str, Any]:
        """
        Classify document type based on content analysis
        
        Args:
            file_path: Path to document file
            
        Returns:
            Dictionary with classification results
        """
        
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"Document not found: {file_path}")
            
            # Extract text based on file type
            if path.suffix.lower() == '.pdf':
                text = await self._extract_pdf_text(path)
            else:
                # For text files, read directly
                with open(path, 'r', encoding='utf-8') as f:
                    text = f.read()
            
            # Classify document type
            document_type = self._detect_document_type(text)
            confidence = self._calculate_classification_confidence(text, document_type)
            
            # Determine priority based on document type
            priority = self._determine_priority(document_type)
            
            logger.info("Document classification completed",
                       file_path=file_path,
                       document_type=document_type,
                       confidence=confidence,
                       priority=priority)
            
            return {
                "document_type": document_type,
                "confidence": confidence,
                "priority": priority,
                "file_path": file_path,
                "text_length": len(text),
                "classification_details": self._get_classification_details(text, document_type)
            }
            
        except Exception as e:
            logger.error("Document classification failed", 
                        file_path=file_path, 
                        error=str(e))
            raise
    
    def _detect_document_type(self, text: str) -> str:
        """Detect document type based on text content"""
        
        text_lower = text.lower()
        
        # Contract detection
        contract_keywords = ['agreement', 'contract', 'terms and conditions', 'party', 'whereas', 'parties:', 'contractor:', 'client:']
        contract_score = sum(1 for keyword in contract_keywords if keyword in text_lower)
        
        # Invoice detection
        invoice_keywords = ['invoice', 'bill', 'amount due', 'total amount', 'invoice number', 'due date', 'payment terms']
        invoice_score = sum(1 for keyword in invoice_keywords if keyword in text_lower)
        
        # Report detection
        report_keywords = ['report', 'analysis', 'summary', 'findings', 'conclusion', 'executive summary']
        report_score = sum(1 for keyword in report_keywords if keyword in text_lower)
        
        # Legal document detection
        legal_keywords = ['legal', 'law', 'court', 'jurisdiction', 'statute', 'regulation', 'compliance']
        legal_score = sum(1 for keyword in legal_keywords if keyword in text_lower)
        
        # Form detection
        form_keywords = ['application', 'form', 'please fill', 'signature', 'date signed', 'applicant']
        form_score = sum(1 for keyword in form_keywords if keyword in text_lower)
        
        # Receipt detection
        receipt_keywords = ['receipt', 'thank you', 'purchase', 'transaction', 'card ending']
        receipt_score = sum(1 for keyword in receipt_keywords if keyword in text_lower)
        
        # Determine document type based on highest score
        scores = {
            'contract': contract_score,
            'invoice': invoice_score,
            'report': report_score,
            'legal': legal_score,
            'form': form_score,
            'receipt': receipt_score
        }
        
        max_score = max(scores.values())
        if max_score == 0:
            return 'document'
        
        # Return the type with highest score
        for doc_type, score in scores.items():
            if score == max_score:
                return doc_type
        
        return 'document'
    
    def _calculate_classification_confidence(self, text: str, document_type: str) -> float:
        """Calculate confidence score for classification"""
        
        text_lower = text.lower()
        
        # Define keyword sets for each document type
        keyword_sets = {
            'contract': ['agreement', 'contract', 'terms', 'party', 'whereas', 'parties', 'contractor', 'client'],
            'invoice': ['invoice', 'bill', 'amount', 'total', 'due', 'payment', 'terms'],
            'report': ['report', 'analysis', 'summary', 'findings', 'conclusion', 'executive'],
            'legal': ['legal', 'law', 'court', 'jurisdiction', 'statute', 'regulation'],
            'form': ['application', 'form', 'fill', 'signature', 'signed', 'applicant'],
            'receipt': ['receipt', 'purchase', 'transaction', 'thank you', 'card'],
            'document': []
        }
        
        if document_type not in keyword_sets:
            return 0.5
        
        keywords = keyword_sets[document_type]
        if not keywords:
            return 0.5
        
        # Count keyword matches
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        
        # Calculate confidence based on keyword density
        confidence = min(0.95, 0.5 + (matches / len(keywords)) * 0.45)
        
        return round(confidence, 2)
    
    def _determine_priority(self, document_type: str) -> str:
        """Determine processing priority based on document type"""
        
        priority_map = {
            'invoice': 'high',
            'contract': 'high',
            'legal': 'high',
            'form': 'medium',
            'receipt': 'low',
            'report': 'medium',
            'document': 'low'
        }
        
        return priority_map.get(document_type, 'low')
    
    def _get_classification_details(self, text: str, document_type: str) -> Dict[str, Any]:
        """Get additional classification details"""
        
        details = {
            'word_count': len(text.split()),
            'character_count': len(text),
            'estimated_pages': max(1, len(text) // 2000),  # Rough estimate
        }
        
        # Add type-specific details
        if document_type == 'contract':
            details['contains_signatures'] = 'signature' in text.lower()
            details['contains_dates'] = bool(re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text))
        elif document_type == 'invoice':
            details['contains_amounts'] = bool(re.search(r'\$[\d,]+\.?\d*', text))
            details['contains_due_date'] = 'due date' in text.lower()
        
        return details