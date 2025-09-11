"""
INTELLIGENT SPREADSHEET SERVICE - THE WOW FACTOR
Reads, analyzes, and updates ANY spreadsheet with natural language commands
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import structlog
import re
import json
import time
from datetime import datetime
import shutil

logger = structlog.get_logger(__name__)


class IntelligentSpreadsheetService:
    """AI-powered spreadsheet service that understands natural language"""
    
    def __init__(self):
        self.supported_formats = {
            '.csv': self._read_csv,
            '.xlsx': self._read_excel,
            '.xls': self._read_excel,
            '.ods': self._read_ods
        }
        self.loaded_files = {}  # Cache for loaded spreadsheets
    
    async def smart_file_operation(self, command: str, file_reference: str = None) -> Dict[str, Any]:
        """
        THE WOW FACTOR: Process natural language commands on specific files
        
        Examples:
        - "Read payroll.xlsx and calculate total salaries"
        - "Update fortune500-payroll.csv with 15% salary increase"
        - "Analyze global-sales.csv and show top performers"
        """
        
        try:
            # Extract file name from command or use provided reference
            file_path = self._extract_file_reference(command, file_reference)
            
            # Load and cache the spreadsheet
            df, file_info = await self._smart_load_file(file_path)
            
            # Analyze the command to determine operation
            operation_type = self._analyze_command_intent(command)
            
            # Execute the intelligent operation
            result = await self._execute_smart_operation(df, command, operation_type, file_path)
            
            # Add file context to result
            result.update({
                "file_analyzed": str(file_path),
                "file_info": file_info,
                "command_processed": command,
                "operation_type": operation_type
            })
            
            return result
            
        except Exception as e:
            logger.error("Smart file operation failed", command=command, error=str(e))
            raise
    
    def _extract_file_reference(self, command: str, file_reference: str = None) -> Path:
        """Extract file reference from natural language command with intelligent matching"""
        
        if file_reference:
            return self._resolve_file_path(file_reference)
        
        import structlog
        logger = structlog.get_logger(__name__)
        logger.info("Extracting file reference from command", command=command)
        
        # Enhanced file patterns - more comprehensive matching
        file_patterns = [
            # Direct file mentions with extensions
            r'(?:in|from|file|sheet|document|analyze|read|open|load)\s+["\']?([^"\'\\s]+\.(?:csv|xlsx|xls|ods))["\']?',
            r'["\']([^"\']+\.(?:csv|xlsx|xls|ods))["\']',
            r'(\w+[-_]?\w*\.(?:csv|xlsx|xls|ods))',
            
            # Specific file name patterns (without extension, we'll add .csv)
            r'(?:the\s+)?(?:file\s+)?(?:called\s+)?(fortune500[-_]?payroll)',
            r'(?:the\s+)?(?:file\s+)?(?:called\s+)?(global[-_]?sales)',
            r'(?:the\s+)?(?:file\s+)?(?:called\s+)?(demo[-_]?payroll)',
            r'(?:the\s+)?(?:file\s+)?(?:called\s+)?(ai[-_]?projects)',
            r'(?:the\s+)?(?:file\s+)?(?:called\s+)?(sample[-_]?budget)',
            
            # Keyword-based matching
            r'(?:fortune\s*500|fortune500)',  # -> fortune500-payroll.csv
            r'(?:global\s*sales|globalsales)',  # -> global-sales.csv
            r'(?:payroll|employee\s*data)',  # -> demo-payroll.csv or fortune500-payroll.csv
            r'(?:ai\s*projects|artificial\s*intelligence)',  # -> ai-projects.csv
            r'(?:budget|financial\s*data)',  # -> sample-budget.csv
            r'(?:sales\s*data|revenue)',  # -> global-sales.csv
        ]
        
        # Try to match patterns
        for i, pattern in enumerate(file_patterns):
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                matched_text = match.group(1) if match.groups() else match.group(0)
                logger.info("Pattern matched", pattern_index=i, matched_text=matched_text)
                
                # Handle different types of matches
                if '.' in matched_text:
                    # Already has extension
                    filename = matched_text
                else:
                    # Add .csv extension and normalize
                    filename = matched_text.lower().replace(' ', '-').replace('_', '-')
                    if not filename.endswith('.csv'):
                        filename += '.csv'
                
                # Try to resolve the file
                resolved_path = self._resolve_file_path(filename)
                if resolved_path.exists():
                    logger.info("File found", filename=filename, path=str(resolved_path))
                    return resolved_path
                
                # Try alternative naming patterns
                alternatives = [
                    filename,
                    f"demo-{filename}",
                    f"sample-{filename}",
                    filename.replace('-', '_'),
                    filename.replace('_', '-')
                ]
                
                for alt in alternatives:
                    alt_path = self._resolve_file_path(alt)
                    if alt_path.exists():
                        logger.info("Alternative file found", alternative=alt, path=str(alt_path))
                        return alt_path
        
        # If no specific file found, try to find the most relevant file based on keywords
        keyword_mappings = {
            'fortune': 'fortune500-payroll.csv',
            'global': 'global-sales.csv',
            'sales': 'global-sales.csv',
            'payroll': 'demo-payroll.csv',
            'ai': 'ai-projects.csv',
            'budget': 'sample-budget.csv',
            'revenue': 'global-sales.csv',
            'compensation': 'fortune500-payroll.csv',
            'employee': 'demo-payroll.csv'
        }
        
        command_lower = command.lower()
        for keyword, filename in keyword_mappings.items():
            if keyword in command_lower:
                file_path = self._resolve_file_path(filename)
                if file_path.exists():
                    logger.info("Keyword-based file found", keyword=keyword, filename=filename)
                    return file_path
        
        # Last resort: list available files and pick the first CSV
        docs_path = Path("backend/documents")
        if docs_path.exists():
            csv_files = list(docs_path.glob("*.csv"))
            if csv_files:
                logger.warning("No specific file found, using first available CSV", file=str(csv_files[0]))
                return csv_files[0]
        
        # Final fallback
        logger.error("No suitable file found, falling back to sample-budget.csv")
        return self._resolve_file_path("sample-budget.csv")
    
    def _resolve_file_path(self, filename: str) -> Path:
        """Resolve file path in common locations"""
        
        search_locations = [
            Path("backend/documents") / filename,
            Path("documents") / filename,
            Path(filename),
            Path("backend/documents") / f"sample-{filename}",
            Path("backend/documents") / f"demo-{filename}",
        ]
        
        for location in search_locations:
            if location.exists():
                return location
        
        # If not found, return the most likely location
        return Path("backend/documents") / filename
    
    async def _smart_load_file(self, file_path: Path) -> tuple[pd.DataFrame, Dict[str, Any]]:
        """Load spreadsheet with intelligent format detection"""
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get file extension
        ext = file_path.suffix.lower()
        
        if ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {ext}")
        
        # Load the file
        df = self.supported_formats[ext](file_path)
        
        # Generate file intelligence
        file_info = {
            "filename": file_path.name,
            "size_mb": round(file_path.stat().st_size / (1024 * 1024), 2),
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "numeric_columns": list(df.select_dtypes(include=[np.number]).columns),
            "text_columns": list(df.select_dtypes(include=['object']).columns),
            "sample_data": df.head(3).to_dict('records'),
            "summary_stats": self._generate_summary_stats(df)
        }
        
        # Cache the loaded file
        self.loaded_files[str(file_path)] = {
            "dataframe": df,
            "info": file_info,
            "loaded_at": datetime.now()
        }
        
        return df, file_info
    
    def _analyze_command_intent(self, command: str) -> str:
        """Analyze natural language to determine operation intent"""
        
        cmd_lower = command.lower()
        
        # Analysis operations
        if any(word in cmd_lower for word in ['calculate', 'sum', 'total', 'analyze', 'show']):
            if any(word in cmd_lower for word in ['top', 'best', 'highest', 'maximum']):
                return 'top_analysis'
            elif any(word in cmd_lower for word in ['average', 'mean', 'avg']):
                return 'average_analysis'
            else:
                return 'sum_analysis'
        
        # Update operations
        elif any(word in cmd_lower for word in ['update', 'increase', 'decrease', 'modify', 'change']):
            if any(word in cmd_lower for word in ['salary', 'pay', 'compensation']):
                return 'salary_update'
            elif any(word in cmd_lower for word in ['bonus', 'incentive']):
                return 'bonus_update'
            else:
                return 'general_update'
        
        # Read operations
        elif any(word in cmd_lower for word in ['read', 'load', 'open', 'display']):
            return 'read_analysis'
        
        # Default to analysis
        return 'smart_analysis'
    
    async def _execute_smart_operation(self, df: pd.DataFrame, command: str, operation_type: str, file_path: Path) -> Dict[str, Any]:
        """Execute the intelligent operation based on command analysis"""
        
        if operation_type == 'sum_analysis':
            return await self._smart_sum_analysis(df, command)
        
        elif operation_type == 'top_analysis':
            return await self._smart_top_analysis(df, command)
        
        elif operation_type == 'average_analysis':
            return await self._smart_average_analysis(df, command)
        
        elif operation_type in ['salary_update', 'bonus_update', 'general_update']:
            return await self._smart_update_operation(df, command, operation_type, file_path)
        
        elif operation_type == 'read_analysis':
            return await self._smart_read_analysis(df, command)
        
        else:
            return await self._smart_comprehensive_analysis(df, command)
    
    async def _smart_sum_analysis(self, df: pd.DataFrame, command: str) -> Dict[str, Any]:
        """Intelligent sum analysis based on command context"""
        
        # Identify target columns based on command
        target_columns = self._identify_target_columns(df, command)
        
        results = {}
        employee_details = []
        
        # Get employee/record details for display
        name_columns = [col for col in df.columns if any(word in col.lower() for word in ['name', 'employee', 'rep', 'person'])]
        
        for col in target_columns:
            if df[col].dtype in ['int64', 'float64']:
                total = df[col].sum()
                results[col] = {
                    "total": float(total),
                    "count": len(df[col].dropna()),
                    "average": float(df[col].mean()),
                    "formatted_total": f"${total:,.2f}" if 'salary' in col.lower() or 'pay' in col.lower() or 'revenue' in col.lower() else f"{total:,.2f}"
                }
                
                # Get top 5 records for this column
                top_records = df.nlargest(5, col)
                for _, row in top_records.iterrows():
                    employee_detail = {}
                    if name_columns:
                        employee_detail['name'] = row[name_columns[0]]
                    employee_detail[col] = f"${row[col]:,.2f}" if 'salary' in col.lower() or 'pay' in col.lower() or 'revenue' in col.lower() else f"{row[col]:,.2f}"
                    
                    # Add other relevant columns
                    for other_col in ['Position', 'Department', 'Region', 'Country']:
                        if other_col in df.columns:
                            employee_detail[other_col] = row[other_col]
                    
                    employee_details.append(employee_detail)
        
        return {
            "operation": "intelligent_sum_analysis",
            "results": results,
            "employee_details": employee_details[:10],  # Show top 10
            "total_records": len(df),
            "insights": self._generate_insights(df, results),
            "success": True
        }
    
    async def _smart_top_analysis(self, df: pd.DataFrame, command: str) -> Dict[str, Any]:
        """Find top performers/values based on command"""
        
        target_columns = self._identify_target_columns(df, command)
        
        results = {}
        for col in target_columns:
            if df[col].dtype in ['int64', 'float64']:
                # Get top 5 values
                top_values = df.nlargest(5, col)
                results[col] = {
                    "top_performers": top_values.to_dict('records'),
                    "highest_value": float(df[col].max()),
                    "top_5_total": float(top_values[col].sum())
                }
        
        return {
            "operation": "top_performers_analysis",
            "results": results,
            "success": True
        }
    
    async def _smart_update_operation(self, df: pd.DataFrame, command: str, operation_type: str, file_path: Path) -> Dict[str, Any]:
        """THE WOW FACTOR: Update the actual file based on natural language"""
        
        # Extract percentage or amount from command
        percentage = self._extract_percentage(command)
        amount = self._extract_amount(command)
        
        # Create backup
        backup_path = self._create_backup(file_path)
        
        # Identify columns to update
        target_columns = self._identify_target_columns(df, command)
        
        updates_made = {}
        
        for col in target_columns:
            if df[col].dtype in ['int64', 'float64']:
                original_sum = df[col].sum()
                
                if percentage:
                    # Apply percentage increase/decrease
                    if 'increase' in command.lower() or 'raise' in command.lower():
                        df[col] = df[col] * (1 + percentage / 100)
                    else:
                        df[col] = df[col] * (1 - percentage / 100)
                elif amount:
                    # Apply fixed amount increase/decrease
                    if 'increase' in command.lower() or 'add' in command.lower():
                        df[col] = df[col] + amount
                    else:
                        df[col] = df[col] - amount
                
                new_sum = df[col].sum()
                updates_made[col] = {
                    "original_total": float(original_sum),
                    "new_total": float(new_sum),
                    "change": float(new_sum - original_sum),
                    "percentage_change": float(((new_sum - original_sum) / original_sum) * 100)
                }
        
        # Save the updated file
        self._save_updated_file(df, file_path)
        
        return {
            "operation": "intelligent_file_update",
            "file_updated": str(file_path),
            "backup_created": str(backup_path),
            "updates_made": updates_made,
            "rows_affected": len(df),
            "success": True,
            "message": f"Successfully updated {file_path.name} with {len(updates_made)} column modifications"
        }
    
    def _identify_target_columns(self, df: pd.DataFrame, command: str) -> List[str]:
        """Intelligently identify which columns to operate on"""
        
        cmd_lower = command.lower()
        numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
        
        # Specific column keywords
        column_keywords = {
            'salary': ['salary', 'pay', 'compensation', 'wage'],
            'bonus': ['bonus', 'incentive', 'commission'],
            'revenue': ['revenue', 'sales', 'income'],
            'total': ['total', 'gross', 'net'],
            'budget': ['budget', 'cost', 'expense']
        }
        
        target_columns = []
        
        # Look for specific mentions
        for category, keywords in column_keywords.items():
            if any(keyword in cmd_lower for keyword in keywords):
                # Find columns that match this category
                matching_cols = [col for col in numeric_cols 
                               if any(keyword in col.lower() for keyword in keywords)]
                target_columns.extend(matching_cols)
        
        # If no specific columns found, use the most likely numeric columns
        if not target_columns:
            # Prioritize columns with money-related names
            money_cols = [col for col in numeric_cols 
                         if any(word in col.lower() for word in ['salary', 'pay', 'total', 'revenue', 'sales', 'gross'])]
            if money_cols:
                target_columns = money_cols[:3]  # Top 3 money columns
            else:
                target_columns = numeric_cols[:3]  # Top 3 numeric columns
        
        return list(set(target_columns))  # Remove duplicates
    
    def _extract_percentage(self, command: str) -> Optional[float]:
        """Extract percentage from natural language command"""
        
        # Look for percentage patterns
        patterns = [
            r'(\d+(?:\.\d+)?)\s*%',
            r'(\d+(?:\.\d+)?)\s*percent',
            r'by\s+(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*point'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        return None
    
    def _extract_amount(self, command: str) -> Optional[float]:
        """Extract fixed amount from command"""
        
        # Look for dollar amounts
        patterns = [
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*dollars?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                return float(amount_str)
        
        return None
    
    def _create_backup(self, file_path: Path) -> Path:
        """Create backup before modifying file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.parent / f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def _save_updated_file(self, df: pd.DataFrame, file_path: Path):
        """Save updated dataframe back to file"""
        
        ext = file_path.suffix.lower()
        
        if ext == '.csv':
            df.to_csv(file_path, index=False)
        elif ext in ['.xlsx', '.xls']:
            df.to_excel(file_path, index=False)
        else:
            # Fallback to CSV
            df.to_csv(file_path, index=False)
    
    def _generate_summary_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate intelligent summary statistics"""
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        stats = {}
        for col in numeric_cols:
            stats[col] = {
                "mean": float(df[col].mean()),
                "median": float(df[col].median()),
                "std": float(df[col].std()),
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "sum": float(df[col].sum())
            }
        
        return stats
    
    def _generate_insights(self, df: pd.DataFrame, results: Dict) -> List[str]:
        """Generate business insights from analysis"""
        
        insights = []
        
        for col, data in results.items():
            if 'total' in data:
                total = data['total']
                count = data['count']
                avg = data['average']
                
                insights.append(f"Total {col}: {data['formatted_total']}")
                insights.append(f"Average {col} per record: ${avg:,.2f}")
                
                if 'salary' in col.lower():
                    annual_cost = total * 12
                    insights.append(f"Annual payroll cost: ${annual_cost:,.2f}")
                
                if count > 0:
                    insights.append(f"Records analyzed: {count}")
        
        return insights
    
    def _create_backup(self, file_path: Path) -> Path:
        """Create backup of original file before modification"""
        import time
        import shutil
        
        timestamp = int(time.time())
        backup_name = f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
        backup_path = file_path.parent / backup_name
        
        try:
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            logger.warning("Failed to create backup", error=str(e))
            return file_path
    
    def _save_updated_file(self, df: pd.DataFrame, file_path: Path) -> None:
        """Save updated dataframe to file with proper permission handling"""
        import tempfile
        import shutil
        import os
        
        try:
            # Create temporary file first
            with tempfile.NamedTemporaryFile(mode='w', suffix=file_path.suffix, delete=False) as temp_file:
                temp_path = Path(temp_file.name)
            
            # Save to temporary file
            if file_path.suffix.lower() == '.csv':
                df.to_csv(temp_path, index=False)
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                df.to_excel(temp_path, index=False)
            else:
                df.to_csv(temp_path, index=False)  # Default to CSV
            
            # Try to replace original file
            try:
                # Remove read-only attribute if present
                if file_path.exists():
                    os.chmod(file_path, 0o666)
                
                # Replace original with updated file
                shutil.move(str(temp_path), str(file_path))
                
            except PermissionError:
                # If we can't overwrite, create a new file with timestamp
                timestamp = int(time.time())
                new_name = f"{file_path.stem}_updated_{timestamp}{file_path.suffix}"
                new_path = file_path.parent / new_name
                shutil.move(str(temp_path), str(new_path))
                
                logger.info("Created new file due to permissions", 
                           original=str(file_path), 
                           new_file=str(new_path))
                
        except Exception as e:
            # Clean up temp file if it exists
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except:
                    pass
            raise e
    
    def _extract_percentage(self, command: str) -> Optional[float]:
        """Extract percentage value from command"""
        import re
        
        # Look for patterns like "10%", "15 percent", "5.5%"
        patterns = [
            r'(\d+(?:\.\d+)?)\s*%',
            r'(\d+(?:\.\d+)?)\s*percent'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        return None
    
    def _extract_amount(self, command: str) -> Optional[float]:
        """Extract fixed amount from command"""
        import re
        
        # Look for patterns like "$100", "100 dollars", "1000"
        patterns = [
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*dollars?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                return float(amount_str)
        
        return None
    
    # File reading methods
    def _read_csv(self, file_path: Path) -> pd.DataFrame:
        """Read CSV file with intelligent encoding detection"""
        try:
            return pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            return pd.read_csv(file_path, encoding='latin-1')
    
    def _read_excel(self, file_path: Path) -> pd.DataFrame:
        """Read Excel file"""
        return pd.read_excel(file_path)
    
    def _read_ods(self, file_path: Path) -> pd.DataFrame:
        """Read ODS file"""
        return pd.read_excel(file_path, engine='odf')
    
    async def _smart_read_analysis(self, df: pd.DataFrame, command: str) -> Dict[str, Any]:
        """Provide comprehensive file reading analysis with actual employee data"""
        
        # Get employee/record details
        employee_data = []
        name_columns = [col for col in df.columns if any(word in col.lower() for word in ['name', 'employee', 'rep', 'person'])]
        
        # Show all records with formatted data
        for _, row in df.iterrows():
            record = {}
            for col in df.columns:
                if col in name_columns:
                    record[col] = row[col]
                elif df[col].dtype in ['int64', 'float64'] and any(word in col.lower() for word in ['salary', 'pay', 'compensation', 'sales', 'revenue', 'commission']):
                    record[col] = f"${row[col]:,.2f}"
                else:
                    record[col] = row[col]
            employee_data.append(record)
        
        # Calculate totals for numeric columns
        totals = {}
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                total = df[col].sum()
                totals[col] = {
                    "total": f"${total:,.2f}" if any(word in col.lower() for word in ['salary', 'pay', 'compensation', 'sales', 'revenue', 'commission']) else f"{total:,.2f}",
                    "average": f"${df[col].mean():,.2f}" if any(word in col.lower() for word in ['salary', 'pay', 'compensation', 'sales', 'revenue', 'commission']) else f"{df[col].mean():,.2f}",
                    "count": len(df[col].dropna())
                }
        
        return {
            "operation": "smart_file_read_with_data",
            "file_summary": {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "columns": list(df.columns)
            },
            "employee_data": employee_data,
            "totals_summary": totals,
            "insights": [
                f"Found {len(df)} records in the file",
                f"Total columns: {len(df.columns)}",
                *[f"Total {col}: {data['total']}" for col, data in totals.items() if 'salary' in col.lower() or 'pay' in col.lower() or 'compensation' in col.lower()]
            ],
            "success": True
        }
    
    async def _smart_comprehensive_analysis(self, df: pd.DataFrame, command: str) -> Dict[str, Any]:
        """Comprehensive analysis with actual employee data display"""
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        name_columns = [col for col in df.columns if any(word in col.lower() for word in ['name', 'employee', 'rep', 'person'])]
        
        # Detailed analysis with employee data
        analysis = {}
        employee_breakdown = []
        
        for col in numeric_cols:
            analysis[col] = {
                "total": float(df[col].sum()),
                "average": float(df[col].mean()),
                "count": len(df[col].dropna()),
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "formatted_total": f"${df[col].sum():,.2f}" if any(word in col.lower() for word in ['salary', 'pay', 'compensation', 'sales', 'revenue', 'commission']) else f"{df[col].sum():,.2f}"
            }
        
        # Get employee breakdown for key columns
        for _, row in df.iterrows():
            employee_record = {}
            if name_columns:
                employee_record['name'] = row[name_columns[0]]
            
            # Add position/department if available
            for info_col in ['Position', 'Department', 'Region', 'Country']:
                if info_col in df.columns:
                    employee_record[info_col] = row[info_col]
            
            # Add key numeric values
            for col in numeric_cols:
                if any(word in col.lower() for word in ['salary', 'pay', 'compensation', 'sales', 'revenue', 'commission', 'bonus']):
                    employee_record[col] = f"${row[col]:,.2f}"
            
            employee_breakdown.append(employee_record)
        
        # Generate enhanced insights
        enhanced_insights = []
        for col, data in analysis.items():
            if any(word in col.lower() for word in ['salary', 'pay', 'compensation']):
                enhanced_insights.append(f"Total {col}: {data['formatted_total']}")
                enhanced_insights.append(f"Average {col}: ${data['average']:,.2f}")
                if 'salary' in col.lower():
                    annual_cost = data['total'] * 12
                    enhanced_insights.append(f"Annual payroll cost: ${annual_cost:,.2f}")
            elif any(word in col.lower() for word in ['sales', 'revenue']):
                enhanced_insights.append(f"Total {col}: {data['formatted_total']}")
                enhanced_insights.append(f"Average {col}: ${data['average']:,.2f}")
        
        enhanced_insights.append(f"Total employees/records analyzed: {len(df)}")
        
        return {
            "operation": "smart_comprehensive_analysis",
            "analysis": analysis,
            "employee_breakdown": employee_breakdown,
            "insights": enhanced_insights,
            "total_records": len(df),
            "success": True
        }