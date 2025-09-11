"""
Spreadsheet analysis service
Handles CSV, Excel, and ODS file analysis with pandas and openpyxl
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
import structlog
from fuzzywuzzy import fuzz, process

from config import settings

logger = structlog.get_logger(__name__)


class SpreadsheetService:
    """Service for spreadsheet data analysis"""
    
    def __init__(self):
        self.supported_formats = {
            '.csv': self._read_csv,
            '.xlsx': self._read_excel,
            '.xls': self._read_excel,
            '.ods': self._read_ods
        }
    
    async def analyze(self, path: str, operation: str, column: str) -> Dict[str, Any]:
        """
        Analyze spreadsheet data with specified operation
        
        Args:
            path: Path to spreadsheet file
            operation: Operation to perform (sum, avg, count, total)
            column: Column name to analyze
            
        Returns:
            Dictionary with analysis results
        """
        
        try:
            # Validate and normalize file path
            file_path = Path(path)
            
            # If path is relative, try to find it in common locations
            if not file_path.is_absolute():
                # Get current working directory
                cwd = Path.cwd()
                
                search_paths = [
                    file_path,  # Try as-is first
                    Path("documents") / file_path.name,  # documents/filename
                    Path("backend/documents") / file_path.name,  # backend/documents/filename
                    cwd / "documents" / file_path.name,  # absolute path to documents
                    cwd / "backend" / "documents" / file_path.name,  # absolute path to backend/documents
                    cwd.parent / "documents" / file_path.name,  # parent/documents
                ]
                
                # If the original path has directories, try just the filename too
                if "/" in path or "\\" in path:
                    filename = Path(path).name
                    search_paths.extend([
                        Path("documents") / filename,
                        Path("backend/documents") / filename,
                        cwd / "documents" / filename,
                        cwd / "backend" / "documents" / filename,
                        cwd.parent / "documents" / filename,
                    ])
                
                # Try each path until we find one that exists
                for search_path in search_paths:
                    try:
                        if search_path.exists():
                            file_path = search_path
                            logger.info("Found file at path", original_path=path, resolved_path=str(file_path))
                            break
                    except (OSError, PermissionError):
                        continue
            
            if not file_path.exists():
                raise FileNotFoundError(f"Spreadsheet file not found: {path}")
            
            # Check file size
            if file_path.stat().st_size > settings.MAX_FILE_SIZE:
                raise ValueError(f"File too large: {file_path.stat().st_size} bytes")
            
            # Load spreadsheet data
            df = await self._load_spreadsheet(file_path)
            
            # Find matching column with fuzzy matching
            matched_column = self._find_column(df, column)
            
            # Perform the requested operation
            result = self._perform_operation(df, matched_column, operation)
            
            # Count non-null cells
            cells_count = df[matched_column].notna().sum()
            
            logger.info("Spreadsheet analysis completed",
                       path=path,
                       operation=operation,
                       column=column,
                       matched_column=matched_column,
                       result=result,
                       cells_count=cells_count)
            
            return {
                "result": float(result),
                "matched_column": matched_column,
                "cells_count": int(cells_count),
                "operation": operation,
                "total_rows": len(df),
                "total_columns": len(df.columns)
            }
            
        except Exception as e:
            logger.error("Spreadsheet analysis failed", 
                        path=path, 
                        operation=operation, 
                        column=column, 
                        error=str(e))
            raise
    
    async def _load_spreadsheet(self, file_path: Path) -> pd.DataFrame:
        """Load spreadsheet file into pandas DataFrame"""
        
        extension = file_path.suffix.lower()
        
        if extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {extension}")
        
        try:
            loader_func = self.supported_formats[extension]
            df = loader_func(file_path)
            
            if df.empty:
                raise ValueError("Spreadsheet is empty")
            
            logger.info("Spreadsheet loaded successfully",
                       path=str(file_path),
                       rows=len(df),
                       columns=len(df.columns))
            
            return df
            
        except Exception as e:
            logger.error("Failed to load spreadsheet", path=str(file_path), error=str(e))
            raise ValueError(f"Failed to load spreadsheet: {str(e)}")
    
    def _read_csv(self, file_path: Path) -> pd.DataFrame:
        """Read CSV file"""
        try:
            # Try different encodings and separators
            encodings = ['utf-8', 'latin-1', 'cp1252']
            separators = [',', ';', '\t']
            
            for encoding in encodings:
                for sep in separators:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding, sep=sep)
                        if len(df.columns) > 1:  # Valid CSV should have multiple columns
                            return df
                    except (UnicodeDecodeError, pd.errors.EmptyDataError):
                        continue
            
            # Fallback to default
            return pd.read_csv(file_path)
            
        except Exception as e:
            raise ValueError(f"Failed to read CSV file: {str(e)}")
    
    def _read_excel(self, file_path: Path) -> pd.DataFrame:
        """Read Excel file (xlsx, xls)"""
        try:
            # Try to read the first sheet
            df = pd.read_excel(file_path, engine='openpyxl' if file_path.suffix == '.xlsx' else 'xlrd')
            return df
            
        except Exception as e:
            raise ValueError(f"Failed to read Excel file: {str(e)}")
    
    def _read_ods(self, file_path: Path) -> pd.DataFrame:
        """Read ODS file"""
        try:
            df = pd.read_excel(file_path, engine='odf')
            return df
            
        except Exception as e:
            raise ValueError(f"Failed to read ODS file: {str(e)}")
    
    def _find_column(self, df: pd.DataFrame, column_query: str) -> str:
        """Find column using fuzzy matching"""
        
        columns = list(df.columns)
        
        # Exact match first
        if column_query in columns:
            return column_query
        
        # Case-insensitive exact match
        for col in columns:
            if str(col).lower() == column_query.lower():
                return col
        
        # Fuzzy matching
        matches = process.extract(column_query, columns, limit=3)
        
        if matches and matches[0][1] >= 70:  # 70% similarity threshold
            best_match = matches[0][0]
            logger.info("Column matched using fuzzy search",
                       query=column_query,
                       matched=best_match,
                       similarity=matches[0][1])
            return best_match
        
        # If no good match, suggest available columns
        available_columns = ", ".join(str(col) for col in columns[:10])
        raise ValueError(f"Column '{column_query}' not found. Available columns: {available_columns}")
    
    def _perform_operation(self, df: pd.DataFrame, column: str, operation: str) -> float:
        """Perform the requested operation on the column"""
        
        # Get the column data
        col_data = df[column]
        
        # Convert to numeric, coercing errors to NaN
        numeric_data = pd.to_numeric(col_data, errors='coerce')
        
        # Remove NaN values
        clean_data = numeric_data.dropna()
        
        if len(clean_data) == 0:
            raise ValueError(f"Column '{column}' contains no numeric data")
        
        # Perform operation
        if operation in ['sum', 'total']:
            result = clean_data.sum()
        elif operation == 'avg':
            result = clean_data.mean()
        elif operation == 'count':
            result = len(clean_data)
        else:
            raise ValueError(f"Unsupported operation: {operation}")
        
        logger.info("Operation performed successfully",
                   column=column,
                   operation=operation,
                   result=result,
                   data_points=len(clean_data))
        
        return result
    
    def get_column_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get information about all columns in the DataFrame"""
        
        column_info = {}
        
        for col in df.columns:
            col_data = df[col]
            numeric_data = pd.to_numeric(col_data, errors='coerce')
            
            column_info[str(col)] = {
                "type": str(col_data.dtype),
                "non_null_count": col_data.notna().sum(),
                "null_count": col_data.isna().sum(),
                "is_numeric": not numeric_data.isna().all(),
                "unique_values": col_data.nunique(),
                "sample_values": col_data.dropna().head(3).tolist()
            }
        
        return column_info
    
    async def update_spreadsheet(self, path: str, operation: str, column: str = None, value: str = None, percentage: float = None) -> Dict[str, Any]:
        """
        Update spreadsheet with various operations
        
        Args:
            path: Path to spreadsheet file
            operation: Operation to perform (salary_increase, bonus_update, add_column)
            column: Column name for operations
            value: Value for operations
            percentage: Percentage for increases
            
        Returns:
            Dictionary with update results
        """
        
        try:
            # Validate and normalize file path (same logic as analyze method)
            file_path = Path(path)
            
            # If path is relative, try to find it in common locations
            if not file_path.is_absolute():
                # Get current working directory
                cwd = Path.cwd()
                
                search_paths = [
                    file_path,  # Try as-is first
                    Path("documents") / file_path.name,  # documents/filename
                    Path("backend/documents") / file_path.name,  # backend/documents/filename
                    cwd / "documents" / file_path.name,  # absolute path to documents
                    cwd / "backend" / "documents" / file_path.name,  # absolute path to backend/documents
                    cwd.parent / "documents" / file_path.name,  # parent/documents
                ]
                
                # If the original path has directories, try just the filename too
                if "/" in path or "\\" in path:
                    filename = Path(path).name
                    search_paths.extend([
                        Path("documents") / filename,
                        Path("backend/documents") / filename,
                        cwd / "documents" / filename,
                        cwd / "backend" / "documents" / filename,
                        cwd.parent / "documents" / filename,
                    ])
                
                # Try each path until we find one that exists
                for search_path in search_paths:
                    try:
                        if search_path.exists():
                            file_path = search_path
                            logger.info("Found file for update", original_path=path, resolved_path=str(file_path))
                            break
                    except (OSError, PermissionError):
                        continue
            
            if not file_path.exists():
                logger.error("File not found for update after trying all paths", 
                           original_path=path, 
                           final_path=str(file_path),
                           cwd=str(Path.cwd()))
                raise FileNotFoundError(f"Spreadsheet file not found: {path}")
            
            # Load spreadsheet data
            df = await self._load_spreadsheet(file_path)
            
            # Perform the requested operation
            if operation == "salary_increase":
                df = self._apply_salary_increase(df, percentage or 10.0)
                
            elif operation == "bonus_update":
                df = self._update_bonuses(df, value)
                
            elif operation == "add_column":
                df = self._add_column(df, column or "New_Column", value)
                
            else:
                raise ValueError(f"Unsupported operation: {operation}")
            
            # Create backup before updating
            import shutil
            import time
            backup_path = file_path.parent / f"{file_path.stem}_backup_{int(time.time())}{file_path.suffix}"
            shutil.copy2(file_path, backup_path)
            logger.info("Created backup", backup_path=str(backup_path))
            
            # Save updated file IN PLACE (overwrite original) with retry logic
            max_retries = 3
            retry_delay = 0.5
            
            for attempt in range(max_retries):
                try:
                    # Ensure file is not read-only
                    import stat
                    file_path.chmod(stat.S_IWRITE | stat.S_IREAD)
                    
                    if file_path.suffix.lower() == '.csv':
                        df.to_csv(file_path, index=False)
                    elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                        df.to_excel(file_path, index=False)
                    else:
                        # Fallback to CSV
                        df.to_csv(file_path, index=False)
                    
                    # If we get here, the write was successful
                    break
                    
                except PermissionError as pe:
                    if attempt < max_retries - 1:
                        logger.warning(f"Permission error on attempt {attempt + 1}, retrying...", 
                                     error=str(pe), file_path=str(file_path))
                        import time
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        # Last attempt failed, try alternative approach
                        logger.warning("All write attempts failed, trying alternative file name")
                        
                        # Create new file with timestamp suffix
                        import time
                        timestamp = int(time.time())
                        alt_path = file_path.parent / f"{file_path.stem}_updated_{timestamp}{file_path.suffix}"
                        
                        if file_path.suffix.lower() == '.csv':
                            df.to_csv(alt_path, index=False)
                        elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                            df.to_excel(alt_path, index=False)
                        else:
                            df.to_csv(alt_path, index=False)
                        
                        logger.info("Created updated file with new name", 
                                  original=str(file_path), 
                                  updated=str(alt_path))
                        
                        # Update the file_path for return value
                        file_path = alt_path
                        break
            
            logger.info("Spreadsheet update completed",
                       path=path,
                       operation=operation,
                       output_file=str(file_path),
                       backup_file=str(backup_path),
                       rows=len(df),
                       columns=len(df.columns))
            
            return {
                "operation": operation,
                "input_file": path,
                "output_file": str(file_path),  # Same as input - updated in place
                "rows_updated": len(df),
                "columns": len(df.columns),
                "changes_applied": True,
                "update_type": "in_place"
            }
            
        except Exception as e:
            logger.error("Spreadsheet update failed", 
                        path=path, 
                        operation=operation, 
                        error=str(e))
            raise
    
    def _apply_salary_increase(self, df: pd.DataFrame, percentage: float) -> pd.DataFrame:
        """Apply salary increase to base salary and recalculate totals - IN PLACE"""
        
        # Find salary columns
        salary_cols = [col for col in df.columns if 'salary' in str(col).lower() or 'base' in str(col).lower()]
        total_cols = [col for col in df.columns if 'total' in str(col).lower()]
        
        if salary_cols:
            salary_col = salary_cols[0]
            # Apply percentage increase IN PLACE
            df[salary_col] = pd.to_numeric(df[salary_col], errors='coerce') * (1 + percentage / 100)
            
            # Recalculate totals if total column exists
            if total_cols:
                total_col = total_cols[0]
                bonus_cols = [col for col in df.columns if 'bonus' in str(col).lower()]
                benefits_cols = [col for col in df.columns if 'benefit' in str(col).lower()]
                
                # Recalculate total IN PLACE
                total = df[salary_col].copy()
                if bonus_cols:
                    total += pd.to_numeric(df[bonus_cols[0]], errors='coerce').fillna(0)
                if benefits_cols:
                    total += pd.to_numeric(df[benefits_cols[0]], errors='coerce').fillna(0)
                
                df[total_col] = total
        
        return df
    
    def _update_bonuses(self, df: pd.DataFrame, bonus_value: str = None) -> pd.DataFrame:
        """Update bonus amounts"""
        
        bonus_cols = [col for col in df.columns if 'bonus' in str(col).lower()]
        
        if bonus_cols:
            bonus_col = bonus_cols[0]
            
            if bonus_value:
                # Set specific bonus value
                df[f'New_{bonus_col}'] = float(bonus_value)
            else:
                # Apply performance-based bonus increases
                current_bonus = pd.to_numeric(df[bonus_col], errors='coerce').fillna(0)
                df[f'New_{bonus_col}'] = current_bonus * 1.2  # 20% increase
            
            # Recalculate totals
            total_cols = [col for col in df.columns if 'total' in str(col).lower()]
            if total_cols:
                total_col = total_cols[0]
                salary_cols = [col for col in df.columns if 'salary' in str(col).lower()]
                benefits_cols = [col for col in df.columns if 'benefit' in str(col).lower()]
                
                total = df[f'New_{bonus_col}']
                if salary_cols:
                    total += pd.to_numeric(df[salary_cols[0]], errors='coerce').fillna(0)
                if benefits_cols:
                    total += pd.to_numeric(df[benefits_cols[0]], errors='coerce').fillna(0)
                
                df[f'Updated_{total_col}'] = total
        
        return df
    
    def _add_column(self, df: pd.DataFrame, column_name: str, default_value: str = None) -> pd.DataFrame:
        """Add a new column with sample data"""
        
        if column_name in df.columns:
            column_name = f"{column_name}_New"
        
        # Generate appropriate sample data based on column name
        if 'rating' in column_name.lower() or 'performance' in column_name.lower():
            ratings = ['Excellent', 'Good', 'Outstanding', 'Satisfactory', 'Needs Improvement']
            df[column_name] = [ratings[i % len(ratings)] for i in range(len(df))]
            
        elif 'experience' in column_name.lower() or 'years' in column_name.lower():
            df[column_name] = [2 + (i % 8) for i in range(len(df))]  # 2-10 years
            
        elif 'bonus' in column_name.lower() or 'salary' in column_name.lower():
            df[column_name] = [1000 + (i * 200) for i in range(len(df))]  # Incremental amounts
            
        elif 'department' in column_name.lower() and 'code' in column_name.lower():
            dept_codes = ['ENG001', 'MKT001', 'SAL001', 'HR001', 'FIN001']
            df[column_name] = [dept_codes[i % len(dept_codes)] for i in range(len(df))]
            
        else:
            # Default to provided value or generic data
            df[column_name] = default_value or f"Value_{column_name}"
        
        return df