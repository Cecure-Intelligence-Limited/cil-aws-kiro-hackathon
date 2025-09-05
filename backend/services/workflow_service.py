"""
Document Workflow Processing Service
Handles document classification, approval workflows, and automated routing
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import structlog
import json
from datetime import datetime, timedelta
from enum import Enum
import hashlib

logger = structlog.get_logger(__name__)


class WorkflowStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class WorkflowService:
    """Service for document workflow processing and automation"""
    
    def __init__(self):
        self.workflows = []
        self.document_types = {}
        self.approval_rules = {}
        self.processed_documents = []
        
    async def classify_document(self, file_path: str, content: str = None) -> Dict[str, Any]:
        """
        Classify document type and determine workflow
        
        Args:
            file_path: Path to document file
            content: Optional document content (if already extracted)
            
        Returns:
            Document classification and workflow assignment
        """
        
        try:
            path = Path(file_path)
            
            if not path.exists():
                raise FileNotFoundError(f"Document not found: {file_path}")
            
            # Extract content if not provided
            if not content:
                content = await self._extract_document_content(path)
            
            # Classify document type
            document_type = self._classify_document_type(content, path.name)
            
            # Determine workflow based on document type
            workflow_config = self._get_workflow_config(document_type)
            
            # Calculate priority
            priority = self._calculate_document_priority(content, document_type)
            
            # Generate document metadata
            metadata = self._generate_document_metadata(path, content, document_type)
            
            logger.info("Document classified",
                       file_path=file_path,
                       document_type=document_type,
                       priority=priority.value,
                       workflow=workflow_config["name"])
            
            return {
                "success": True,
                "file_path": file_path,
                "document_type": document_type,
                "priority": priority.value,
                "workflow_config": workflow_config,
                "metadata": metadata,
                "classification_confidence": self._calculate_classification_confidence(content, document_type)
            }
            
        except Exception as e:
            logger.error("Document classification failed", file_path=file_path, error=str(e))
            raise
    
    async def _extract_document_content(self, file_path: Path) -> str:
        """Extract text content from document"""
        
        try:
            if file_path.suffix.lower() == '.pdf':
                # Use OCR service for PDF extraction
                from .ocr_service import OCRService
                ocr_service = OCRService()
                result = await ocr_service.extract_data_from_document(str(file_path))
                return result.get("raw_text", "")
                
            elif file_path.suffix.lower() in ['.txt', '.md']:
                # Plain text files
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
                    
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                # Word documents (simplified - would need python-docx)
                return f"Word document: {file_path.name}"
                
            else:
                return f"Binary document: {file_path.name}"
                
        except Exception as e:
            logger.error("Content extraction failed", file_path=str(file_path), error=str(e))
            return f"Content extraction failed: {str(e)}"
    
    def _classify_document_type(self, content: str, filename: str) -> str:
        """Classify document based on content and filename"""
        
        content_lower = content.lower()
        filename_lower = filename.lower()
        
        # Invoice classification
        invoice_keywords = ['invoice', 'bill', 'amount due', 'payment terms', 'invoice number']
        if any(keyword in content_lower for keyword in invoice_keywords) or 'invoice' in filename_lower:
            return "invoice"
        
        # Contract classification
        contract_keywords = ['agreement', 'contract', 'terms and conditions', 'party', 'whereas', 'signature']
        if any(keyword in content_lower for keyword in contract_keywords) or 'contract' in filename_lower:
            return "contract"
        
        # Purchase order classification
        po_keywords = ['purchase order', 'po number', 'vendor', 'delivery date', 'order total']
        if any(keyword in content_lower for keyword in po_keywords) or 'purchase' in filename_lower:
            return "purchase_order"
        
        # Receipt classification
        receipt_keywords = ['receipt', 'transaction', 'thank you for your purchase', 'total paid']
        if any(keyword in content_lower for keyword in receipt_keywords) or 'receipt' in filename_lower:
            return "receipt"
        
        # Report classification
        report_keywords = ['report', 'analysis', 'summary', 'findings', 'recommendations']
        if any(keyword in content_lower for keyword in report_keywords) or 'report' in filename_lower:
            return "report"
        
        # Form classification
        form_keywords = ['application', 'form', 'please fill', 'signature required', 'submit']
        if any(keyword in content_lower for keyword in form_keywords) or 'form' in filename_lower:
            return "form"
        
        # Proposal classification
        proposal_keywords = ['proposal', 'quotation', 'estimate', 'scope of work', 'project timeline']
        if any(keyword in content_lower for keyword in proposal_keywords) or 'proposal' in filename_lower:
            return "proposal"
        
        return "general_document"
    
    def _get_workflow_config(self, document_type: str) -> Dict[str, Any]:
        """Get workflow configuration for document type"""
        
        workflow_configs = {
            "invoice": {
                "name": "Invoice Processing",
                "steps": ["finance_review", "manager_approval", "payment_processing"],
                "approvers": ["finance_team", "finance_manager"],
                "auto_approve_threshold": 1000.00,
                "sla_hours": 48
            },
            "contract": {
                "name": "Contract Review",
                "steps": ["legal_review", "business_approval", "signature_collection"],
                "approvers": ["legal_team", "business_manager", "executive"],
                "auto_approve_threshold": None,
                "sla_hours": 120
            },
            "purchase_order": {
                "name": "Purchase Order Processing",
                "steps": ["procurement_review", "budget_approval", "vendor_notification"],
                "approvers": ["procurement_team", "budget_manager"],
                "auto_approve_threshold": 5000.00,
                "sla_hours": 24
            },
            "receipt": {
                "name": "Expense Processing",
                "steps": ["expense_validation", "manager_approval"],
                "approvers": ["expense_team", "manager"],
                "auto_approve_threshold": 500.00,
                "sla_hours": 24
            },
            "proposal": {
                "name": "Proposal Review",
                "steps": ["technical_review", "business_review", "pricing_approval"],
                "approvers": ["technical_lead", "business_manager", "sales_director"],
                "auto_approve_threshold": None,
                "sla_hours": 72
            },
            "form": {
                "name": "Form Processing",
                "steps": ["data_validation", "processing", "notification"],
                "approvers": ["admin_team"],
                "auto_approve_threshold": None,
                "sla_hours": 8
            }
        }
        
        return workflow_configs.get(document_type, {
            "name": "General Document Review",
            "steps": ["review", "approval"],
            "approvers": ["manager"],
            "auto_approve_threshold": None,
            "sla_hours": 48
        })
    
    def _calculate_document_priority(self, content: str, document_type: str) -> Priority:
        """Calculate document priority based on content and type"""
        
        content_lower = content.lower()
        
        # Urgent keywords
        urgent_keywords = ['urgent', 'asap', 'immediate', 'emergency', 'critical', 'deadline today']
        if any(keyword in content_lower for keyword in urgent_keywords):
            return Priority.URGENT
        
        # High priority keywords
        high_keywords = ['high priority', 'important', 'deadline', 'time sensitive']
        if any(keyword in content_lower for keyword in high_keywords):
            return Priority.HIGH
        
        # Document type based priority
        if document_type in ['invoice', 'purchase_order']:
            # Check for large amounts
            import re
            amounts = re.findall(r'\$?([0-9,]+\.?[0-9]*)', content)
            for amount_str in amounts:
                try:
                    amount = float(amount_str.replace(',', ''))
                    if amount > 10000:
                        return Priority.HIGH
                    elif amount > 5000:
                        return Priority.MEDIUM
                except ValueError:
                    continue
        
        if document_type == 'contract':
            return Priority.HIGH  # Contracts are generally high priority
        
        return Priority.MEDIUM  # Default priority
    
    def _generate_document_metadata(self, file_path: Path, content: str, document_type: str) -> Dict[str, Any]:
        """Generate metadata for document"""
        
        # Calculate content hash for duplicate detection
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # Extract key information based on document type
        extracted_info = self._extract_key_information(content, document_type)
        
        metadata = {
            "filename": file_path.name,
            "file_size": file_path.stat().st_size if file_path.exists() else 0,
            "file_extension": file_path.suffix,
            "content_hash": content_hash,
            "word_count": len(content.split()),
            "character_count": len(content),
            "created_at": datetime.now().isoformat(),
            "document_type": document_type,
            "extracted_info": extracted_info
        }
        
        return metadata
    
    def _extract_key_information(self, content: str, document_type: str) -> Dict[str, Any]:
        """Extract key information based on document type"""
        
        import re
        
        info = {}
        
        # Extract dates
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{4}-\d{2}-\d{2})',
            r'([A-Za-z]+ \d{1,2}, \d{4})'
        ]
        
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, content))
        
        if dates:
            info['dates'] = dates[:5]  # Limit to first 5 dates
        
        # Extract amounts
        amount_patterns = [
            r'\$([0-9,]+\.?[0-9]*)',
            r'([0-9,]+\.?[0-9]*)\s*dollars?',
            r'total[:\s]*\$?([0-9,]+\.?[0-9]*)'
        ]
        
        amounts = []
        for pattern in amount_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            amounts.extend(matches)
        
        if amounts:
            try:
                numeric_amounts = [float(amt.replace(',', '')) for amt in amounts if amt.replace(',', '').replace('.', '').isdigit()]
                info['amounts'] = numeric_amounts[:5]  # Limit to first 5 amounts
            except ValueError:
                pass
        
        # Extract emails
        email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        emails = re.findall(email_pattern, content)
        if emails:
            info['emails'] = emails[:3]  # Limit to first 3 emails
        
        # Extract phone numbers
        phone_pattern = r'([0-9]{3}[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})'
        phones = re.findall(phone_pattern, content)
        if phones:
            info['phone_numbers'] = phones[:3]  # Limit to first 3 phone numbers\n        \n        # Document type specific extraction\n        if document_type == 'invoice':\n            invoice_number = re.search(r'invoice\\s*#?\\s*:?\\s*([A-Z0-9\\-]+)', content, re.IGNORECASE)\n            if invoice_number:\n                info['invoice_number'] = invoice_number.group(1)\n        \n        elif document_type == 'contract':\n            parties = re.findall(r'between\\s+([^,\\n]+)\\s+and\\s+([^,\\n]+)', content, re.IGNORECASE)\n            if parties:\n                info['contract_parties'] = parties[0]\n        \n        return info\n    \n    def _calculate_classification_confidence(self, content: str, document_type: str) -> float:\n        \"\"\"Calculate confidence score for document classification\"\"\"\n        \n        # Simple confidence calculation based on keyword matches\n        type_keywords = {\n            'invoice': ['invoice', 'bill', 'amount due', 'payment terms'],\n            'contract': ['agreement', 'contract', 'terms', 'signature'],\n            'purchase_order': ['purchase order', 'po number', 'vendor'],\n            'receipt': ['receipt', 'transaction', 'total paid'],\n            'proposal': ['proposal', 'quotation', 'scope of work'],\n            'form': ['application', 'form', 'please fill']\n        }\n        \n        keywords = type_keywords.get(document_type, [])\n        if not keywords:\n            return 0.5  # Default confidence for unknown types\n        \n        content_lower = content.lower()\n        matches = sum(1 for keyword in keywords if keyword in content_lower)\n        \n        confidence = min(0.5 + (matches * 0.15), 0.95)  # Scale from 0.5 to 0.95\n        return confidence\n    \n    async def start_workflow(self, document_info: Dict[str, Any], workflow_config: Dict[str, Any]) -> Dict[str, Any]:\n        \"\"\"Start workflow process for document\"\"\"\n        \n        try:\n            workflow_id = f\"workflow_{int(datetime.now().timestamp())}\"\n            \n            workflow = {\n                \"id\": workflow_id,\n                \"document_info\": document_info,\n                \"config\": workflow_config,\n                \"status\": WorkflowStatus.PENDING.value,\n                \"current_step\": 0,\n                \"steps\": workflow_config[\"steps\"],\n                \"approvers\": workflow_config[\"approvers\"],\n                \"created_at\": datetime.now().isoformat(),\n                \"updated_at\": datetime.now().isoformat(),\n                \"sla_deadline\": (datetime.now() + timedelta(hours=workflow_config[\"sla_hours\"])).isoformat(),\n                \"approval_history\": [],\n                \"comments\": []\n            }\n            \n            # Check for auto-approval\n            if await self._check_auto_approval(document_info, workflow_config):\n                workflow[\"status\"] = WorkflowStatus.APPROVED.value\n                workflow[\"approval_history\"].append({\n                    \"step\": \"auto_approval\",\n                    \"approver\": \"system\",\n                    \"decision\": \"approved\",\n                    \"timestamp\": datetime.now().isoformat(),\n                    \"comment\": \"Auto-approved based on predefined criteria\"\n                })\n            else:\n                # Start first step\n                workflow[\"status\"] = WorkflowStatus.IN_PROGRESS.value\n                await self._notify_approvers(workflow, 0)\n            \n            self.workflows.append(workflow)\n            await self._save_workflows()\n            \n            logger.info(\"Workflow started\",\n                       workflow_id=workflow_id,\n                       document_type=document_info[\"document_type\"],\n                       status=workflow[\"status\"])\n            \n            return {\n                \"success\": True,\n                \"workflow_id\": workflow_id,\n                \"status\": workflow[\"status\"],\n                \"current_step\": workflow[\"current_step\"],\n                \"sla_deadline\": workflow[\"sla_deadline\"],\n                \"message\": \"Workflow started successfully\"\n            }\n            \n        except Exception as e:\n            logger.error(\"Failed to start workflow\", error=str(e))\n            raise\n    \n    async def _check_auto_approval(self, document_info: Dict[str, Any], workflow_config: Dict[str, Any]) -> bool:\n        \"\"\"Check if document qualifies for auto-approval\"\"\"\n        \n        auto_approve_threshold = workflow_config.get(\"auto_approve_threshold\")\n        \n        if auto_approve_threshold is None:\n            return False\n        \n        # Check document amounts against threshold\n        extracted_info = document_info.get(\"metadata\", {}).get(\"extracted_info\", {})\n        amounts = extracted_info.get(\"amounts\", [])\n        \n        if amounts:\n            max_amount = max(amounts)\n            return max_amount <= auto_approve_threshold\n        \n        return False\n    \n    async def _notify_approvers(self, workflow: Dict[str, Any], step_index: int):\n        \"\"\"Notify approvers for current workflow step\"\"\"\n        \n        try:\n            if step_index >= len(workflow[\"approvers\"]):\n                return\n            \n            approver = workflow[\"approvers\"][step_index]\n            step_name = workflow[\"steps\"][step_index]\n            \n            # In real implementation, this would send actual notifications\n            logger.info(\"Approval notification sent\",\n                       workflow_id=workflow[\"id\"],\n                       step=step_name,\n                       approver=approver)\n            \n        except Exception as e:\n            logger.error(\"Failed to notify approvers\", error=str(e))\n    \n    async def process_approval(self, workflow_id: str, approver: str, decision: str, comment: str = \"\") -> Dict[str, Any]:\n        \"\"\"Process approval decision for workflow step\"\"\"\n        \n        try:\n            workflow = next((w for w in self.workflows if w[\"id\"] == workflow_id), None)\n            if not workflow:\n                raise ValueError(f\"Workflow {workflow_id} not found\")\n            \n            if workflow[\"status\"] not in [WorkflowStatus.PENDING.value, WorkflowStatus.IN_PROGRESS.value]:\n                raise ValueError(f\"Workflow {workflow_id} is not in a state that allows approval\")\n            \n            # Record approval decision\n            approval_record = {\n                \"step\": workflow[\"steps\"][workflow[\"current_step\"]],\n                \"approver\": approver,\n                \"decision\": decision,\n                \"timestamp\": datetime.now().isoformat(),\n                \"comment\": comment\n            }\n            \n            workflow[\"approval_history\"].append(approval_record)\n            workflow[\"updated_at\"] = datetime.now().isoformat()\n            \n            if decision == \"approved\":\n                # Move to next step\n                workflow[\"current_step\"] += 1\n                \n                if workflow[\"current_step\"] >= len(workflow[\"steps\"]):\n                    # Workflow completed\n                    workflow[\"status\"] = WorkflowStatus.COMPLETED.value\n                    await self._complete_workflow(workflow)\n                else:\n                    # Continue to next step\n                    await self._notify_approvers(workflow, workflow[\"current_step\"])\n                    \n            elif decision == \"rejected\":\n                workflow[\"status\"] = WorkflowStatus.REJECTED.value\n                await self._handle_workflow_rejection(workflow)\n            \n            await self._save_workflows()\n            \n            logger.info(\"Approval processed\",\n                       workflow_id=workflow_id,\n                       decision=decision,\n                       approver=approver,\n                       new_status=workflow[\"status\"])\n            \n            return {\n                \"success\": True,\n                \"workflow_id\": workflow_id,\n                \"decision\": decision,\n                \"new_status\": workflow[\"status\"],\n                \"current_step\": workflow[\"current_step\"],\n                \"message\": f\"Approval {decision} processed successfully\"\n            }\n            \n        except Exception as e:\n            logger.error(\"Failed to process approval\", workflow_id=workflow_id, error=str(e))\n            raise\n    \n    async def _complete_workflow(self, workflow: Dict[str, Any]):\n        \"\"\"Handle workflow completion\"\"\"\n        \n        try:\n            # Archive document\n            await self._archive_document(workflow)\n            \n            # Send completion notifications\n            logger.info(\"Workflow completed\",\n                       workflow_id=workflow[\"id\"],\n                       document_type=workflow[\"document_info\"][\"document_type\"])\n            \n        except Exception as e:\n            logger.error(\"Failed to complete workflow\", error=str(e))\n    \n    async def _handle_workflow_rejection(self, workflow: Dict[str, Any]):\n        \"\"\"Handle workflow rejection\"\"\"\n        \n        try:\n            # Notify document submitter\n            logger.info(\"Workflow rejected\",\n                       workflow_id=workflow[\"id\"],\n                       document_type=workflow[\"document_info\"][\"document_type\"])\n            \n        except Exception as e:\n            logger.error(\"Failed to handle workflow rejection\", error=str(e))\n    \n    async def _archive_document(self, workflow: Dict[str, Any]):\n        \"\"\"Archive completed document\"\"\"\n        \n        try:\n            document_info = workflow[\"document_info\"]\n            \n            archived_document = {\n                \"workflow_id\": workflow[\"id\"],\n                \"document_info\": document_info,\n                \"final_status\": workflow[\"status\"],\n                \"approval_history\": workflow[\"approval_history\"],\n                \"archived_at\": datetime.now().isoformat(),\n                \"retention_until\": (datetime.now() + timedelta(days=2555)).isoformat()  # 7 years\n            }\n            \n            self.processed_documents.append(archived_document)\n            \n            # Save to archive\n            archive_file = Path(\"backend/data/document_archive.json\")\n            archive_file.parent.mkdir(exist_ok=True)\n            \n            with open(archive_file, 'w') as f:\n                json.dump(self.processed_documents, f, indent=2, default=str)\n            \n            logger.info(\"Document archived\",\n                       workflow_id=workflow[\"id\"],\n                       document_type=document_info[\"document_type\"])\n            \n        except Exception as e:\n            logger.error(\"Failed to archive document\", error=str(e))\n    \n    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:\n        \"\"\"Get current status of workflow\"\"\"\n        \n        try:\n            workflow = next((w for w in self.workflows if w[\"id\"] == workflow_id), None)\n            if not workflow:\n                raise ValueError(f\"Workflow {workflow_id} not found\")\n            \n            # Calculate progress percentage\n            progress = (workflow[\"current_step\"] / len(workflow[\"steps\"])) * 100\n            \n            # Check SLA status\n            sla_deadline = datetime.fromisoformat(workflow[\"sla_deadline\"])\n            is_overdue = datetime.now() > sla_deadline\n            \n            return {\n                \"success\": True,\n                \"workflow_id\": workflow_id,\n                \"status\": workflow[\"status\"],\n                \"current_step\": workflow[\"current_step\"],\n                \"total_steps\": len(workflow[\"steps\"]),\n                \"progress_percentage\": progress,\n                \"sla_deadline\": workflow[\"sla_deadline\"],\n                \"is_overdue\": is_overdue,\n                \"approval_history\": workflow[\"approval_history\"],\n                \"document_info\": workflow[\"document_info\"]\n            }\n            \n        except Exception as e:\n            logger.error(\"Failed to get workflow status\", workflow_id=workflow_id, error=str(e))\n            raise\n    \n    async def get_pending_approvals(self, approver: str) -> Dict[str, Any]:\n        \"\"\"Get list of pending approvals for an approver\"\"\"\n        \n        try:\n            pending_workflows = []\n            \n            for workflow in self.workflows:\n                if (workflow[\"status\"] == WorkflowStatus.IN_PROGRESS.value and \n                    workflow[\"current_step\"] < len(workflow[\"approvers\"]) and\n                    workflow[\"approvers\"][workflow[\"current_step\"]] == approver):\n                    \n                    pending_workflows.append({\n                        \"workflow_id\": workflow[\"id\"],\n                        \"document_type\": workflow[\"document_info\"][\"document_type\"],\n                        \"priority\": workflow[\"document_info\"][\"priority\"],\n                        \"current_step\": workflow[\"steps\"][workflow[\"current_step\"]],\n                        \"sla_deadline\": workflow[\"sla_deadline\"],\n                        \"created_at\": workflow[\"created_at\"]\n                    })\n            \n            # Sort by priority and SLA deadline\n            pending_workflows.sort(key=lambda x: (x[\"priority\"], x[\"sla_deadline\"]))\n            \n            return {\n                \"success\": True,\n                \"approver\": approver,\n                \"pending_count\": len(pending_workflows),\n                \"pending_workflows\": pending_workflows\n            }\n            \n        except Exception as e:\n            logger.error(\"Failed to get pending approvals\", approver=approver, error=str(e))\n            raise\n    \n    async def _save_workflows(self):\n        \"\"\"Save workflows to file\"\"\"\n        try:\n            workflows_file = Path(\"backend/data/workflows.json\")\n            workflows_file.parent.mkdir(exist_ok=True)\n            \n            with open(workflows_file, 'w') as f:\n                json.dump(self.workflows, f, indent=2, default=str)\n                \n        except Exception as e:\n            logger.error(\"Failed to save workflows\", error=str(e))\n    \n    async def load_workflows(self):\n        \"\"\"Load workflows from file\"\"\"\n        try:\n            workflows_file = Path(\"backend/data/workflows.json\")\n            if workflows_file.exists():\n                with open(workflows_file, 'r') as f:\n                    self.workflows = json.load(f)\n        except Exception as e:\n            logger.error(\"Failed to load workflows\", error=str(e))"