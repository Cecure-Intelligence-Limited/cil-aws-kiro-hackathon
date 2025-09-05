"""
PDF Summarization Tests with Mock HF API
Tests document processing functionality using pytest
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path

from services.document_service import DocumentService
from hf_client import HuggingFaceClient


@pytest.fixture
def sample_pdf_content():
    """Sample PDF text content for testing"""
    return """
    Quarterly Business Report - Q4 2024
    
    Executive Summary:
    Our company achieved record-breaking revenue of $2.5 million in Q4 2024, 
    representing a 25% increase from the previous quarter. Key highlights include:
    
    - Revenue growth of 25% quarter-over-quarter
    - Customer acquisition increased by 40%
    - Product launches in three new markets
    - Team expansion with 15 new hires
    
    Financial Performance:
    Total revenue for Q4 reached $2.5M, driven primarily by strong sales in 
    our core product lines. Operating expenses were well-controlled at $1.8M, 
    resulting in a healthy profit margin of 28%.
    
    Market Expansion:
    We successfully launched our products in European, Asian, and South American 
    markets, establishing partnerships with local distributors and achieving 
    initial market penetration of 5-8% in each region.
    
    Future Outlook:
    Looking ahead to 2025, we project continued growth with an estimated 
    revenue target of $12M for the full year, supported by our expanded 
    market presence and new product development initiatives.
    """


@pytest.fixture
def mock_pdf_file(sample_pdf_content):
    """Create a mock PDF file for testing"""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        # We'll mock the PDF reading, so just create an empty file
        tmp_file.write(b'Mock PDF content')
        yield tmp_file.name, sample_pdf_content
    os.unlink(tmp_file.name)


@pytest.fixture
def document_service():
    """Create DocumentService instance"""
    return DocumentService()


class TestDocumentService:
    """Test cases for document processing functionality"""

    @pytest.mark.asyncio
    @patch('services.document_service.DocumentService._extract_pdf_text')
    @patch('hf_client.summarize_text')
    async def test_short_summary(self, mock_summarize, mock_extract, document_service, mock_pdf_file):
        """Test short summary generation"""
        pdf_path, content = mock_pdf_file
        mock_extract.return_value = content
        mock_summarize.return_value = "Q4 2024 revenue reached $2.5M with 25% growth and successful market expansion."
        
        result = await document_service.summarize(pdf_path, 'short')
        
        assert result['summary'] == "Q4 2024 revenue reached $2.5M with 25% growth and successful market expansion."
        assert result['length_type'] == 'short'
        assert result['word_count'] == 13
        assert result['original_length'] == len(content)
        
        mock_extract.assert_called_once_with(Path(pdf_path))
        mock_summarize.assert_called_once_with(content, 'short')

    @pytest.mark.asyncio
    @patch('services.document_service.DocumentService._extract_pdf_text')
    @patch('hf_client.summarize_text')
    async def test_bullet_summary(self, mock_summarize, mock_extract, document_service, mock_pdf_file):
        """Test bullet point summary generation"""
        pdf_path, content = mock_pdf_file
        mock_extract.return_value = content
        mock_summarize.return_value = "• Revenue grew 25% to $2.5M\n• Customer acquisition up 40%\n• Expanded to 3 new markets"
        
        result = await document_service.summarize(pdf_path, 'bullets')
        
        assert '•' in result['summary']
        assert result['length_type'] == 'bullets'
        assert result['word_count'] == 13
        
        mock_summarize.assert_called_once_with(content, 'bullets')

    @pytest.mark.asyncio
    @patch('services.document_service.DocumentService._extract_pdf_text')
    @patch('hf_client.summarize_text')
    async def test_tweet_summary(self, mock_summarize, mock_extract, document_service, mock_pdf_file):
        """Test tweet-length summary generation"""
        pdf_path, content = mock_pdf_file
        mock_extract.return_value = content
        mock_summarize.return_value = "Q4 2024: $2.5M revenue (+25%), 40% customer growth, 3 new markets launched! 🚀"
        
        result = await document_service.summarize(pdf_path, 'tweet')
        
        assert len(result['summary']) <= 280
        assert result['length_type'] == 'tweet'
        
        mock_summarize.assert_called_once_with(content, 'tweet')

    @pytest.mark.asyncio
    async def test_nonexistent_file(self, document_service):
        """Test handling of nonexistent PDF file"""
        with pytest.raises(FileNotFoundError):
            await document_service.summarize('nonexistent.pdf', 'short')

    @pytest.mark.asyncio
    @patch('services.document_service.DocumentService._extract_pdf_text')
    async def test_empty_pdf_content(self, mock_extract, document_service, mock_pdf_file):
        """Test handling of PDF with no extractable text"""
        pdf_path, _ = mock_pdf_file
        mock_extract.return_value = ""
        
        with pytest.raises(ValueError, match="insufficient text"):
            await document_service.summarize(pdf_path, 'short')

    @pytest.mark.asyncio
    @patch('services.document_service.DocumentService._extract_pdf_text')
    @patch('hf_client.summarize_text')
    async def test_hf_api_failure_fallback(self, mock_summarize, mock_extract, document_service, mock_pdf_file):
        """Test fallback when Hugging Face API fails"""
        pdf_path, content = mock_pdf_file
        mock_extract.return_value = content
        mock_summarize.side_effect = Exception("API Error")
        
        result = await document_service.summarize(pdf_path, 'short')
        
        # Should use fallback summarization
        assert result['summary'] is not None
        assert len(result['summary']) > 0
        assert result['length_type'] == 'short'

    @pytest.mark.asyncio
    @patch('services.document_service.DocumentService._extract_pdf_text')
    async def test_text_preprocessing(self, mock_extract, document_service, mock_pdf_file):
        """Test text preprocessing functionality"""
        pdf_path, _ = mock_pdf_file
        messy_content = """
        Page 1
        
        Title    with    extra    spaces
        
        
        Multiple newlines
        
        
        http://example.com/url
        email@example.com
        
        Page 2
        
        More content here
        """
        mock_extract.return_value = messy_content
        
        # Access the private method for testing
        processed = document_service._preprocess_text(messy_content)
        
        assert 'http://example.com/url' not in processed
        assert 'email@example.com' not in processed
        assert processed.count('\n') < messy_content.count('\n')
        assert '    ' not in processed  # Multiple spaces should be reduced

    def test_sentence_splitting(self, document_service):
        """Test sentence splitting functionality"""
        text = "First sentence. Second sentence! Third sentence? Fourth sentence."
        sentences = document_service._split_into_sentences(text)
        
        assert len(sentences) == 4
        assert "First sentence" in sentences[0]
        assert "Second sentence" in sentences[1]

    @pytest.mark.asyncio
    @patch('services.document_service.DocumentService._extract_pdf_text')
    async def test_fallback_summary_types(self, mock_extract, document_service, mock_pdf_file):
        """Test different fallback summary types"""
        pdf_path, content = mock_pdf_file
        mock_extract.return_value = content
        
        # Mock HF API failure to trigger fallback
        with patch('hf_client.summarize_text', side_effect=Exception("API Error")):
            # Test short fallback
            result_short = await document_service.summarize(pdf_path, 'short')
            assert result_short['length_type'] == 'short'
            assert len(result_short['summary']) > 0
            
            # Test bullets fallback
            result_bullets = await document_service.summarize(pdf_path, 'bullets')
            assert result_bullets['length_type'] == 'bullets'
            assert '•' in result_bullets['summary']
            
            # Test tweet fallback
            result_tweet = await document_service.summarize(pdf_path, 'tweet')
            assert result_tweet['length_type'] == 'tweet'
            assert len(result_tweet['summary']) <= 280

    @pytest.mark.asyncio
    @patch('services.document_service.DocumentService._count_pdf_pages')
    @patch('services.document_service.DocumentService._extract_pdf_text')
    async def test_page_count_tracking(self, mock_extract, mock_count_pages, document_service, mock_pdf_file):
        """Test PDF page count tracking"""
        pdf_path, content = mock_pdf_file
        mock_extract.return_value = content
        mock_count_pages.return_value = 5
        
        with patch('hf_client.summarize_text', return_value="Test summary"):
            result = await document_service.summarize(pdf_path, 'short')
            assert result['pages_processed'] == 5


class TestHuggingFaceClient:
    """Test cases for Hugging Face client functionality"""

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test HF client initialization"""
        client = HuggingFaceClient("test-token")
        assert client.api_token == "test-token"
        assert client.base_url is not None

    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.post')
    async def test_successful_summarization(self, mock_post):
        """Test successful text summarization"""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=[{"summary_text": "Test summary"}])
        mock_post.return_value.__aenter__.return_value = mock_response
        
        async with HuggingFaceClient("test-token") as client:
            result = await client.summarize_text("Test text", max_length=50)
            assert result == "Test summary"

    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.post')
    async def test_model_loading_retry(self, mock_post):
        """Test retry logic when model is loading"""
        # First response: model loading
        loading_response = MagicMock()
        loading_response.status = 503
        loading_response.json = AsyncMock(return_value={"estimated_time": 1})
        
        # Second response: success
        success_response = MagicMock()
        success_response.status = 200
        success_response.json = AsyncMock(return_value=[{"summary_text": "Test summary"}])
        
        mock_post.return_value.__aenter__.side_effect = [loading_response, success_response]
        
        async with HuggingFaceClient("test-token") as client:
            with patch('asyncio.sleep'):  # Mock sleep to speed up test
                result = await client.summarize_text("Test text")
                assert result == "Test summary"

    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.post')
    async def test_api_error_handling(self, mock_post):
        """Test API error handling"""
        mock_response = MagicMock()
        mock_response.status = 400
        mock_response.json = AsyncMock(return_value={"error": "Bad request"})
        mock_post.return_value.__aenter__.return_value = mock_response
        
        async with HuggingFaceClient("test-token") as client:
            with pytest.raises(Exception):
                await client.summarize_text("Test text")

    @pytest.mark.asyncio
    async def test_bullet_summary_generation(self):
        """Test bullet point summary generation"""
        client = HuggingFaceClient("test-token")
        
        with patch.object(client, 'answer_question') as mock_qa:
            mock_qa.side_effect = [
                {"answer": "Revenue increased significantly", "score": 0.8},
                {"answer": "New markets were entered", "score": 0.7},
                {"answer": "Team expanded with new hires", "score": 0.6},
                {"answer": "Low confidence answer", "score": 0.05}  # Should be filtered out
            ]
            
            result = await client.generate_bullet_summary("Test document content")
            
            assert "• Revenue increased significantly" in result
            assert "• New markets were entered" in result
            assert "• Team expanded with new hires" in result
            assert "Low confidence answer" not in result

    @pytest.mark.asyncio
    async def test_tweet_summary_length_limit(self):
        """Test tweet summary respects character limit"""
        client = HuggingFaceClient("test-token")
        
        long_summary = "This is a very long summary that exceeds the Twitter character limit " * 10
        
        with patch.object(client, 'summarize_text', return_value=long_summary):
            result = await client.generate_tweet_summary("Test content")
            assert len(result) <= 280
            assert result.endswith("...")