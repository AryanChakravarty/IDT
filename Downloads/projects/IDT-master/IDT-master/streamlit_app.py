#!/usr/bin/env python3
"""
IDT GenAI Financial Statement Analyzer - Streamlit Web App
Enhanced with Gemini AI and ChromaDB for better performance and accuracy.
"""

import os
import sys
import streamlit as st
from pathlib import Path
from typing import Optional
import logging
import tempfile
import shutil
from fpdf import FPDF

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from enhanced_document_processor import EnhancedDocumentProcessor
from compliance_checker import ComplianceChecker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamlitFinancialAnalyzer:
    def __init__(self):
        """Initialize the Streamlit financial analyzer."""
        self.document_processor = None
        self.compliance_checker = None
        self.current_document = None
        self.compliance_results = None
        
        # Check for Gemini API key
        if not os.getenv('GEMINI_API_KEY'):
            st.error("GEMINI_API_KEY not found in environment variables.")
            st.info("Please create a .env file in the root directory with your Gemini API key.")
            st.info("Format: GEMINI_API_KEY=your_api_key_here")
            st.stop()
    
    def display_header(self):
        """Display the application header."""
        st.title("IDT GenAI Financial Statement Analyzer")
        st.subheader("Enhanced Version - Powered by Gemini AI & ChromaDB")
        st.markdown("---")
    
    def load_document(self):
        """Load a new document using file upload."""
        st.header("📄 Load Document")
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload your financial statement PDF for analysis"
        )
        
        if uploaded_file is not None:
            try:
                # Get the original filename for caching
                original_filename = uploaded_file.name
                doc_name = Path(original_filename).stem
                
                # Check if this document is already cached
                doc_specific_persist_dir = os.path.join("./financial_docs_chroma", doc_name)
                is_cached = os.path.exists(doc_specific_persist_dir)
                
                if is_cached:
                    st.info(f"Found cached vector store for '{original_filename}'. Loading from cache...")
                    # Check if the cache directory has content
                    try:
                        import chromadb
                        client = chromadb.PersistentClient(path=doc_specific_persist_dir)
                        collections = client.list_collections()
                        if collections:
                            st.info(f"Cache contains {len(collections)} collections with data")
                        else:
                            st.warning("Cache directory exists but appears empty")
                    except Exception as e:
                        st.warning(f"Could not verify cache contents: {e}")
                else:
                    st.info(f"Processing new document: {original_filename}")
                    st.info(f"Cache directory will be created at: {doc_specific_persist_dir}")
                
                # Create a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    doc_path = tmp_file.name
                
                # Initialize enhanced document processor (only once)
                if not hasattr(self, 'document_processor') or self.document_processor is None:
                    with st.spinner("Initializing document processor..."):
                        self.document_processor = EnhancedDocumentProcessor(
                            persist_directory="./financial_docs_chroma"
                        )
                
                with st.spinner("Processing document..."):
                    # Load or create vector store using original filename for caching
                    cache_used = self.document_processor.load_or_create_vector_store(doc_path, original_filename)
                
                self.current_document = doc_path
                self.current_document_name = original_filename
                self.compliance_checker = ComplianceChecker()
                
                if cache_used:
                    st.success(f"✓ Document loaded successfully! (Using cached vector store for '{original_filename}')")
                else:
                    st.success(f"✓ Document loaded successfully! (Created new vector store for '{original_filename}')")
                
                # Store document info in session state
                st.session_state.current_document_name = original_filename
                st.session_state.document_loaded = True
                
                return True
                
            except Exception as e:
                st.error(f"Error loading document: {str(e)}")
                logger.error(f"Error loading document: {str(e)}")
                return False
        
        # Show currently loaded document if any
        if hasattr(self, 'current_document_name') and self.current_document_name:
            st.info(f"Currently loaded document: {self.current_document_name}")
        
        return False
    
    def run_compliance_check(self):
        """Run comprehensive compliance checks."""
        if not self.document_processor:
            st.error("Please load a document first (Option 1)")
            return
        
        st.header("🔍 Run Compliance Check")
        
        if st.button("Run BRD IDT Compliance Check"):
            try:
                with st.spinner("Running comprehensive BRD IDT compliance check..."):
                    # Get compliance rules
                    compliance_rules = self.compliance_checker.get_compliance_rules()
                    
                    compliance_results = []
                    rule_count = 0
                    
                    # Create progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for rule_key, rule in compliance_rules.items():
                        rule_count += 1
                        status_text.text(f"Checking {rule['name']}... ({rule_count}/{len(compliance_rules)})")
                        
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
                        
                        # Store detailed results
                        compliance_results.append({
                            'rule_key': rule_key,
                            'rule': rule,
                            'result': result,
                            'status': status
                        })
                        
                        # Update progress
                        progress_bar.progress(rule_count / len(compliance_rules))
                    
                    status_text.text("Compliance check completed!")
                    
                    # Display results table
                    self._display_compliance_results(compliance_results)
                    
                    # Show summary statistics
                    self._display_compliance_summary(compliance_results)
                    
                    # Store results for report generation
                    self.compliance_results = compliance_results
                    
            except Exception as e:
                st.error(f"Error running compliance check: {str(e)}")
                logger.error(f"Error running compliance check: {str(e)}")
    
    def _display_compliance_results(self, compliance_results):
        """Display compliance results in a table."""
        st.subheader("Compliance Check Results")
        
        # Create results data
        results_data = []
        for i, result in enumerate(compliance_results, 1):
            rule = result['rule']
            results_data.append({
                'S.No': i,
                'Part': rule.get('part', ''),
                'Sub-part': rule.get('sub_part', ''),
                'Status': result['status'],
                'Details': result['result']['verification_result'][:100] + "..." if len(result['result']['verification_result']) > 100 else result['result']['verification_result']
            })
        
        st.dataframe(results_data, use_container_width=True)
    
    def _display_compliance_summary(self, compliance_results):
        """Display compliance summary statistics."""
        st.subheader("Compliance Summary")
        
        total_rules = len(compliance_results)
        compliant = sum(1 for r in compliance_results if "✅" in r['status'])
        non_compliant = sum(1 for r in compliance_results if "❌" in r['status'])
        partially_compliant = sum(1 for r in compliance_results if "⚠️" in r['status'])
        no_impact = sum(1 for r in compliance_results if "ℹ️" in r['status'])
        unknown = sum(1 for r in compliance_results if "❓" in r['status'])
        
        # Create summary data
        summary_data = {
            'Category': ['Total Rules', '✅ Compliant', '❌ Non-Compliant', '⚠️ Partially Compliant', 'ℹ️ No Impact', '❓ Unknown'],
            'Count': [total_rules, compliant, non_compliant, partially_compliant, no_impact, unknown],
            'Percentage': ['100%', f'{(compliant/total_rules*100):.1f}%', f'{(non_compliant/total_rules*100):.1f}%', 
                          f'{(partially_compliant/total_rules*100):.1f}%', f'{(no_impact/total_rules*100):.1f}%', 
                          f'{(unknown/total_rules*100):.1f}%']
        }
        
        st.dataframe(summary_data, use_container_width=True)
    
    def query_document(self):
        """Query the document using text input."""
        if not self.document_processor:
            st.error("Please load a document first (Option 1)")
            return
        
        st.header("❓ Query Document")
        
        query = st.text_input("Enter your question about the document:")
        
        if st.button("Submit Query") and query:
            try:
                with st.spinner("Processing query..."):
                    # Use enhanced processor for querying
                    result = self.document_processor.query_document(query)
                
                # Display results
                st.subheader("Answer:")
                st.write(result['answer'])
                
                if result['citations']:
                    st.subheader("Citations:")
                    for citation in result['citations']:
                        st.write(f"• Page {citation.get('page', 'Unknown')}: {citation.get('text', '')}")
                
            except Exception as e:
                st.error(f"Error querying document: {str(e)}")
                logger.error(f"Error querying document: {str(e)}")
    
    def generate_report(self):
        """Generate a comprehensive compliance-focused report."""
        if not self.document_processor:
            st.error("Please load a document first (Option 1)")
            return
        
        if not self.compliance_results:
            st.error("Please run compliance check first (Option 2)")
            return
        
        st.header("📊 Generate Report")
        
        if st.button("Generate Compliance Report"):
            try:
                with st.spinner("Generating comprehensive compliance report..."):
                    # Generate compliance-focused report
                    report_content = self._generate_compliance_report_content()
                st.session_state.report_content = report_content
                st.session_state.report_generated = True
                st.session_state.show_full_report = False
            except Exception as e:
                st.error(f"Error generating report: {str(e)}")
                logger.error(f"Error generating report: {str(e)}")
                return
        
        # Only show download/report preview if report is generated
        if st.session_state.get('report_generated', False):
            report_content = st.session_state.report_content
            # Download buttons at the top
            st.subheader("📥 Download Report:")
            col1, col2 = st.columns(2)
            report_text = "BRD IDT Compliance Analysis Report\n" + "=" * 50 + "\n\n" + "".join(report_content)
            with col1:
                st.download_button(
                    label="📄 Download TXT Report",
                    data=report_text,
                    file_name=f"BRD_IDT_Compliance_Report.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            pdf_path = self._create_pdf_report(report_content)
            with open(pdf_path, "rb") as pdf_file:
                with col2:
                    st.download_button(
                        label="📋 Download PDF Report",
                        data=pdf_file.read(),
                        file_name=f"BRD_IDT_Compliance_Report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            os.remove(pdf_path)
            # Report preview logic
            st.subheader("📋 Report Preview:")
            if not st.session_state.get('show_full_report', False):
                st.info("Showing first page of the report. Click 'Show Complete Report' to view the full report.")
                if report_content:
                    st.text(report_content[0])
                if len(report_content) > 1:
                    if st.button("📖 Show Complete Report"):
                        st.session_state.show_full_report = True
                        st.experimental_rerun()
            else:
                st.info("Showing complete report. Click 'Show Less' to collapse.")
                for i, section in enumerate(report_content):
                    if i == 0:
                        continue
                    st.text(section)
                if st.button("📖 Show Less"):
                    st.session_state.show_full_report = False
                    st.experimental_rerun()
    
    def _create_pdf_report(self, report_content):
        """Create PDF report and return file path."""
        emoji_map = {
            '✅': '[Compliant]',
            '❌': '[Non-Compliant]',
            '⚠️': '[Partial]',
            'ℹ️': '[No Impact]',
            '❓': '[Unknown]',
            '─': '-',
            '—': '-',
            '–': '-',
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
        }
        
        def replace_emojis(text):
            for emoji, replacement in emoji_map.items():
                text = text.replace(emoji, replacement)
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
        
        # Save to temporary file
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf.output(temp_pdf.name)
        return temp_pdf.name
    
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
        """Force reprocess the current document."""
        if not self.current_document:
            st.error("No document loaded. Please load a document first (Option 1)")
            return
        
        st.header("🔄 Force Reprocess Document")
        
        if st.button("Force Reprocess Document"):
            try:
                st.info(f"Force reprocessing document...")
                
                # Clear the document-specific vector store using original filename
                if hasattr(self, 'current_document_name'):
                    doc_name = Path(self.current_document_name).stem
                else:
                    doc_name = Path(self.current_document).stem
                
                doc_specific_persist_dir = os.path.join("./financial_docs_chroma", doc_name)
                
                if os.path.exists(doc_specific_persist_dir):
                    shutil.rmtree(doc_specific_persist_dir)
                    st.success(f"Cleared cached vector store for {doc_name}")
                
                # Reload the document using original filename
                with st.spinner("Reprocessing document..."):
                    if hasattr(self, 'current_document_name'):
                        cache_used = self.document_processor.load_or_create_vector_store(self.current_document, self.current_document_name)
                    else:
                        cache_used = self.document_processor.load_or_create_vector_store(self.current_document)
                
                if cache_used:
                    st.success("Document reprocessed successfully! (Using cached vector store)")
                else:
                    st.success("Document reprocessed successfully! (Created new vector store)")
                
            except Exception as e:
                st.error(f"Error force reprocessing document: {str(e)}")
                logger.error(f"Error force reprocessing document: {str(e)}")

def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="IDT GenAI Financial Statement Analyzer",
        page_icon="📊",
        layout="wide"
    )
    
    # Initialize analyzer
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = StreamlitFinancialAnalyzer()
    
    analyzer = st.session_state.analyzer
    
    # Display header
    analyzer.display_header()
    
    # Show current document status
    if hasattr(analyzer, 'current_document_name') and analyzer.current_document_name:
        st.success(f"📄 Currently loaded: {analyzer.current_document_name}")
        
        # Check cache status
        doc_name = Path(analyzer.current_document_name).stem
        doc_specific_persist_dir = os.path.join("./financial_docs_chroma", doc_name)
        if os.path.exists(doc_specific_persist_dir):
            st.info(f"💾 Cached vector store available for faster processing")
        else:
            st.warning(f"⚠️ No cached vector store found - document will be processed from scratch")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    option = st.sidebar.selectbox(
        "Select an option:",
        [
            "1. Load Document",
            "2. Run Compliance Check", 
            "3. Query Document",
            "4. Generate Report",
            "5. Force Reprocess Document"
        ]
    )
    
    # Handle option selection
    if option == "1. Load Document":
        analyzer.load_document()
    elif option == "2. Run Compliance Check":
        analyzer.run_compliance_check()
    elif option == "3. Query Document":
        analyzer.query_document()
    elif option == "4. Generate Report":
        analyzer.generate_report()
    elif option == "5. Force Reprocess Document":
        analyzer.force_reprocess_document()

if __name__ == "__main__":
    main() 