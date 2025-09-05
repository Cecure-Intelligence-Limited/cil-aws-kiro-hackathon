"""
Email Management Automation Service
Handles email sorting, template responses, and follow-up tracking
"""

import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, Any, List, Optional
import structlog
import re
from datetime import datetime, timedelta
import json

logger = structlog.get_logger(__name__)


class EmailService:
    """Service for email management automation"""
    
    def __init__(self):
        self.imap_connection = None
        self.smtp_connection = None
        self.email_rules = []
        self.templates = {}
        
    async def setup_email_connection(self, email_config: Dict[str, str]) -> Dict[str, Any]:
        """
        Setup email connection with IMAP/SMTP
        
        Args:
            email_config: Email configuration with server details
            
        Returns:
            Connection status
        """
        
        try:
            # Setup IMAP connection
            imap_server = email_config.get('imap_server')
            imap_port = email_config.get('imap_port', 993)
            username = email_config.get('username')
            password = email_config.get('password')
            
            self.imap_connection = imaplib.IMAP4_SSL(imap_server, imap_port)
            self.imap_connection.login(username, password)
            
            # Setup SMTP connection
            smtp_server = email_config.get('smtp_server')
            smtp_port = email_config.get('smtp_port', 587)
            
            self.smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
            self.smtp_connection.starttls()
            self.smtp_connection.login(username, password)
            
            logger.info("Email connections established successfully")
            
            return {
                "success": True,
                "imap_connected": True,
                "smtp_connected": True,
                "message": "Email connections established"
            }
            
        except Exception as e:
            logger.error("Email connection failed", error=str(e))
            raise ValueError(f"Failed to connect to email: {str(e)}")
    
    async def sort_emails_by_rules(self, folder: str = "INBOX") -> Dict[str, Any]:
        """
        Sort emails based on predefined rules
        
        Args:
            folder: Email folder to process
            
        Returns:
            Sorting results
        """
        
        try:
            if not self.imap_connection:
                raise ValueError("Email connection not established")
            
            # Select folder
            self.imap_connection.select(folder)
            
            # Search for unread emails
            status, messages = self.imap_connection.search(None, 'UNSEEN')
            email_ids = messages[0].split()
            
            sorted_count = 0
            results = []
            
            for email_id in email_ids:
                # Fetch email
                status, msg_data = self.imap_connection.fetch(email_id, '(RFC822)')
                email_message = email.message_from_bytes(msg_data[0][1])
                
                # Extract email details
                email_details = self._extract_email_details(email_message)
                
                # Apply sorting rules
                rule_applied = self._apply_sorting_rules(email_id, email_details)
                
                if rule_applied:
                    sorted_count += 1
                    results.append({
                        "email_id": email_id.decode(),
                        "subject": email_details["subject"],
                        "rule_applied": rule_applied
                    })
            
            logger.info("Email sorting completed",
                       total_emails=len(email_ids),
                       sorted_emails=sorted_count)
            
            return {
                "success": True,
                "total_emails": len(email_ids),
                "sorted_emails": sorted_count,
                "results": results
            }
            
        except Exception as e:
            logger.error("Email sorting failed", error=str(e))
            raise
    
    def _extract_email_details(self, email_message) -> Dict[str, Any]:
        """Extract details from email message"""
        
        details = {
            "subject": email_message.get("Subject", ""),
            "from": email_message.get("From", ""),
            "to": email_message.get("To", ""),
            "date": email_message.get("Date", ""),
            "body": ""
        }
        
        # Extract body
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    details["body"] = part.get_payload(decode=True).decode()
                    break
        else:
            details["body"] = email_message.get_payload(decode=True).decode()
        
        return details
    
    def _apply_sorting_rules(self, email_id: bytes, email_details: Dict[str, Any]) -> Optional[str]:
        """Apply sorting rules to email"""
        
        for rule in self.email_rules:
            if self._rule_matches(rule, email_details):
                # Apply rule action
                if rule["action"] == "move":
                    self._move_email(email_id, rule["target"])
                elif rule["action"] == "label":
                    self._label_email(email_id, rule["target"])
                elif rule["action"] == "forward":
                    self._forward_email(email_id, rule["target"])
                elif rule["action"] == "respond":
                    self._auto_respond(email_id, email_details, rule["target"])
                
                return rule["name"]
        
        return None
    
    def _rule_matches(self, rule: Dict[str, Any], email_details: Dict[str, Any]) -> bool:
        """Check if email matches rule conditions"""
        
        condition = rule["condition"].lower()
        subject = email_details["subject"].lower()
        sender = email_details["from"].lower()
        body = email_details["body"].lower()
        
        # Simple keyword matching
        if "subject contains" in condition:
            keyword = condition.split("subject contains")[1].strip().strip('"\'')
            return keyword in subject
        elif "from contains" in condition:
            keyword = condition.split("from contains")[1].strip().strip('"\'')
            return keyword in sender
        elif "body contains" in condition:
            keyword = condition.split("body contains")[1].strip().strip('"\'')
            return keyword in body
        
        return False
    
    def _move_email(self, email_id: bytes, folder: str):
        """Move email to specified folder"""
        try:
            self.imap_connection.move(email_id, folder)
        except Exception as e:
            logger.error("Failed to move email", email_id=email_id, folder=folder, error=str(e))
    
    def _label_email(self, email_id: bytes, label: str):
        """Add label to email (Gmail-specific)"""
        try:
            self.imap_connection.store(email_id, '+X-GM-LABELS', f'({label})')
        except Exception as e:
            logger.error("Failed to label email", email_id=email_id, label=label, error=str(e))
    
    def _forward_email(self, email_id: bytes, recipient: str):
        """Forward email to recipient"""
        try:
            # Fetch original email
            status, msg_data = self.imap_connection.fetch(email_id, '(RFC822)')
            original_email = email.message_from_bytes(msg_data[0][1])
            
            # Create forward message
            forward_msg = MIMEMultipart()
            forward_msg['Subject'] = f"Fwd: {original_email.get('Subject', '')}"
            forward_msg['To'] = recipient
            forward_msg['From'] = self.smtp_connection.user
            
            # Add original email as attachment
            forward_msg.attach(MIMEText(f"Forwarded message:\n\n{original_email.as_string()}"))
            
            # Send forward
            self.smtp_connection.send_message(forward_msg)
            
        except Exception as e:
            logger.error("Failed to forward email", email_id=email_id, recipient=recipient, error=str(e))
    
    def _auto_respond(self, email_id: bytes, email_details: Dict[str, Any], template_name: str):
        """Send auto-response using template"""
        try:
            template = self.templates.get(template_name)
            if not template:
                logger.warning("Template not found", template_name=template_name)
                return
            
            # Create response
            response = MIMEText(template["body"])
            response['Subject'] = template["subject"]
            response['To'] = email_details["from"]
            response['From'] = self.smtp_connection.user
            
            # Send response
            self.smtp_connection.send_message(response)
            
        except Exception as e:
            logger.error("Failed to send auto-response", email_id=email_id, error=str(e))
    
    async def create_email_rule(self, rule_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new email sorting rule
        
        Args:
            rule_config: Rule configuration
            
        Returns:
            Rule creation result
        """
        
        try:
            rule = {
                "name": rule_config["name"],
                "condition": rule_config["condition"],
                "action": rule_config["action"],
                "target": rule_config["target"],
                "created": datetime.now().isoformat()
            }
            
            self.email_rules.append(rule)
            
            # Save rules to file
            await self._save_email_rules()
            
            logger.info("Email rule created", rule_name=rule["name"])
            
            return {
                "success": True,
                "rule_id": len(self.email_rules) - 1,
                "rule_name": rule["name"],
                "message": "Email rule created successfully"
            }
            
        except Exception as e:
            logger.error("Failed to create email rule", error=str(e))
            raise
    
    async def create_email_template(self, template_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create email response template
        
        Args:
            template_config: Template configuration
            
        Returns:
            Template creation result
        """
        
        try:
            template = {
                "name": template_config["name"],
                "subject": template_config["subject"],
                "body": template_config["body"],
                "created": datetime.now().isoformat()
            }
            
            self.templates[template["name"]] = template
            
            # Save templates to file
            await self._save_email_templates()
            
            logger.info("Email template created", template_name=template["name"])
            
            return {
                "success": True,
                "template_name": template["name"],
                "message": "Email template created successfully"
            }
            
        except Exception as e:
            logger.error("Failed to create email template", error=str(e))
            raise
    
    async def track_follow_ups(self) -> Dict[str, Any]:
        """
        Track emails requiring follow-up
        
        Returns:
            Follow-up tracking results
        """
        
        try:
            if not self.imap_connection:
                raise ValueError("Email connection not established")
            
            # Search for emails from last 7 days that might need follow-up
            cutoff_date = (datetime.now() - timedelta(days=7)).strftime("%d-%b-%Y")
            
            self.imap_connection.select("SENT")
            status, messages = self.imap_connection.search(None, f'SINCE {cutoff_date}')
            
            sent_emails = messages[0].split()
            follow_ups_needed = []
            
            for email_id in sent_emails:
                # Fetch sent email
                status, msg_data = self.imap_connection.fetch(email_id, '(RFC822)')
                email_message = email.message_from_bytes(msg_data[0][1])
                
                email_details = self._extract_email_details(email_message)
                
                # Check if follow-up is needed (simple heuristic)
                if self._needs_follow_up(email_details):
                    follow_ups_needed.append({
                        "subject": email_details["subject"],
                        "to": email_details["to"],
                        "date": email_details["date"],
                        "days_since": self._days_since_sent(email_details["date"])
                    })
            
            logger.info("Follow-up tracking completed",
                       total_sent=len(sent_emails),
                       follow_ups_needed=len(follow_ups_needed))
            
            return {
                "success": True,
                "total_sent_emails": len(sent_emails),
                "follow_ups_needed": len(follow_ups_needed),
                "follow_up_list": follow_ups_needed
            }
            
        except Exception as e:
            logger.error("Follow-up tracking failed", error=str(e))
            raise
    
    def _needs_follow_up(self, email_details: Dict[str, Any]) -> bool:
        """Determine if email needs follow-up"""
        
        subject = email_details["subject"].lower()
        body = email_details["body"].lower()
        
        # Keywords that suggest follow-up needed
        follow_up_keywords = [
            "please respond", "need response", "waiting for", "follow up",
            "deadline", "urgent", "asap", "meeting request", "proposal"
        ]
        
        return any(keyword in subject or keyword in body for keyword in follow_up_keywords)
    
    def _days_since_sent(self, date_str: str) -> int:
        """Calculate days since email was sent"""
        try:
            # Parse email date (simplified)
            email_date = datetime.strptime(date_str.split(',')[1].strip()[:11], "%d %b %Y")
            return (datetime.now() - email_date).days
        except:
            return 0
    
    async def _save_email_rules(self):
        """Save email rules to file"""
        try:
            rules_file = Path("backend/data/email_rules.json")
            rules_file.parent.mkdir(exist_ok=True)
            
            with open(rules_file, 'w') as f:
                json.dump(self.email_rules, f, indent=2)
        except Exception as e:
            logger.error("Failed to save email rules", error=str(e))
    
    async def _save_email_templates(self):
        """Save email templates to file"""
        try:
            templates_file = Path("backend/data/email_templates.json")
            templates_file.parent.mkdir(exist_ok=True)
            
            with open(templates_file, 'w') as f:
                json.dump(self.templates, f, indent=2)
        except Exception as e:
            logger.error("Failed to save email templates", error=str(e))
    
    async def load_email_rules(self):
        """Load email rules from file"""
        try:
            rules_file = Path("backend/data/email_rules.json")
            if rules_file.exists():
                with open(rules_file, 'r') as f:
                    self.email_rules = json.load(f)
        except Exception as e:
            logger.error("Failed to load email rules", error=str(e))
    
    async def load_email_templates(self):
        """Load email templates from file"""
        try:
            templates_file = Path("backend/data/email_templates.json")
            if templates_file.exists():
                with open(templates_file, 'r') as f:
                    self.templates = json.load(f)
        except Exception as e:
            logger.error("Failed to load email templates", error=str(e))