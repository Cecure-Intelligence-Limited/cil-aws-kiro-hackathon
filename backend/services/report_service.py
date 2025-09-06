"""
Report Generation Automation Service
Handles automated report compilation from multiple data sources
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
import structlog
import json
from datetime import datetime, timedelta
import io
import base64

# Optional imports for enhanced features
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    from jinja2 import Template
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False

logger = structlog.get_logger(__name__)


class ReportService:
    """Service for automated report generation"""
    
    def __init__(self):
        self.report_templates = {}
        self.data_sources = {}
        self.generated_reports = []
        
    async def generate_report(self, report_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate report from multiple data sources
        
        Args:
            report_config: Report configuration with type, sources, template
            
        Returns:
            Generated report details
        """
        
        try:
            report_type = report_config.get("type", "custom")
            data_sources = report_config.get("data_sources", [])
            template_name = report_config.get("template", "default")
            period = report_config.get("period", "monthly")
            
            # Collect data from sources
            collected_data = await self._collect_data_from_sources(data_sources, period)
            
            # Process and analyze data
            processed_data = await self._process_report_data(collected_data, report_type)
            
            # Generate visualizations
            charts = await self._generate_charts(processed_data, report_type)
            
            # Generate report content
            report_content = await self._generate_report_content(
                processed_data, charts, template_name, report_type
            )
            
            # Save report
            report_id = await self._save_report(report_content, report_config)
            
            logger.info("Report generated successfully",
                       report_id=report_id,
                       report_type=report_type,
                       data_sources_count=len(data_sources))
            
            return {
                "success": True,
                "report_id": report_id,
                "report_type": report_type,
                "generated_at": datetime.now().isoformat(),
                "data_sources": len(data_sources),
                "charts_generated": len(charts),
                "report_content": report_content
            }
            
        except Exception as e:
            logger.error("Report generation failed", error=str(e))
            raise
    
    async def _collect_data_from_sources(self, data_sources: List[str], period: str) -> Dict[str, Any]:
        """Collect data from specified sources"""
        
        collected_data = {}
        
        for source in data_sources:
            try:
                if source.endswith('.csv') or source.endswith('.xlsx'):
                    # Spreadsheet data source
                    data = await self._load_spreadsheet_data(source)
                    collected_data[source] = data
                    
                elif source == "crm":
                    # Simulated CRM data
                    data = await self._get_crm_data(period)
                    collected_data["crm"] = data
                    
                elif source == "sales":
                    # Simulated sales data
                    data = await self._get_sales_data(period)
                    collected_data["sales"] = data
                    
                elif source == "financial":
                    # Simulated financial data
                    data = await self._get_financial_data(period)
                    collected_data["financial"] = data
                    
                else:
                    logger.warning("Unknown data source", source=source)
                    
            except Exception as e:
                logger.error("Failed to collect data from source", source=source, error=str(e))
                continue
        
        return collected_data
    
    async def _load_spreadsheet_data(self, file_path: str) -> pd.DataFrame:
        """Load data from spreadsheet file"""
        
        path = Path(file_path)
        
        # Try to find file in common locations
        if not path.is_absolute():
            search_paths = [
                Path("documents") / path.name,
                Path("backend/documents") / path.name,
                Path.cwd() / "documents" / path.name,
                Path.cwd() / "backend" / "documents" / path.name,
            ]
            
            for search_path in search_paths:
                if search_path.exists():
                    path = search_path
                    break
        
        if not path.exists():
            raise FileNotFoundError(f"Data source file not found: {file_path}")
        
        # Load based on file extension
        if path.suffix.lower() == '.csv':
            return pd.read_csv(path)
        elif path.suffix.lower() in ['.xlsx', '.xls']:
            return pd.read_excel(path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
    
    async def _get_crm_data(self, period: str) -> pd.DataFrame:
        """Get simulated CRM data"""
        
        # Generate sample CRM data
        data = {
            "customer_id": range(1, 101),
            "customer_name": [f"Customer {i}" for i in range(1, 101)],
            "industry": ["Tech", "Finance", "Healthcare", "Retail", "Manufacturing"] * 20,
            "deal_value": [1000 + (i * 500) for i in range(100)],
            "stage": ["Prospect", "Qualified", "Proposal", "Negotiation", "Closed"] * 20,
            "created_date": [datetime.now() - timedelta(days=i) for i in range(100)]
        }
        
        return pd.DataFrame(data)
    
    async def _get_sales_data(self, period: str) -> pd.DataFrame:
        """Get simulated sales data"""
        
        # Generate sample sales data
        data = {
            "sale_id": range(1, 201),
            "product": ["Product A", "Product B", "Product C", "Product D"] * 50,
            "quantity": [1 + (i % 10) for i in range(200)],
            "unit_price": [100, 150, 200, 250] * 50,
            "total_amount": [100 * (1 + (i % 10)) for i in range(200)],
            "sale_date": [datetime.now() - timedelta(days=i//4) for i in range(200)],
            "salesperson": ["Alice", "Bob", "Charlie", "Diana"] * 50
        }
        
        df = pd.DataFrame(data)
        df["total_amount"] = df["quantity"] * df["unit_price"]
        
        return df
    
    async def _get_financial_data(self, period: str) -> pd.DataFrame:
        """Get simulated financial data"""
        
        # Generate sample financial data
        data = {
            "account": ["Revenue", "Expenses", "Marketing", "Operations", "R&D"] * 12,
            "amount": [50000, -20000, -5000, -10000, -8000] * 12,
            "month": [f"2024-{i:02d}" for i in range(1, 13)] * 5,
            "category": ["Income", "Expense", "Expense", "Expense", "Expense"] * 12
        }
        
        return pd.DataFrame(data)
    
    async def _process_report_data(self, collected_data: Dict[str, Any], report_type: str) -> Dict[str, Any]:
        """Process and analyze collected data"""
        
        processed_data = {}
        
        if report_type == "sales":
            processed_data = await self._process_sales_report_data(collected_data)
        elif report_type == "financial":
            processed_data = await self._process_financial_report_data(collected_data)
        elif report_type == "performance":
            processed_data = await self._process_performance_report_data(collected_data)
        else:
            # Custom report processing
            processed_data = await self._process_custom_report_data(collected_data)
        
        return processed_data
    
    async def _process_sales_report_data(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data for sales report"""
        
        processed = {}
        
        # Process sales data if available
        if "sales" in collected_data:
            sales_df = collected_data["sales"]
            
            processed["total_sales"] = sales_df["total_amount"].sum()
            processed["total_transactions"] = len(sales_df)
            processed["average_sale"] = sales_df["total_amount"].mean()
            processed["top_products"] = sales_df.groupby("product")["total_amount"].sum().sort_values(ascending=False).head(5).to_dict()
            processed["sales_by_person"] = sales_df.groupby("salesperson")["total_amount"].sum().to_dict()
            processed["monthly_trend"] = sales_df.groupby(sales_df["sale_date"].dt.strftime("%Y-%m"))["total_amount"].sum().to_dict()
        
        # Process CRM data if available
        if "crm" in collected_data:
            crm_df = collected_data["crm"]
            
            processed["total_deals"] = len(crm_df)
            processed["pipeline_value"] = crm_df["deal_value"].sum()
            processed["deals_by_stage"] = crm_df.groupby("stage")["deal_value"].sum().to_dict()
            processed["deals_by_industry"] = crm_df.groupby("industry")["deal_value"].sum().to_dict()
        
        return processed
    
    async def _process_financial_report_data(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data for financial report"""
        
        processed = {}
        
        if "financial" in collected_data:
            financial_df = collected_data["financial"]
            
            processed["total_revenue"] = financial_df[financial_df["category"] == "Income"]["amount"].sum()
            processed["total_expenses"] = abs(financial_df[financial_df["category"] == "Expense"]["amount"].sum())
            processed["net_profit"] = processed["total_revenue"] - processed["total_expenses"]
            processed["profit_margin"] = (processed["net_profit"] / processed["total_revenue"]) * 100 if processed["total_revenue"] > 0 else 0
            processed["expenses_by_account"] = financial_df[financial_df["category"] == "Expense"].groupby("account")["amount"].sum().abs().to_dict()
            processed["monthly_revenue"] = financial_df[financial_df["category"] == "Income"].groupby("month")["amount"].sum().to_dict()
        
        return processed
    
    async def _process_performance_report_data(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data for performance report"""
        
        processed = {}
        
        # Combine sales and CRM data for performance metrics
        if "sales" in collected_data and "crm" in collected_data:
            sales_df = collected_data["sales"]
            crm_df = collected_data["crm"]
            
            processed["conversion_rate"] = (len(crm_df[crm_df["stage"] == "Closed"]) / len(crm_df)) * 100
            processed["average_deal_size"] = crm_df["deal_value"].mean()
            processed["sales_velocity"] = len(sales_df) / 30  # Sales per day
            processed["top_performers"] = sales_df.groupby("salesperson")["total_amount"].sum().sort_values(ascending=False).head(3).to_dict()
        
        return processed
    
    async def _process_custom_report_data(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data for custom report"""
        
        processed = {}
        
        for source_name, data in collected_data.items():
            if isinstance(data, pd.DataFrame):
                processed[f"{source_name}_summary"] = {
                    "total_rows": len(data),
                    "columns": list(data.columns),
                    "numeric_columns": list(data.select_dtypes(include=['number']).columns)
                }
                
                # Basic statistics for numeric columns
                numeric_data = data.select_dtypes(include=['number'])
                if not numeric_data.empty:
                    processed[f"{source_name}_stats"] = numeric_data.describe().to_dict()
        
        return processed
    
    async def _generate_charts(self, processed_data: Dict[str, Any], report_type: str) -> List[Dict[str, str]]:
        """Generate charts for the report"""
        
        charts = []
        
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            plt.style.use('seaborn-v0_8')
            
            if report_type == "sales" and "top_products" in processed_data:
                # Top products chart
                fig, ax = plt.subplots(figsize=(10, 6))
                products = list(processed_data["top_products"].keys())
                values = list(processed_data["top_products"].values())
                
                ax.bar(products, values)
                ax.set_title("Top Products by Sales")
                ax.set_ylabel("Sales Amount ($)")
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                # Convert to base64
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                chart_data = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
                
                charts.append({
                    "title": "Top Products by Sales",
                    "type": "bar",
                    "data": chart_data
                })
            
            if report_type == "financial" and "expenses_by_account" in processed_data:
                # Expenses pie chart
                fig, ax = plt.subplots(figsize=(8, 8))
                accounts = list(processed_data["expenses_by_account"].keys())
                amounts = list(processed_data["expenses_by_account"].values())
                
                ax.pie(amounts, labels=accounts, autopct='%1.1f%%')
                ax.set_title("Expenses by Account")
                
                # Convert to base64
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                chart_data = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
                
                charts.append({
                    "title": "Expenses by Account",
                    "type": "pie",
                    "data": chart_data
                })
                
        except ImportError:
            logger.warning("Matplotlib not available, generating text-based charts")
            # Generate simple text-based charts as fallback
            if report_type == "sales" and "top_products" in processed_data:
                chart_text = "Top Products by Sales:\n"
                for product, value in processed_data["top_products"].items():
                    chart_text += f"  {product}: ${value:,.2f}\n"
                
                charts.append({
                    "title": "Top Products by Sales",
                    "type": "text",
                    "data": chart_text
                })
            
            if report_type == "financial" and "expenses_by_account" in processed_data:
                chart_text = "Expenses by Account:\n"
                total = sum(processed_data["expenses_by_account"].values())
                for account, amount in processed_data["expenses_by_account"].items():
                    percentage = (amount / total) * 100 if total > 0 else 0
                    chart_text += f"  {account}: ${amount:,.2f} ({percentage:.1f}%)\n"
                
                charts.append({
                    "title": "Expenses by Account",
                    "type": "text",
                    "data": chart_text
                })
                
        except Exception as e:
            logger.error("Chart generation failed", error=str(e))
        
        return charts
    
    async def _generate_report_content(self, processed_data: Dict[str, Any], 
                                     charts: List[Dict[str, str]], 
                                     template_name: str, 
                                     report_type: str) -> Dict[str, Any]:
        """Generate final report content"""
        
        # Create report summary
        summary = self._create_report_summary(processed_data, report_type)
        
        # Generate HTML content
        html_content = self._generate_html_report(processed_data, charts, summary, report_type)
        
        return {
            "summary": summary,
            "processed_data": processed_data,
            "charts": charts,
            "html_content": html_content,
            "report_type": report_type,
            "generated_at": datetime.now().isoformat()
        }
    
    def _create_report_summary(self, processed_data: Dict[str, Any], report_type: str) -> str:
        """Create executive summary for the report"""
        
        if report_type == "sales":
            total_sales = processed_data.get("total_sales", 0)
            total_transactions = processed_data.get("total_transactions", 0)
            average_sale = processed_data.get("average_sale", 0)
            
            return f"""
            Sales Report Summary:
            • Total Sales: ${total_sales:,.2f}
            • Total Transactions: {total_transactions:,}
            • Average Sale: ${average_sale:.2f}
            • Performance shows {'strong' if total_sales > 100000 else 'moderate'} sales activity
            """
            
        elif report_type == "financial":
            total_revenue = processed_data.get("total_revenue", 0)
            total_expenses = processed_data.get("total_expenses", 0)
            net_profit = processed_data.get("net_profit", 0)
            profit_margin = processed_data.get("profit_margin", 0)
            
            return f"""
            Financial Report Summary:
            • Total Revenue: ${total_revenue:,.2f}
            • Total Expenses: ${total_expenses:,.2f}
            • Net Profit: ${net_profit:,.2f}
            • Profit Margin: {profit_margin:.1f}%
            • Financial health appears {'strong' if profit_margin > 10 else 'moderate'}
            """
            
        else:
            return "Custom report generated with available data sources."
    
    def _generate_html_report(self, processed_data: Dict[str, Any], 
                            charts: List[Dict[str, str]], 
                            summary: str, 
                            report_type: str) -> str:
        """Generate HTML report content using Python string formatting"""
        
        # Generate charts HTML
        charts_html = ""
        for chart in charts:
            charts_html += f"""
            <div class="chart">
                <h3>{chart['title']}</h3>
                <img src="data:image/png;base64,{chart['data']}" alt="{chart['title']}">
            </div>
            """
        
        # Generate data sections HTML
        data_html = ""
        for key, value in processed_data.items():
            formatted_key = key.replace('_', ' ').title()
            data_html += f"""
                <h3>{formatted_key}</h3>
                <p>{str(value)}</p>
            """
        
        # Complete HTML template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{report_type.title()} Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .summary {{ background: #f5f5f5; padding: 20px; margin: 20px 0; }}
                .chart {{ margin: 20px 0; text-align: center; }}
                .data-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .data-table th, .data-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .data-table th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{report_type.title()} Report</h1>
                <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            
            <div class="summary">
                <h2>Executive Summary</h2>
                <pre>{summary}</pre>
            </div>
            
            {charts_html}
            
            <div class="data-section">
                <h2>Detailed Data</h2>
                {data_html}
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    async def _save_report(self, report_content: Dict[str, Any], report_config: Dict[str, Any]) -> str:
        """Save generated report"""
        
        try:
            report_id = f"report_{int(datetime.now().timestamp())}"
            
            # Save report data
            report_data = {
                "id": report_id,
                "config": report_config,
                "content": report_content,
                "generated_at": datetime.now().isoformat()
            }
            
            self.generated_reports.append(report_data)
            
            # Save to file
            reports_file = Path("backend/data/generated_reports.json")
            reports_file.parent.mkdir(exist_ok=True)
            
            with open(reports_file, 'w') as f:
                json.dump(self.generated_reports, f, indent=2, default=str)
            
            # Save HTML report
            html_file = Path(f"backend/data/reports/{report_id}.html")
            html_file.parent.mkdir(exist_ok=True)
            
            with open(html_file, 'w') as f:
                f.write(report_content["html_content"])
            
            return report_id
            
        except Exception as e:
            logger.error("Failed to save report", error=str(e))
            raise
    
    async def schedule_report(self, report_config: Dict[str, Any], schedule: str) -> Dict[str, Any]:
        """
        Schedule automatic report generation
        
        Args:
            report_config: Report configuration
            schedule: Schedule frequency (daily, weekly, monthly)
            
        Returns:
            Scheduling result
        """
        
        try:
            scheduled_report = {
                "id": f"scheduled_{int(datetime.now().timestamp())}",
                "config": report_config,
                "schedule": schedule,
                "next_run": self._calculate_next_run(schedule),
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
            
            # Save scheduled report (in real implementation, this would integrate with a job scheduler)
            logger.info("Report scheduled",
                       schedule_id=scheduled_report["id"],
                       schedule=schedule,
                       next_run=scheduled_report["next_run"])
            
            return {
                "success": True,
                "schedule_id": scheduled_report["id"],
                "schedule": schedule,
                "next_run": scheduled_report["next_run"],
                "message": "Report scheduled successfully"
            }
            
        except Exception as e:
            logger.error("Failed to schedule report", error=str(e))
            raise
    
    def _calculate_next_run(self, schedule: str) -> str:
        """Calculate next run time for scheduled report"""
        
        now = datetime.now()
        
        if schedule == "daily":
            next_run = now + timedelta(days=1)
        elif schedule == "weekly":
            next_run = now + timedelta(weeks=1)
        elif schedule == "monthly":
            next_run = now + timedelta(days=30)
        else:
            next_run = now + timedelta(days=1)  # Default to daily
        
        return next_run.isoformat()