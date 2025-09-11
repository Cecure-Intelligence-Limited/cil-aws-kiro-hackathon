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
        # Remove control characters check that was causing issues
        if any(char in v for char in invalid_chars):
            raise ValueError(f"Filename contains invalid characters: {invalid_chars}")
        return v

    @validator('path')
    def validate_path(cls, v):
        if v and ('..' in v or v.startswith('/')):
            raise ValueError("Path traversal not allowed")
        return v


class OpenItemRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Search query for the item to open")
    type: Optional[str] = Field("auto", pattern="^(file|application|folder|auto)$", 
                               description="Type of item to open")


class AnalyzeSheetRequest(BaseModel):
    path: str = Field(..., description="Path to the spreadsheet file")
    op: str = Field(..., pattern="^(sum|avg|count|total)$", description="Operation to perform")
    column: str = Field(..., min_length=1, max_length=100, description="Column name to analyze")

    @validator('path')
    def validate_spreadsheet_path(cls, v):
        valid_extensions = ('.csv', '.xlsx', '.xls', '.ods')
        if not any(v.lower().endswith(ext) for ext in valid_extensions):
            raise ValueError(f"File must have one of these extensions: {valid_extensions}")
        return v


class SummarizeDocRequest(BaseModel):
    path: str = Field(..., description="Path to the PDF document")
    length: Optional[str] = Field("short", pattern="^(short|bullets|tweet)$", 
                                 description="Summary format and length")

    @validator('path')
    def validate_pdf_path(cls, v):
        if not v.lower().endswith('.pdf'):
            raise ValueError("File must be a PDF document")
        return v


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    error: Optional[str] = None


class SpreadsheetAnalysisResponse(BaseModel):
    success: bool
    result: float
    matched_column: str
    cells_count: int
    operation: str
    message: str


class DocumentSummaryResponse(BaseModel):
    success: bool
    summary: str
    length_type: str
    word_count: int
    message: str


class UpdateSheetRequest(BaseModel):
    path: str = Field(..., description="Path to the spreadsheet file")
    operation: str = Field(..., pattern="^(salary_increase|bonus_update|add_column)$", description="Update operation to perform")
    column: Optional[str] = Field(None, description="Column name for operations")
    value: Optional[str] = Field(None, description="Value for operations")
    percentage: Optional[float] = Field(None, description="Percentage for increases")

    @validator('path')
    def validate_spreadsheet_path(cls, v):
        valid_extensions = ('.csv', '.xlsx', '.xls', '.ods')
        if not any(v.lower().endswith(ext) for ext in valid_extensions):
            raise ValueError(f"File must have one of these extensions: {valid_extensions}")
        return v


class ExtractDataRequest(BaseModel):
    file_path: str = Field(..., description="Path to document for data extraction")
    document_type: Optional[str] = Field("auto", pattern="^(auto|invoice|contract|form|receipt)$", description="Type of document")
    destination_file: Optional[str] = Field(None, description="Optional destination spreadsheet for data transfer")


class EmailRuleRequest(BaseModel):
    name: str = Field(..., description="Name of the email rule")
    condition: str = Field(..., description="Rule condition (e.g., 'subject contains invoice')")
    action: str = Field(..., pattern="^(move|label|forward|respond)$", description="Action to take")
    target: str = Field(..., description="Target folder, label, recipient, or template")


class ScheduleMeetingRequest(BaseModel):
    participants: List[str] = Field(..., description="List of participant emails")
    duration: int = Field(60, description="Meeting duration in minutes")
    timeframe: Optional[str] = Field("next_week", description="Time range to search for slots")
    title: Optional[str] = Field("Meeting", description="Meeting title")
    agenda: Optional[str] = Field("", description="Meeting agenda")


class GenerateReportRequest(BaseModel):
    report_type: str = Field(..., pattern="^(sales|financial|performance|custom)$", description="Type of report to generate")
    data_sources: List[str] = Field(..., description="List of data sources (file paths or source names)")
    period: Optional[str] = Field("monthly", pattern="^(daily|weekly|monthly|quarterly)$", description="Report period")
    template: Optional[str] = Field("default", description="Report template to use")


class ClassifyDocumentRequest(BaseModel):
    file_path: str = Field(..., description="Path to document file")
    content: Optional[str] = Field(None, description="Optional document content if already extracted")


class ProcessApprovalRequest(BaseModel):
    workflow_id: str = Field(..., description="Workflow ID")
    approver: str = Field(..., description="Approver name/email")
    decision: str = Field(..., pattern="^(approved|rejected)$", description="Approval decision")
    comment: Optional[str] = Field("", description="Optional comment")


