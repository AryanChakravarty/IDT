# 📑 IDT GenAI Financial Statement Analyzer

An AI-powered compliance automation tool designed to analyze financial statements (PDFs) and verify compliance against Goods and Services Tax (GST) indirect tax (IDT) regulations. Powered by Google's Gemini AI, LangChain, and ChromaDB vector database.

---

## 🚀 Key Features

- **Automated Compliance Verification:** Intelligently checks documents against critical GST and BRD IDT rules.
- **RAG Architecture (Retrieval-Augmented Generation):** Implements semantic chunking and embedding storage in ChromaDB to query large financial PDFs contextually.
- **State-of-the-Art LLM Integration:** Utilizes Google's `gemini-1.5-flash-8b` for high-speed, cost-effective reasoning.
- **Semantic Search Capability:** Uses `embedding-001` to match compliance rules with relevant sections in financial reports.
- **Interactive CLI Console:** Easy-to-use command-line interface powered by `rich` featuring progress bars, colored panels, and structured tables.
- **Comprehensive Report Generation:** Exports analysis results directly to structured text (`.txt`) and PDF formats.

---

## 🏗️ Architecture & Data Flow

```
                                  +-----------------------+
                                  |   Financial PDF doc   |
                                  +-----------+-----------+
                                              |
                                              v (PyMuPDF / PyPDFLoader)
                                  +-----------+-----------+
                                  | Text Chunking (2000 ch)|
                                  +-----------+-----------+
                                              |
                                              v (Google embedding-001)
                                  +-----------+-----------+
                                  | Chroma Vector Database| <---+
                                  +-----------+-----------+     |
                                                                |
+------------------+         +--------------------+             |
| Compliance Rules | ------> |  Semantic Query    | ------------+
| (YAML/Defaults)  |         |  Similarity Search |
+------------------+         +---------+----------+
                                       |
                                       v (Top 6 Context Chunks)
                                  +----+--------------+
                                  | Gemini AI Engine  |
                                  +---------+---------+
                                            |
                                            v
                                  +---------+---------+
                                  | Audit Report & PDF|
                                  +-------------------+
```

---

## 📁 Directory Structure

```
IDT-master/
├── src/
│   ├── compliance_checker.py         # Rules configuration loader & default rules
│   ├── enhanced_document_processor.py # PDF loader, Chroma vector store, & LLM query logic
│   └── main.py                       # Console application controller & CLI runner
├── explanation.md                    # In-depth project documentation
├── prep.md                           # Interview preparation and domain reference guide
├── .gitignore                        # Git exclusion settings
└── README.md                         # Project documentation (this file)
```

---

## 🛠️ Setup & Installation

### 1. Prerequisites
Make sure you have Python 3.8+ installed on your system.

### 2. Clone and Setup Environment
Navigate to the project root directory and create a virtual environment:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
Install the required packages:

```bash
pip install langchain langchain-community langchain-chroma langchain-google-genai google-generativeai pymupdf rich pyyaml fpdf python-dotenv
```

### 4. Configuration
Create a `.env` file in the root directory and add your Google Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 💻 Usage

To launch the CLI application:

```bash
python src/main.py
```

### Main Menu Options

1. **Load new document:** Prompts for a PDF path, extracts pages, chunks text (size: 2000, overlap: 400), embeds them using Google GenAI, and initializes/loads a persistent ChromaDB database.
2. **Run compliance check:** Automatically runs the loaded document against active GST compliance rules. Displays a live status dashboard (`✅ Compliant`, `❌ Non-Compliant`, `⚠️ Partially Compliant`, `ℹ️ No Impact`).
3. **Query document:** Allows you to ask arbitrary custom questions about the financial statement. The engine performs semantic search, finds relevant context, generates a detailed response, and provides source page citations.
4. **Generate report:** Creates a clean summary report containing the executive summary, detailed analysis per checklist point, and recommendations, and offers to save it as a text file and PDF.
5. **Force reprocess document:** Clears the cached vector database for the active document and processes it fresh.
6. **Exit:** Safely quits the program.

---

## 📜 Compliance Rules
By default, the application checks several high-impact tax disclosure areas:
* **Foreign Currency Transactions:** Verifies disclosures of foreign exchange gains/losses and RCM applicability on imported services.
* **Related Party Transactions:** Evaluates compliance with Rule 28 of CGST rules and deemed supply valuations.
* **Revenue Recognition:** Inspects policy alignment with revenue recognition and GST turnover reconciliations.
* **Capital Work in Progress (CWIP):** Analyzes CWIP disclosures for Input Tax Credit (ITC) eligibility.
* **Fixed Assets and ITC:** Audits ITC reversals and capitalization practices.

*Custom rules can be defined by creating a `config/compliance_rules.yaml` file.*
