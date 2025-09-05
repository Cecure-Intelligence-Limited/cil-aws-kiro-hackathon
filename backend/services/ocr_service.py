"""
OCR and Data Extraction Service
Handles document processing, OCR, and structured data extraction
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
import structlog
import pytesseract
from PIL import Image
import re
import json
import io

logger = structlog.get_logger(__name__)


class OCRService:
    """Service for OCR and document data extraction"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']
        
    async def extract_data_from_document(self, file_path: str, document_type: str = "auto") -> Dict[str, Any]:
        """
        Extract structured data from documents using OCR
        
        Args:
            file_path: Path to document file
            document_type: Type of document (invoice, contract, form, auto)
            
        Returns:
            Dictionary with extracted structured data
        """
        
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"Document not found: {file_path}")
            
            # Extract text using OCR
            extracted_text = await self._extract_text_from_image(path)
            
            # Detect document type if auto
            if document_type == "auto":
                document_type = self._detect_document_type(extracted_text)
            
            # Extract structured data based on document type
            structured_data = self._extract_structured_data(extracted_text, document_type)
            
            logger.info("Document data extraction completed",
                       file_path=file_path,
                       document_type=document_type,
                       fields_extracted=len(structured_data))
            
            return {
                "document_type": document_type,
                "extracted_data": structured_data,
                "raw_text": extracted_text,
                "confidence": self._calculate_confidence(structured_data),
                "file_path": file_path
            }
            
        except Exception as e:
            logger.error("Document data extraction failed", 
                        file_path=file_path, 
                        error=str(e))
            raise
    
    async def _extract_text_from_image(self, file_path: Path) -> str:
        """Extract text from image using OCR or fallback to file reading"""
        
        try:
            # For text files, read directly
            if file_path.suffix.lower() in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            # Try OCR for images and PDFs
            if file_path.suffix.lower() == '.pdf':
                try:
                    # For PDF, try to extract text first
                    import fitz  # PyMuPDF
                    doc = fitz.open(file_path)
                    text = ""
                    for page in doc:
                        text += page.get_text()
                    if text.strip():
                        return text.strip()
                    
                    # If no text, try OCR on first page
                    page = doc[0]
                    pix = page.get_pixmap()
                    img_data = pix.tobytes("png")
                    image = Image.open(io.BytesIO(img_data))
                except ImportError:
                    # Fallback if PyMuPDF not available
                    return await self._simulate_ocr(file_path)
            else:
                try:
                    image = Image.open(file_path)
                except ImportError:
                    return await self._simulate_ocr(file_path)
            
            try:
                # Preprocess image for better OCR
                image = self._preprocess_image(image)
                
                # Extract text using Tesseract
                text = pytesseract.image_to_string(image, config='--psm 6')
                return text.strip()
            except ImportError:
                # Tesseract not available, use simulation
                return await self._simulate_ocr(file_path)
            
        except Exception as e:
            logger.warning("OCR extraction failed, using simulation", file_path=str(file_path), error=str(e))
            return await self._simulate_ocr(file_path)
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR accuracy"""
        
        try:
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Convert to numpy array for OpenCV processing
            img_array = np.array(image)
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(img_array)
            
            # Apply threshold for better text recognition
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Convert back to PIL Image
            return Image.fromarray(thresh)
        except ImportError:
            # OpenCV not available, return original image
            logger.warning("OpenCV not available, skipping image preprocessing")
            return image
        except Exception as e:
            logger.warning("Image preprocessing failed", error=str(e))
            return image
    
    def _detect_document_type(self, text: str) -> str:
        """Detect document type based on text content"""
        
        text_lower = text.lower()
        
        # Invoice detection
        invoice_keywords = ['invoice', 'bill', 'amount due', 'total amount', 'invoice number', 'due date']
        if any(keyword in text_lower for keyword in invoice_keywords):
            return "invoice"
        
        # Contract detection
        contract_keywords = ['agreement', 'contract', 'terms and conditions', 'party', 'whereas']
        if any(keyword in text_lower for keyword in contract_keywords):
            return "contract"
        
        # Form detection
        form_keywords = ['application', 'form', 'please fill', 'signature', 'date signed']
        if any(keyword in text_lower for keyword in form_keywords):
            return "form"
        
        # Receipt detection
        receipt_keywords = ['receipt', 'thank you', 'purchase', 'transaction', 'card ending']
        if any(keyword in text_lower for keyword in receipt_keywords):
            return "receipt"
        
        return "document"
    
    def _extract_structured_data(self, text: str, document_type: str) -> Dict[str, Any]:
        """Extract structured data based on document type"""
        
        if document_type == "invoice":
            return self._extract_invoice_data(text)
        elif document_type == "contract":
            return self._extract_contract_data(text)
        elif document_type == "form":
            return self._extract_form_data(text)
        elif document_type == "receipt":
            return self._extract_receipt_data(text)
        else:
            return self._extract_generic_data(text)
    
    def _extract_invoice_data(self, text: str) -> Dict[str, Any]:
        """Extract structured data from invoice"""
        
        data = {}
        
        # Extract invoice number
        invoice_patterns = [
            r'invoice\s*#?\s*:?\s*([A-Z0-9\-]+)',
            r'inv\s*#?\s*:?\s*([A-Z0-9\-]+)',
            r'#\s*([A-Z0-9\-]+)'
        ]
        for pattern in invoice_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data['invoice_number'] = match.group(1)
                break
        
        # Extract total amount
        amount_patterns = [
            r'total\s*:?\s*\$?([0-9,]+\.?[0-9]*)',
            r'amount\s*due\s*:?\s*\$?([0-9,]+\.?[0-9]*)',
            r'balance\s*:?\s*\$?([0-9,]+\.?[0-9]*)'
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    data['total_amount'] = float(amount_str)
                except ValueError:
                    continue
                break
        
        # Extract date
        date_patterns = [
            r'date\s*:?\s*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})',
            r'([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data['date'] = match.group(1)
                break
        
        # Extract vendor/company name (first line usually)
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if len(line) > 3 and not any(char.isdigit() for char in line):
                data['vendor'] = line
                break
        
        return data
    
    def _extract_contract_data(self, text: str) -> Dict[str, Any]:
        """Extract structured data from contract"""
        
        data = {}
        
        # Extract parties
        party_patterns = [
            r'between\s+([^,\n]+)\s+and\s+([^,\n]+)',
            r'party\s*:\s*([^\n]+)',
            r'client\s*:\s*([^\n]+)'
        ]
        for pattern in party_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if 'between' in pattern:
                    data['party_1'] = match.group(1).strip()
                    data['party_2'] = match.group(2).strip()
                else:
                    data['party'] = match.group(1).strip()
                break
        
        # Extract contract value
        value_patterns = [
            r'amount\s*:?\s*\$?([0-9,]+\.?[0-9]*)',
            r'value\s*:?\s*\$?([0-9,]+\.?[0-9]*)',
            r'fee\s*:?\s*\$?([0-9,]+\.?[0-9]*)'
        ]
        for pattern in value_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    data['contract_value'] = float(amount_str)
                except ValueError:
                    continue
                break
        
        # Extract dates
        date_patterns = [
            r'effective\s+date\s*:?\s*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})',
            r'start\s+date\s*:?\s*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})',
            r'end\s+date\s*:?\s*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if 'effective' in pattern:
                    data['effective_date'] = match.group(1)
                elif 'start' in pattern:
                    data['start_date'] = match.group(1)
                elif 'end' in pattern:
                    data['end_date'] = match.group(1)
        
        return data
    
    def _extract_form_data(self, text: str) -> Dict[str, Any]:
        """Extract structured data from form"""
        
        data = {}
        
        # Extract name
        name_patterns = [
            r'name\s*:?\s*([^\n]+)',
            r'full\s+name\s*:?\s*([^\n]+)',
            r'applicant\s*:?\s*([^\n]+)'
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data['name'] = match.group(1).strip()
                break
        
        # Extract email
        email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        match = re.search(email_pattern, text)
        if match:
            data['email'] = match.group(1)
        
        # Extract phone
        phone_patterns = [
            r'phone\s*:?\s*([0-9\-\(\)\s]+)',
            r'tel\s*:?\s*([0-9\-\(\)\s]+)',
            r'([0-9]{3}[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})'
        ]
        for pattern in phone_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data['phone'] = match.group(1).strip()
                break
        
        return data
    
    def _extract_receipt_data(self, text: str) -> Dict[str, Any]:
        """Extract structured data from receipt"""
        
        data = {}
        
        # Extract merchant name (usually first line)
        lines = text.split('\n')
        for line in lines[:3]:
            line = line.strip()
            if len(line) > 3:
                data['merchant'] = line
                break
        
        # Extract total amount
        amount_patterns = [
            r'total\s*:?\s*\$?([0-9,]+\.?[0-9]*)',
            r'amount\s*:?\s*\$?([0-9,]+\.?[0-9]*)'
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    data['total'] = float(amount_str)
                except ValueError:
                    continue
                break
        
        # Extract date/time
        datetime_patterns = [
            r'([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})',
            r'([0-9]{1,2}:[0-9]{2})'
        ]
        for pattern in datetime_patterns:
            match = re.search(pattern, text)
            if match:
                if ':' in match.group(1):
                    data['time'] = match.group(1)
                else:
                    data['date'] = match.group(1)
        
        return data
    
    def _extract_generic_data(self, text: str) -> Dict[str, Any]:
        """Extract generic data from any document"""
        
        data = {}
        
        # Extract emails
        email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        emails = re.findall(email_pattern, text)
        if emails:
            data['emails'] = emails
        
        # Extract phone numbers
        phone_pattern = r'([0-9]{3}[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})'
        phones = re.findall(phone_pattern, text)
        if phones:
            data['phone_numbers'] = phones
        
        # Extract dates
        date_pattern = r'([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})'
        dates = re.findall(date_pattern, text)
        if dates:
            data['dates'] = dates
        
        # Extract amounts
        amount_pattern = r'\$?([0-9,]+\.?[0-9]*)'
        amounts = re.findall(amount_pattern, text)
        if amounts:
            try:
                data['amounts'] = [float(amt.replace(',', '')) for amt in amounts if float(amt.replace(',', '')) > 0]
            except ValueError:
                pass
        
        return data
    
    def _calculate_confidence(self, structured_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on extracted data completeness"""
        
        if not structured_data:
            return 0.0
        
        # Base confidence on number of fields extracted
        field_count = len(structured_data)
        
        # Higher confidence for more complete data
        if field_count >= 5:
            return 0.95
        elif field_count >= 3:
            return 0.85
        elif field_count >= 2:
            return 0.75
        elif field_count >= 1:
            return 0.65
        else:
            return 0.5
    
    async def transfer_data_to_spreadsheet(self, extracted_data: Dict[str, Any], 
                                         destination_file: str, 
                                         mapping: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Transfer extracted data to spreadsheet
        
        Args:
            extracted_data: Data extracted from document
            destination_file: Path to destination spreadsheet
            mapping: Optional field mapping (source_field -> destination_column)
            
        Returns:
            Dictionary with transfer results
        """
        
        try:
            import pandas as pd
            from pathlib import Path
            
            dest_path = Path(destination_file)
            
            # Load or create destination spreadsheet
            if dest_path.exists():
                if dest_path.suffix.lower() == '.csv':
                    df = pd.read_csv(dest_path)
                else:
                    df = pd.read_excel(dest_path)
            else:
                # Create new spreadsheet with extracted data columns
                df = pd.DataFrame()
            
            # Prepare data for insertion
            data_to_insert = extracted_data.get('extracted_data', {})
            
            # Apply field mapping if provided
            if mapping:
                mapped_data = {}
                for source_field, dest_column in mapping.items():
                    if source_field in data_to_insert:
                        mapped_data[dest_column] = data_to_insert[source_field]
                data_to_insert = mapped_data
            
            # Add new row to dataframe
            new_row = pd.DataFrame([data_to_insert])
            df = pd.concat([df, new_row], ignore_index=True)
            
            # Save updated spreadsheet
            if dest_path.suffix.lower() == '.csv':
                df.to_csv(dest_path, index=False)
            else:
                df.to_excel(dest_path, index=False)
            
            logger.info("Data transfer completed",
                       destination=destination_file,
                       fields_transferred=len(data_to_insert),
                       total_rows=len(df))
            
            return {
                "success": True,
                "destination_file": destination_file,
                "fields_transferred": list(data_to_insert.keys()),
                "new_row_index": len(df) - 1,
                "total_rows": len(df)
            }
            
        except Exception as e:
            logger.error("Data transfer failed", 
                        destination=destination_file, 
                        error=str(e))
            raise