class SmartSpreadsheetRequest(BaseModel):
    command: str = Field(..., description="Natural language command for spreadsheet operation")
    file_reference: Optional[str] = Field(None, description="Optional specific file reference")


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
@app.post("/create_file", response_model=APIResponse)  # Keep backward compatibility
async def create_file(request: CreateFileRequest):
    """Create a new file with optional content"""
    try:
        logger.info("Creating file", title=request.title, path=request.path, 
                   content_length=len(request.content or ""))
        
        result = await file_service.create_file(
            title=request.title,
            path=request.path,
            content=request.content
        )
        
        logger.info("File created successfully", file_path=result["file_path"])
        
        return APIResponse(
            success=True,
            message=f"File '{request.title}' created successfully",
            data=result
        )
        
    except FileExistsError as e:
        logger.warning("File already exists", title=request.title, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"File already exists: {str(e)}"
        )
    except PermissionError as e:
        logger.error("Permission denied", title=request.title, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: {str(e)}"
        )
    except Exception as e:
        logger.error("Failed to create file", title=request.title, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create file: {str(e)}"
        )


@app.post("/api/open-item", response_model=APIResponse)
@app.post("/open_item", response_model=APIResponse)  # Keep backward compatibility
async def open_item(request: OpenItemRequest):
    """Open a file, application, or folder"""
    try:
        logger.info("Opening item", query=request.query, type=request.type)
        
        result = await file_service.open_item(
            query=request.query,
            item_type=request.type
        )
        
        logger.info("Item opened successfully", query=request.query, 
                   found_path=result.get("path"))
        
        return APIResponse(
            success=True,
            message=f"Opened '{request.query}' successfully",
            data=result
        )
        
    except FileNotFoundError as e:
        logger.warning("Item not found", query=request.query, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item not found: {str(e)}"
        )
    except Exception as e:
        logger.error("Failed to open item", query=request.query, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to open item: {str(e)}"
        )


@app.post("/api/analyze-sheet", response_model=SpreadsheetAnalysisResponse)
@app.post("/analyze_sheet", response_model=SpreadsheetAnalysisResponse)  # Keep backward compatibility
async def analyze_spreadsheet(request: AnalyzeSheetRequest):
    """Analyze spreadsheet data with specified operation"""
    try:
        logger.info("Analyzing spreadsheet", path=request.path, 
                   operation=request.op, column=request.column)
        
        result = await spreadsheet_service.analyze(
            path=request.path,
            operation=request.op,
            column=request.column
        )
        
        logger.info("Spreadsheet analysis completed", 
                   result=result["result"], 
                   matched_column=result["matched_column"],
                   cells_count=result["cells_count"])
        
        return SpreadsheetAnalysisResponse(
            success=True,
            result=result["result"],
            matched_column=result["matched_column"],
            cells_count=result["cells_count"],
            operation=request.op,
            message=f"Analysis completed: {request.op} of '{result['matched_column']}' = {result['result']}"
        )
        
    except FileNotFoundError as e:
        logger.warning("Spreadsheet file not found", path=request.path, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spreadsheet file not found: {str(e)}"
        )
    except ValueError as e:
        logger.warning("Invalid spreadsheet operation", path=request.path, 
                      column=request.column, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid operation: {str(e)}"
        )
    except Exception as e:
        logger.error("Failed to analyze spreadsheet", path=request.path, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze spreadsheet: {str(e)}"
        )


@app.post("/summarize_doc", response_model=DocumentSummaryResponse)
async def summarize_document(request: SummarizeDocRequest):
    """Summarize a PDF document"""
    try:
        logger.info("Summarizing document", path=request.path, length=request.length)
        
        result = await document_service.summarize(
            path=request.path,
            length_type=request.length
        )
        
        logger.info("Document summarization completed", 
                   path=request.path,
                   summary_length=len(result["summary"]),
                   word_count=result["word_count"])
        
        return DocumentSummaryResponse(
            success=True,
            summary=result["summary"],
            length_type=request.length,
            word_count=result["word_count"],
            message=f"Document summarized successfully ({result['word_count']} words)"
        )
        
    except FileNotFoundError as e:
        logger.warning("PDF file not found", path=request.path, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PDF file not found: {str(e)}"
        )
    except Exception as e:
        logger.error("Failed to summarize document", path=request.path, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to summarize document: {str(e)}"
        )


