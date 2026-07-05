#!/usr/bin/env python3
"""
IDT GenAI Financial Statement Analyzer - Enhanced Version
Enhanced with Gemini AI and ChromaDB for better performance and accuracy.
"""

import os
import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import logging
from fpdf import FPDF

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent))

from enhanced_document_processor import EnhancedDocumentProcessor
from compliance_checker import ComplianceChecker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedFinancialAnalyzer:
    def __init__(self):
        """Initialize the enhanced financial analyzer."""
        self.console = Console()
        self.document_processor = None
        self.compliance_checker = None
        self.current_document = None
        
        # Check for Gemini API key
        if not os.getenv('GEMINI_API_KEY'):
            self.console.print("[red]Warning: GEMINI_API_KEY not found in environment variables.[/red]")
            self.console.print("Please create a .env file in the root directory with your Gemini API key.")
            self.console.print("Format: GEMINI_API_KEY=your_api_key_here")
            if not Confirm.ask("Continue without Gemini (will use fallback mode)?"):
                sys.exit(1)
    
    def display_banner(self):
        """Display the application banner."""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    IDT GenAI Financial Statement Analyzer                    ║
║                              Enhanced Version                                ║
║                        Powered by Gemini AI & ChromaDB                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        self.console.print(Panel(banner, style="bold blue"))
    
    def display_menu(self):
        """Display the main menu."""
        menu = """
╭─────────────────────────────────────────── Main Menu ───────────────────────────────────────────╮
│ 1 Load new document                                                                             │
│                                                                                                 │
│ 2 Run compliance check                                                                          │
│                                                                                                 │
│ 3 Query document                                                                                │
│                                                                                                 │
│ 4 Generate report                                                                               │
│                                                                                                 │
│ 5 Force reprocess document                                                                      │
│                                                                                                 │
│ 6 Exit                                                                                          │
╰─────────────────────────────────────────────────────────────────────────────────────────────────╯
        """
        self.console.print(menu)
    
    def load_document(self) -> bool:
        """Load a new document using the enhanced processor."""
        try:
            # Get document path
            doc_path = Prompt.ask(
                "\n[bold cyan]Enter the path to your PDF document[/bold cyan]",
                default="tata steel financial statements.pdf"
            )
            
            # Resolve relative paths
            if not os.path.isabs(doc_path):
                doc_path = os.path.join(os.getcwd(), doc_path)
            
            if not os.path.exists(doc_path):
                self.console.print(f"[red]Error: File not found at {doc_path}[/red]")
                return False
            
            self.console.print(f"\n[bold green]Loading document: {os.path.basename(doc_path)}[/bold green]")
            
            # Initialize enhanced document processor
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Initializing document processor...", total=None)
                
                self.document_processor = EnhancedDocumentProcessor(
                    persist_directory="./financial_docs_chroma"
                )
                
                progress.update(task, description="Processing document...")
                
                # Load or create vector store
                is_cached = self.document_processor.load_or_create_vector_store(doc_path)
                
                if is_cached:
                    progress.update(task, description="Loaded cached vector store")
                else:
                    progress.update(task, description="Created new vector store")
            
            self.current_document = doc_path
            self.compliance_checker = ComplianceChecker()
            
            self.console.print(f"[bold green]✓ Document loaded successfully![/bold green]")
            if is_cached:
                self.console.print("[yellow]Note: Using cached vector store for faster processing[/yellow]")
            
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error loading document: {str(e)}[/red]")
            logger.error(f"Error loading document: {str(e)}")
            return False
    
    def run_compliance_check(self):
        """Run comprehensive compliance checks using the enhanced processor."""
        if not self.document_processor:
            self.console.print("[red]Please load a document first (Option 1)[/red]")
            return
        
        try:
            self.console.print("\n[bold cyan]Running comprehensive BRD IDT compliance check...[/bold cyan]")
            
            # Get compliance rules
            compliance_rules = self.compliance_checker.get_compliance_rules()
            impact_rules = self.compliance_checker.get_impact_rules()
            
            # Create results table
            table = Table(title="BRD IDT Compliance Check Results")
            table.add_column("S.No", style="cyan", no_wrap=True)
            table.add_column("Part", style="cyan", no_wrap=True)
            table.add_column("Sub-part", style="cyan", no_wrap=True)
            table.add_column("Status", style="bold")
            table.add_column("Details", style="white")
            
            compliance_results = []
            rule_count = 0
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Verifying compliance rules...", total=len(compliance_rules))
                
                for rule_key, rule in compliance_rules.items():
                    rule_count += 1
                    progress.update(task, description=f"Checking {rule['name']}...")
                    
                    # Use enhanced processor for compliance verification
                    result = self.document_processor.verify_compliance(rule_key, compliance_rules)
                    
                    # Determine status
                    status = "❓ Unknown"
                    if "compliant" in result['verification_result'].lower():
                        status = "✅ Compliant"
                    elif "non-compliant" in result['verification_result'].lower():
                        status = "❌ Non-Compliant"
                    elif "partially" in result['verification_result'].lower():
                        status = "⚠️ Partially Compliant"
                    elif "no impact" in result['verification_result'].lower():
                        status = "ℹ️ No Impact"
                    
                    # Add to table
                    table.add_row(
                        str(rule_count),
                        rule.get('part', ''),
                        rule.get('sub_part', ''),
                        status,
                        result['verification_result'][:100] + "..." if len(result['verification_result']) > 100 else result['verification_result']
                    )
                    
                    # Store detailed results
                    compliance_results.append({
                        'rule_key': rule_key,
                        'rule': rule,
                        'result': result,
                        'status': status
                    })
                    
                    progress.advance(task)
            
            self.console.print(table)
            
            # Show summary statistics
            self._display_compliance_summary(compliance_results)
            
            # Show detailed results if requested
            if Confirm.ask("\nShow detailed compliance results?"):
                self._display_detailed_compliance_results(compliance_results)
            
            # Store results for report generation
            self.compliance_results = compliance_results
            
        except Exception as e:
            self.console.print(f"[red]Error running compliance check: {str(e)}[/red]")
            logger.error(f"Error running compliance check: {str(e)}")
    
    def _display_compliance_summary(self, compliance_results):
        """Display compliance summary statistics."""
        total_rules = len(compliance_results)
        compliant = sum(1 for r in compliance_results if "✅" in r['status'])
        non_compliant = sum(1 for r in compliance_results if "❌" in r['status'])
        partially_compliant = sum(1 for r in compliance_results if "⚠️" in r['status'])
        no_impact = sum(1 for r in compliance_results if "ℹ️" in r['status'])
        unknown = sum(1 for r in compliance_results if "❓" in r['status'])
        
        summary_table = Table(title="Compliance Summary")
        summary_table.add_column("Category", style="cyan")
        summary_table.add_column("Count", style="bold")
        summary_table.add_column("Percentage", style="green")
        
        summary_table.add_row("Total Rules", str(total_rules), "100%")
        summary_table.add_row("✅ Compliant", str(compliant), f"{(compliant/total_rules*100):.1f}%")
        summary_table.add_row("❌ Non-Compliant", str(non_compliant), f"{(non_compliant/total_rules*100):.1f}%")
        summary_table.add_row("⚠️ Partially Compliant", str(partially_compliant), f"{(partially_compliant/total_rules*100):.1f}%")
        summary_table.add_row("ℹ️ No Impact", str(no_impact), f"{(no_impact/total_rules*100):.1f}%")
        summary_table.add_row("❓ Unknown", str(unknown), f"{(unknown/total_rules*100):.1f}%")
        
        self.console.print(summary_table)
    
    def _display_detailed_compliance_results(self, compliance_results):
        """Display detailed compliance results."""
        for result in compliance_results:
            rule = result['rule']
            verification_result = result['result']['verification_result']
            
            self.console.print(f"\n[bold cyan]{rule['name']}[/bold cyan]")
            self.console.print(f"[yellow]Part: {rule.get('part', '')} | Sub-part: {rule.get('sub_part', '')}[/yellow]")
            self.console.print(f"[white]{rule.get('description', '')}[/white]")
            
            if rule.get('verification_points'):
                self.console.print(f"\n[bold]Verification Points:[/bold]")
                for point in rule['verification_points']:
                    self.console.print(f"• {point}")
            
            self.console.print(f"\n[bold]Result:[/bold] {result['status']}")
            self.console.print(f"[white]{verification_result}[/white]")
            
            if result['result'].get('citations'):
                self.console.print(f"\n[yellow]Citations:[/yellow]")
                for citation in result['result']['citations']:
                    self.console.print(f"• Page {citation.get('page', 'Unknown')}: {citation.get('text', '')}")
            
            self.console.print("-" * 80)

    def query_document(self):
        """Query the document using the enhanced processor."""
        if not self.document_processor:
            self.console.print("[red]Please load a document first (Option 1)[/red]")
            return
        
        try:
            query = Prompt.ask("\n[bold cyan]Enter your question about the document[/bold cyan]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Processing query...", total=None)
                
                # Use enhanced processor for querying
                result = self.document_processor.query_document(query)
                
                progress.update(task, description="Query completed")
            
            # Display results
            self.console.print(f"\n[bold green]Answer:[/bold green]")
            self.console.print(Panel(result['answer'], title="Response", border_style="green"))
            
            if result['citations']:
                self.console.print(f"\n[bold yellow]Citations:[/bold yellow]")
                for citation in result['citations']:
                    self.console.print(f"• Page {citation.get('page', 'Unknown')}: {citation.get('text', '')}")
            
        except Exception as e:
            self.console.print(f"[red]Error querying document: {str(e)}[/red]")
            logger.error(f"Error querying document: {str(e)}")
    
    def _export_report_to_pdf(self, report_content, pdf_path):
        emoji_map = {
            '✅': '[Compliant]',
            '❌': '[Non-Compliant]',
            '⚠️': '[Partial]',
            'ℹ️': '[No Impact]',
            '❓': '[Unknown]',
            '─': '-',  # horizontal line
            '—': '-',  # em dash
            '–': '-',  # en dash
            '“': '"',
            '”': '"',
            '‘': "'",
            '’': "'",
        }
        def replace_emojis(text):
            for emoji, replacement in emoji_map.items():
                text = text.replace(emoji, replacement)
            # Remove any remaining non-latin-1 characters
            return text.encode('latin-1', errors='ignore').decode('latin-1')
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=11)
        for section in report_content:
            section = replace_emojis(section)
            for line in section.splitlines():
                pdf.multi_cell(0, 8, line)
            pdf.ln(2)
        pdf.output(pdf_path)
    
    def generate_report(self):
        """Generate a comprehensive compliance-focused report."""
        if not self.document_processor:
            self.console.print("[red]Please load a document first (Option 1)[/red]")
            return
        
        if not hasattr(self, 'compliance_results') or not self.compliance_results:
            self.console.print("[red]Please run compliance check first (Option 2)[/red]")
            return
        
        try:
            self.console.print("\n[bold cyan]Generating comprehensive compliance report...[/bold cyan]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Generating report...", total=None)
                
                # Generate compliance-focused report
                report_content = self._generate_compliance_report_content()
                
                progress.update(task, description="Report completed")
            
            # Display report
            self.console.print(f"\n[bold green]Generated Compliance Report:[/bold green]")
            for section in report_content:
                self.console.print(Panel(section, border_style="blue"))
            
            # Save report option
            if Confirm.ask("\nSave compliance report to file?"):
                report_path = f"BRD_IDT_Compliance_Report_{Path(self.current_document).stem}.txt"
                with open(report_path, 'w', encoding='utf-8') as f:
                    f.write("BRD IDT Compliance Analysis Report\n")
                    f.write("=" * 50 + "\n\n")
                    f.write("".join(report_content))
                self.console.print(f"[green]Compliance report saved to: {report_path}[/green]")
                # PDF export option
                if Confirm.ask("Save compliance report as PDF as well?"):
                    pdf_path = f"BRD_IDT_Compliance_Report_{Path(self.current_document).stem}.pdf"
                    self._export_report_to_pdf(report_content, pdf_path)
                    self.console.print(f"[green]Compliance report PDF saved to: {pdf_path}[/green]")
        
        except Exception as e:
            self.console.print(f"[red]Error generating report: {str(e)}[/red]")
            logger.error(f"Error generating report: {str(e)}")
    
    def _generate_compliance_report_content(self):
        """Generate the content for the compliance-focused report."""
        report_sections = []
        
        # Executive Summary
        total_rules = len(self.compliance_results)
        compliant = sum(1 for r in self.compliance_results if "✅" in r['status'])
        non_compliant = sum(1 for r in self.compliance_results if "❌" in r['status'])
        partially_compliant = sum(1 for r in self.compliance_results if "⚠️" in r['status'])
        
        executive_summary = f"""
## EXECUTIVE SUMMARY

This report presents the comprehensive compliance analysis of the financial statements against the BRD IDT checklist containing 38 verification points.

Overall Compliance Status:
- Total Rules Analyzed: {total_rules}
- ✅ Compliant: {compliant} ({(compliant/total_rules*100):.1f}%)
- ❌ Non-Compliant: {non_compliant} ({(non_compliant/total_rules*100):.1f}%)
- ⚠️ Partially Compliant: {partially_compliant} ({(partially_compliant/total_rules*100):.1f}%)

Key Findings:
"""
        
        # Add key findings based on non-compliant items
        non_compliant_items = [r for r in self.compliance_results if "❌" in r['status']]
        if non_compliant_items:
            executive_summary += "\nCritical Non-Compliance Issues:\n"
            for item in non_compliant_items[:5]:  # Top 5 issues
                executive_summary += f"- {item['rule']['name']}: {item['result']['verification_result'][:100]}...\n"
        else:
            executive_summary += "\nNo critical non-compliance issues identified.\n"
        
        report_sections.append(executive_summary)
        
        # Detailed Analysis by Part
        rules_by_part = {}
        for result in self.compliance_results:
            part = result['rule'].get('part', 'Unknown')
            if part not in rules_by_part:
                rules_by_part[part] = []
            rules_by_part[part].append(result)
        
        for part, results in rules_by_part.items():
            part_section = f"\n## {part.upper()}\n\n"
            
            for i, result in enumerate(results, 1):
                rule = result['rule']
                verification_result = result['result']['verification_result']
                
                # Add clear separator and numbering for each checklist point
                part_section += f"### CHECKLIST POINT {i}: {rule['name']}\n"
                part_section += f"Sub-part: {rule.get('sub_part', '')}\n"
                part_section += f"Status: {result['status']}\n"
                part_section += f"Description: {rule.get('description', '')}\n\n"
                
                if rule.get('verification_points'):
                    part_section += "Verification Points:\n"
                    for point in rule['verification_points']:
                        part_section += f"- {point}\n"
                    part_section += "\n"
                
                part_section += f"Analysis: {verification_result}\n\n"
                
                # Add clear separator between points
                part_section += "─" * 80 + "\n\n"
            
            report_sections.append(part_section)
        
        # Recommendations
        recommendations = "\n## RECOMMENDATIONS\n\n"
        
        if non_compliant_items:
            recommendations += "Immediate Actions Required:\n"
            for item in non_compliant_items:
                recommendations += f"- Address non-compliance in {item['rule']['name']}: {item['result']['verification_result'][:150]}...\n"
        else:
            recommendations += "No immediate actions required. All compliance requirements appear to be met.\n"
        
        recommendations += "\nGeneral Recommendations:\n"
        recommendations += "- Maintain documentation for all compliance verifications\n"
        recommendations += "- Regular review of GST compliance procedures\n"
        recommendations += "- Stay updated with latest GST regulations and amendments\n"
        recommendations += "- Consider implementing automated compliance monitoring systems\n"
        
        report_sections.append(recommendations)
        
        return report_sections
    
    def force_reprocess_document(self):
        """Force reprocess the current document by clearing cache and reloading."""
        if not self.current_document:
            self.console.print("[red]No document loaded. Please load a document first (Option 1)[/red]")
            return
        
        try:
            self.console.print(f"\n[bold yellow]Force reprocessing document: {os.path.basename(self.current_document)}[/bold yellow]")
            
            # Clear the document-specific vector store
            doc_name = Path(self.current_document).stem
            doc_specific_persist_dir = os.path.join("./financial_docs_chroma", doc_name)
            
            if os.path.exists(doc_specific_persist_dir):
                import shutil
                shutil.rmtree(doc_specific_persist_dir)
                self.console.print(f"[yellow]Cleared cached vector store for {doc_name}[/yellow]")
            
            # Reload the document
            self.load_document()
            
        except Exception as e:
            self.console.print(f"[red]Error force reprocessing document: {str(e)}[/red]")
            logger.error(f"Error force reprocessing document: {str(e)}")

    def run(self):
        """Run the main application loop."""
        self.display_banner()
        
        while True:
            try:
                self.display_menu()
                choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6"])
                
                if choice == "1":
                    self.load_document()
                elif choice == "2":
                    self.run_compliance_check()
                elif choice == "3":
                    self.query_document()
                elif choice == "4":
                    self.generate_report()
                elif choice == "5":
                    self.force_reprocess_document()
                elif choice == "6":
                    self.console.print("[bold green]Thank you for using IDT GenAI Financial Statement Analyzer![/bold green]")
                    break
                
                if choice in ["2", "3", "4", "5"]:
                    Prompt.ask("\nPress Enter to continue")
                    
            except KeyboardInterrupt:
                self.console.print("\n[bold yellow]Application interrupted by user.[/bold yellow]")
                break
            except Exception as e:
                self.console.print(f"[red]Unexpected error: {str(e)}[/red]")
                logger.error(f"Unexpected error: {str(e)}")

def main():
    """Main entry point."""
    analyzer = EnhancedFinancialAnalyzer()
    analyzer.run()

if __name__ == "__main__":
    main() 