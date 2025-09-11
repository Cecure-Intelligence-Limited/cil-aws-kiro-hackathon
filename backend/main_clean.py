"""
Aura Desktop Assistant FastAPI Backend
Provides REST API endpoints for file operations, spreadsheet analysis, and document processing.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Optional, List
from pathlib import Path

import structlog
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import uvicorn

from config import settings
from services.file_service import FileService
from services.spreadsheet_service import SpreadsheetService
from services.intelligent_spreadsheet_service import IntelligentSpreadsheetService
from services.document_service import DocumentService
from services.ocr_service import OCRService
from services.email_service import EmailService
from services.calendar_service import CalendarService
from services.report_service import ReportService
from services.workflow_service import WorkflowService
from utils.logging_config import setup_logging

# Setup structured logging
setup_logging()
logger = structlog.get_logger(__name__)

# Initialize services
file_service = FileService()
spreadsheet_service = SpreadsheetService()
intelligent_spreadsheet_service = IntelligentSpreadsheetService()
document_service = DocumentService()
ocr_service = OCRService()
email_service = EmailService()
calendar_service = CalendarService()
report_service = ReportService()
workflow_service = WorkflowService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Aura Desktop Assistant API", version="1.0.0")
    yield
    logger.info("Shutting down Aura Desktop Assistant API")


# Create FastAPI app
app = FastAPI(
    title="Aura Desktop Assistant API",
    description="REST API for desktop automation, file operations, and document processing",
    version="1.0.0",
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_DOCS else None,
    lifespan=lifespan
)

# Add CORS middleware - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)


# Request/Response Models
class CreateFileRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Name of the file to create")
    path: Optional[str] = Field(None, description="Optional directory path where file should be created")
    content: Optional[str] = Field("", description="Optional initial content for the file")

    @validator('title')
    def validate_filename(cls, v):
        invalid_chars = '<>:"|?*'
        if any(char in v for char in invalid_chars):
            raise ValueError(f"Filename contains invalid characters: {invalid_chars}")
        return v

    @validator('path')
    def validate_path(cls, v):
        if v and ('..' in v or v.startswith('/')):
            raise ValueError("Path traversal not allowed")
        return v


class AnalyzeSheetRequest(BaseModel):
    path: str = Field(..., description="Path to the spreadsheet file")
    op: str = Field(..., pattern="^(sum|avg|count|total)$", description="Operation to perform")
    column: str = Field(..., min_length=1, max_length=100, description="Column name to analyze")


class UpdateSheetRequest(BaseModel):
    path: str = Field(..., description="Path to the spreadsheet file")
    operation: str = Field(..., pattern="^(salary_increase|bonus_update|add_column)$", description="Update operation to perform")
    column: Optional[str] = Field(None, description="Column name for operations")
    value: Optional[str] = Field(None, description="Value for operations")
    percentage: Optional[float] = Field(None, description="Percentage for increases")


class ExtractDataRequest(BaseModel):
    file_path: str = Field(..., description="Path to document for data extraction")
    document_type: Optional[str] = Field("auto", pattern="^(auto|invoice|contract|form|receipt)$", description="Type of document")


class EmailRuleRequest(BaseModel):
    name: str = Field(..., description="Name of the email rule")
    condition: str = Field(..., description="Rule condition (e.g., 'subject contains invoice')")
    action: str = Field(..., pattern="^(move|label|forward|respond)$", description="Action to take")
    target: str = Field(..., description="Target folder, label, recipient, or template")


class GenerateReportRequest(BaseModel):
    report_type: str = Field(..., pattern="^(sales|financial|performance|custom)$", description="Type of report to generate")
    data_sources: List[str] = Field(..., description="List of data sources (file paths or source names)")
    period: Optional[str] = Field("monthly", pattern="^(daily|weekly|monthly|quarterly)$", description="Report period")


class ClassifyDocumentRequest(BaseModel):
    file_path: str = Field(..., description="Path to document file")


class SmartSpreadsheetRequest(BaseModel):
    command: str = Field(..., description="Natural language command for spreadsheet operation")
    file_reference: Optional[str] = Field(None, description="Optional specific file reference")


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    error: Optional[str] = None


# API Routes
@app.get("/")
async def root():
    """Root endpoint - Welcome page with API information"""
    return {
        "message": "🎯 Aura Desktop Assistant API",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "📄 OCR Data Extraction from invoices/receipts",
            "📧 Email Management with smart sorting",
            "📅 Calendar Scheduling across time zones", 
            "📊 Report Generation with charts",
            "🔄 Document Workflow Processing",
            "📈 Spreadsheet Analysis & In-Place Updates",
            "🗂️ File Operations with voice commands"
        ],
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "api_prefix": "/api/"
        },
        "demo_ready": True
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


@app.post("/api/create-file", response_model=APIResponse)
async def create_file(request: CreateFileRequest):
    """Create a new file with optional content"""
    try:
        result = await file_service.create_file(
            title=request.title,
            path=request.path,
            content=request.content
        )
        
        return APIResponse(
            success=True,
            message=f"File '{request.title}' created successfully",
            data=result
        )
        
    except FileExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"File already exists: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create file: {str(e)}"
        )


@app.post("/api/analyze-sheet", response_model=APIResponse)
async def analyze_spreadsheet(request: AnalyzeSheetRequest):
    """Analyze spreadsheet data with specified operation"""
    try:
        result = await spreadsheet_service.analyze(
            path=request.path,
            operation=request.op,
            column=request.column
        )
        
        return APIResponse(
            success=True,
            message=f"Analysis completed: {request.op} of '{result['matched_column']}' = {result['result']}",
            data=result
        )
        
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spreadsheet file not found: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze spreadsheet: {str(e)}"
        )


@app.post("/api/update-sheet", response_model=APIResponse)
async def update_spreadsheet(request: UpdateSheetRequest):
    """Update spreadsheet with various operations"""
    try:
        result = await spreadsheet_service.update_spreadsheet(
            path=request.path,
            operation=request.operation,
            column=request.column,
            value=request.value,
            percentage=request.percentage
        )
        
        return APIResponse(
            success=True,
            message=f"Spreadsheet updated successfully with {request.operation}",
            data=result
        )
        
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spreadsheet file not found: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update spreadsheet: {str(e)}"
        )


@app.post("/api/extract-data", response_model=APIResponse)
async def extract_data_from_document(request: ExtractDataRequest):
    """Extract structured data from documents using OCR"""
    try:
        # Resolve file path - check documents directory
        documents_dir = Path("documents")
        file_path = documents_dir / request.file_path
        
        if not file_path.exists():
            # Try without documents directory
            file_path = Path(request.file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Document not found: {request.file_path}")
        
        result = await ocr_service.extract_data_from_document(
            str(file_path), 
            request.document_type
        )
        
        return APIResponse(
            success=True,
            message=f"Data extracted from {request.file_path}",
            data=result
        )
        
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document file not found: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data extraction failed: {str(e)}"
        )


@app.post("/api/classify-document", response_model=APIResponse)
async def classify_document(request: ClassifyDocumentRequest):
    """Classify document type using AI analysis"""
    try:
        # Resolve file path - check documents directory
        documents_dir = Path("documents")
        file_path = documents_dir / request.file_path
        
        if not file_path.exists():
            # Try without documents directory
            file_path = Path(request.file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Document not found: {request.file_path}")
        
        result = await document_service.classify_document(str(file_path))
        
        return APIResponse(
            success=True,
            message=f"Document classified as {result.get('document_type', 'unknown')}",
            data=result
        )
        
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document file not found: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document classification failed: {str(e)}"
        )


@app.post("/api/email-rule", response_model=APIResponse)
async def create_email_rule(request: EmailRuleRequest):
    """Create email automation rule"""
    try:
        result = await email_service.create_email_rule({
            "name": request.name,
            "condition": request.condition,
            "action": request.action,
            "target": request.target
        })
        
        return APIResponse(
            success=True,
            message=f"Email rule '{request.name}' created successfully",
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create email rule: {str(e)}"
        )


@app.post("/api/generate-report", response_model=APIResponse)
async def generate_report(request: GenerateReportRequest):
    """Generate automated report from data sources"""
    try:
        report_config = {
            "type": request.report_type,
            "data_sources": request.data_sources,
            "period": request.period
        }
        
        result = await report_service.generate_report(report_config)
        
        return APIResponse(
            success=True,
            message=f"{request.report_type.title()} report generated successfully",
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {str(e)}"
        )


@app.post("/api/smart-spreadsheet", response_model=APIResponse)
async def smart_spreadsheet_operation(request: SmartSpreadsheetRequest):
    """
    🏆 THE WOW FACTOR ENDPOINT 🏆
    Process natural language commands on ANY spreadsheet file
    
    Examples:
    - "Read payroll.xlsx and calculate total salaries"
    - "Update fortune500-payroll.csv with 15% salary increase"  
    - "Analyze global-sales.csv and show top performers"
    - "Open ai-projects.csv and calculate average ROI"
    """
    try:
        result = await intelligent_spreadsheet_service.smart_file_operation(
            command=request.command,
            file_reference=request.file_reference
        )
        
        return APIResponse(
            success=True,
            message=f"Smart operation completed: {result.get('operation_type', 'analysis')}",
            data=result
        )
        
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid operation: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Smart operation failed: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_config=None  # We use structlog instead
    )