@app.post("/api/update-sheet", response_model=APIResponse)
@app.post("/update_sheet", response_model=APIResponse)  # Keep backward compatibility
async def update_spreadsheet(request: UpdateSheetRequest):
    """Update spreadsheet with various operations"""
    try:
        logger.info("Updating spreadsheet", path=request.path, operation=request.operation)
        
        result = await spreadsheet_service.update_spreadsheet(
            path=request.path,
            operation=request.operation,
            column=request.column,
            value=request.value,
            percentage=request.percentage
        )
        
        logger.info("Spreadsheet updated successfully", 
                   path=request.path,
                   operation=request.operation,
                   output_file=result.get("output_file"))
        
        return APIResponse(
            success=True,
            message=f"Spreadsheet updated successfully with {request.operation}",
            data=result
        )
        
    except FileNotFoundError as e:
        logger.warning("Spreadsheet file not found", path=request.path, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spreadsheet file not found: {str(e)}"
        )
    except ValueError as e:
        logger.warning("Invalid spreadsheet update operation", path=request.path, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid operation: {str(e)}"
        )
    except Exception as e:
        logger.error("Failed to update spreadsheet", path=request.path, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update spreadsheet: {str(e)}"
        )


@app.post("/api/extract-data", response_model=APIResponse)
async def extract_document_data(request: ExtractDataRequest):
    """Extract structured data from documents using OCR"""
    try:
        logger.info("Extracting document data", file_path=request.file_path, document_type=request.document_type)
        
        result = await ocr_service.extract_data_from_document(
            file_path=request.file_path,
            document_type=request.document_type
        )
        
        # If destination file specified, transfer data
        if request.destination_file:
            transfer_result = await ocr_service.transfer_data_to_spreadsheet(
                extracted_data=result,
                destination_file=request.destination_file
            )
            result["transfer_result"] = transfer_result
        
        logger.info("Document data extraction completed", 
                   file_path=request.file_path,
                   document_type=result["document_type"],
                   confidence=result["confidence"])
        
        return APIResponse(
            success=True,
            message=f"Data extracted from {result['document_type']} with {result['confidence']:.1%} confidence",
            data=result
        )
        
    except FileNotFoundError as e:
        logger.warning("Document file not found", file_path=request.file_path, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document file not found: {str(e)}"
        )
    except Exception as e:
        logger.error("Failed to extract document data", file_path=request.file_path, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract document data: {str(e)}"
        )


@app.post("/api/email-rule", response_model=APIResponse)
async def create_email_rule(request: EmailRuleRequest):
    """Create email automation rule"""
    try:
        logger.info("Creating email rule", rule_name=request.name, action=request.action)
        
        result = await email_service.create_email_rule({
            "name": request.name,
            "condition": request.condition,
            "action": request.action,
            "target": request.target
        })
        
        logger.info("Email rule created successfully", rule_name=request.name)
        
        return APIResponse(
            success=True,
            message=f"Email rule '{request.name}' created successfully",
            data=result
        )
        
    except Exception as e:
        logger.error("Failed to create email rule", rule_name=request.name, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create email rule: {str(e)}"
        )


@app.post("/api/sort-emails", response_model=APIResponse)
async def sort_emails():
    """Sort emails using automation rules"""
    try:
        logger.info("Sorting emails using automation rules")
        
        result = await email_service.sort_emails_by_rules()
        
        logger.info("Email sorting completed", 
                   total_emails=result["total_emails"],
                   sorted_emails=result["sorted_emails"])
        
        return APIResponse(
            success=True,
            message=f"Sorted {result['sorted_emails']} out of {result['total_emails']} emails",
            data=result
        )
        
    except Exception as e:
        logger.error("Failed to sort emails", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sort emails: {str(e)}"
        )


@app.post("/api/schedule-meeting", response_model=APIResponse)
async def schedule_meeting(request: ScheduleMeetingRequest):
    """Find available slots and schedule meeting"""
    try:
        logger.info("Scheduling meeting", participants=len(request.participants), duration=request.duration)
        
        # First find available slots
        slots_result = await calendar_service.find_available_slots(
            participants=request.participants,
            duration=request.duration,
            timeframe=request.timeframe
        )
        
        if not slots_result["available_slots"]:
            return APIResponse(
                success=False,
                message="No available slots found for all participants",
                data=slots_result
            )
        
        # Use the best available slot
        best_slot = slots_result["available_slots"][0]
        
        # Schedule the meeting
        meeting_result = await calendar_service.schedule_meeting({
            "title": request.title,
            "participants": request.participants,
            "start_time": best_slot["start"].isoformat(),
            "end_time": best_slot["end"].isoformat(),
            "agenda": request.agenda
        })
        
        logger.info("Meeting scheduled successfully", 
                   meeting_id=meeting_result["meeting_id"],
                   participants=len(request.participants))
        
        return APIResponse(
            success=True,
            message=f"Meeting scheduled for {best_slot['formatted_time']} on {best_slot['day_of_week']}",
            data={
                "meeting_details": meeting_result,
                "available_slots": slots_result["available_slots"][:5]  # Show top 5 alternatives
            }
        )
        
    except Exception as e:
        logger.error("Failed to schedule meeting", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule meeting: {str(e)}"
        )


@app.get("/api/follow-ups", response_model=APIResponse)
async def track_follow_ups():
    """Track emails requiring follow-up"""
    try:
        logger.info("Tracking email follow-ups")
        
        result = await email_service.track_follow_ups()
        
        logger.info("Follow-up tracking completed", 
                   follow_ups_needed=result["follow_ups_needed"])
        
        return APIResponse(
            success=True,
            message=f"Found {result['follow_ups_needed']} emails needing follow-up",
            data=result
        )
        
    except Exception as e:
        logger.error("Failed to track follow-ups", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track follow-ups: {str(e)}"
        )


@app.post("/api/generate-report", response_model=APIResponse)
async def generate_report(request: GenerateReportRequest):
    """Generate automated report from data sources"""
    try:
        logger.info("Generating report", report_type=request.report_type, data_sources=len(request.data_sources))
        
        report_config = {
            "type": request.report_type,
            "data_sources": request.data_sources,
            "period": request.period,
            "template": request.template
        }
        
        result = await report_service.generate_report(report_config)
        
        logger.info("Report generated successfully", 
                   report_id=result["report_id"],
                   report_type=request.report_type)
        
        return APIResponse(
            success=True,
            message=f"{request.report_type.title()} report generated successfully",
            data=result
        )
        
    except Exception as e:
        logger.error("Report generation failed", report_type=request.report_type, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {str(e)}"
        )


@app.post("/api/classify-document", response_model=APIResponse)
async def classify_document(request: ClassifyDocumentRequest):
    """Classify document and determine workflow"""
    try:
        logger.info("Classifying document", file_path=request.file_path)
        
        result = await workflow_service.classify_document(
            file_path=request.file_path,
            content=request.content
        )
        
        logger.info("Document classified successfully", 
                   file_path=request.file_path,
                   document_type=result["document_type"],
                   priority=result["priority"])
        
        return APIResponse(
            success=True,
            message=f"Document classified as {result['document_type']} with {result['priority']} priority",
            data=result
        )
        
    except FileNotFoundError as e:
        logger.warning("Document file not found", file_path=request.file_path, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document file not found: {str(e)}"
        )
    except Exception as e:
        logger.error("Document classification failed", file_path=request.file_path, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document classification failed: {str(e)}"
        )


@app.post("/api/start-workflow", response_model=APIResponse)
async def start_workflow(request: ClassifyDocumentRequest):
    """Start workflow process for document"""
    try:
        logger.info("Starting workflow", file_path=request.file_path)
        
        # First classify the document
        classification_result = await workflow_service.classify_document(
            file_path=request.file_path,
            content=request.content
        )
        
        # Start workflow based on classification
        workflow_result = await workflow_service.start_workflow(
            document_info=classification_result,
            workflow_config=classification_result["workflow_config"]
        )
        
        logger.info("Workflow started successfully", 
                   workflow_id=workflow_result["workflow_id"],
                   status=workflow_result["status"])
        
        return APIResponse(
            success=True,
            message=f"Workflow started for {classification_result['document_type']}",
            data={
                "classification": classification_result,
                "workflow": workflow_result
            }
        )
        
    except Exception as e:
        logger.error("Workflow start failed", file_path=request.file_path, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow start failed: {str(e)}"
        )


@app.post("/api/process-approval", response_model=APIResponse)
async def process_approval(request: ProcessApprovalRequest):
    """Process approval decision for workflow"""
    try:
        logger.info("Processing approval", workflow_id=request.workflow_id, decision=request.decision)
        
        result = await workflow_service.process_approval(
            workflow_id=request.workflow_id,
            approver=request.approver,
            decision=request.decision,
            comment=request.comment
        )
        
        logger.info("Approval processed successfully", 
                   workflow_id=request.workflow_id,
                   decision=request.decision,
                   new_status=result["new_status"])
        
        return APIResponse(
            success=True,
            message=f"Approval {request.decision} processed successfully",
            data=result
        )
        
    except ValueError as e:
        logger.warning("Invalid approval request", workflow_id=request.workflow_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid approval request: {str(e)}"
        )
    except Exception as e:
        logger.error("Approval processing failed", workflow_id=request.workflow_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Approval processing failed: {str(e)}"
        )


@app.get("/api/workflow-status/{workflow_id}", response_model=APIResponse)
async def get_workflow_status(workflow_id: str):
    """Get current status of workflow"""
    try:
        logger.info("Getting workflow status", workflow_id=workflow_id)
        
        result = await workflow_service.get_workflow_status(workflow_id)
        
        return APIResponse(
            success=True,
            message=f"Workflow status retrieved",
            data=result
        )
        
    except ValueError as e:
        logger.warning("Workflow not found", workflow_id=workflow_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow not found: {str(e)}"
        )
    except Exception as e:
        logger.error("Workflow status retrieval failed", workflow_id=workflow_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow status retrieval failed: {str(e)}"
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
        logger.info("Processing smart spreadsheet command", 
                   command=request.command, 
                   file_reference=request.file_reference)
        
        # Execute the intelligent spreadsheet operation
        result = await intelligent_spreadsheet_service.smart_file_operation(
            command=request.command,
            file_reference=request.file_reference
        )
        
        logger.info("Smart spreadsheet operation completed successfully",
                   command=request.command,
                   file_processed=result.get("file_analyzed"),
                   operation_type=result.get("operation_type"))
        
        return APIResponse(
            success=True,
            message=f"Smart operation completed: {result.get('operation_type', 'analysis')}",
            data=result
        )
        
    except FileNotFoundError as e:
        logger.warning("File not found for smart operation", 
                      command=request.command, 
                      error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {str(e)}"
        )
    except ValueError as e:
        logger.warning("Invalid smart spreadsheet operation", 
                      command=request.command, 
                      error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid operation: {str(e)}"
        )
    except Exception as e:
        logger.error("Smart spreadsheet operation failed", 
                    command=request.command, 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Smart operation failed: {str(e)}"
        )


@app.get("/api/pending-approvals/{approver}", response_model=APIResponse)
async def get_pending_approvals(approver: str):
    """Get pending approvals for an approver"""
    try:
        logger.info("Getting pending approvals", approver=approver)
        
        result = await workflow_service.get_pending_approvals(approver)
        
        return APIResponse(
            success=True,
            message=f"Found {result['pending_count']} pending approvals",
            data=result
        )
        
    except Exception as e:
        logger.error("Failed to get pending approvals", approver=approver, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pending approvals: {str(e)}"
        )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("Unhandled exception", 
                path=request.url.path,
                method=request.method,
                error=str(exc))
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_config=None  # We use structlog instead
    )

        
        return APIResponse(
            success=True,
            message=f"Smart operation completed: {result.get('message', 'Operation successful')}",
            data=result
        )
        
    except ValueError as e:
        logger.error("Invalid smart spreadsheet request", 
                    command=request.command, 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid operation: {str(e)}"
        )
    except Exception as e:
        logger.error("Smart spreadsheet operation failed", 
                    command=request.command, 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Smart operation failed: {str(e)}"
        )


# OCR and Document Processing Models
class OCRRequest(BaseModel):
    file_path: str = Field(..., description="Path to the document file")
    document_type: str = Field("auto", description="Type of document (auto, invoice, contract, form)")


class DocumentClassifyRequest(BaseModel):
    file_path: str = Field(..., description="Path to the document file")


@app.post("/api/extract-data", response_model=APIResponse)
async def extract_data_from_document(request: OCRRequest):
    """
    Extract structured data from documents using OCR
    
    Supports various document types including invoices, contracts, and forms.
    """
    try:
        logger.info("Starting OCR data extraction", 
                   file_path=request.file_path, 
                   document_type=request.document_type)
        
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
        logger.error("Document file not found", 
                    file_path=request.file_path, 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document file not found: {str(e)}"
        )
    except Exception as e:
        logger.error("OCR data extraction failed", 
                    file_path=request.file_path, 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data extraction failed: {str(e)}"
        )


@app.post("/api/classify-document", response_model=APIResponse)
async def classify_document(request: DocumentClassifyRequest):
    """
    Classify document type using AI analysis
    
    Automatically detects document type (invoice, contract, report, etc.)
    """
    try:
        logger.info("Starting document classification", file_path=request.file_path)
        
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
        logger.error("Document file not found", 
                    file_path=request.file_path, 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document file not found: {str(e)}"
        )
    except Exception as e:
        logger.error("Document classification failed", 
                    file_path=request.file_path, 
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document classification failed: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )