# IDT GenAI Financial Statement Analyzer - Streamlit Web App

🚀 **A modern web-based application for comprehensive BRD IDT compliance checking of financial statements using Google's Gemini AI and ChromaDB vector database.**

---

## ⚡️ Quick Start for New Users

### 1. **Required Files**
- `streamlit_app.py`  ← **Main Streamlit web application (must be present!)**
- `src/enhanced_document_processor.py`  ← Core document/AI logic
- `src/compliance_checker.py`           ← Compliance rules loader/manager
- `config/compliance_rules.yaml`        ← Compliance rules
- `requirements.txt` or `requirements_streamlit.txt` ← Dependencies
- `.env`                                ← Your Gemini API key (create this)

### 2. **Optional (Convenience) Files**
- `run_streamlit.py`  ← *Helper script to launch the app and check setup (see below)*

### 3. **Not Needed for Streamlit Web App**
- `src/main.py`       ← CLI version (not used by Streamlit)
- `setup.py`          ← Setup helper (not needed for running the app)

---

## 🚀 How to Run the App

### **A. The Standard (Recommended) Way**

```bash
streamlit run streamlit_app.py
```
- This is the official Streamlit command and works everywhere.
- Make sure you have your `.env` file with your Gemini API key in the root directory.

### **B. Using the Helper Script (Optional)**

```bash
python run_streamlit.py
```
- This script checks for `.env` and dependencies, then launches the app.
- It is NOT required, but is helpful for onboarding and setup checks.

---

## 📁 File & Directory Structure

```
EY IDT/
├── streamlit_app.py              # 🎯 Main Streamlit web application (REQUIRED)
├── run_streamlit.py              # 🚀 Optional launcher script (OPTIONAL)
├── requirements_streamlit.txt    # 📦 Streamlit-specific dependencies
├── requirements.txt              # 📦 Full project dependencies
├── .env                          # 🔐 Environment variables (create this)
├── config/
│   └── compliance_rules.yaml     # 📋 BRD IDT compliance rules
├── src/
│   ├── enhanced_document_processor.py  # 🤖 AI-powered document processing
│   ├── compliance_checker.py           # ✅ Compliance rule management
│   └── main.py                         # 💻 CLI version (NOT NEEDED)
├── financial_docs_chroma/        # 🗄️ Vector database cache (auto-created)
├── reports/                      # 📊 Generated reports (auto-created)
└── logs/                         # 📝 Application logs (auto-created)
```

---

## 📝 **Which File Does What?**

| File                          | Required? | Purpose/Notes                                 |
|-------------------------------|-----------|-----------------------------------------------|
| `streamlit_app.py`            | ✅ Yes    | Main Streamlit web app                        |
| `run_streamlit.py`            | ❌ No     | Optional launcher/helper for convenience      |
| `src/enhanced_document_processor.py` | ✅ Yes | Core document/AI logic                  |
| `src/compliance_checker.py`   | ✅ Yes    | Compliance rules loader/manager               |
| `config/compliance_rules.yaml`| ✅ Yes    | Compliance rules                              |
| `requirements.txt`/`requirements_streamlit.txt` | ✅ Yes | Dependencies |
| `.env`                        | ✅ Yes    | Gemini API key (create this)                  |
| `src/main.py`                 | ❌ No     | CLI version, not used by Streamlit            |
| `setup.py`                    | ❌ No     | Setup helper, not needed for Streamlit        |

---

## 🏁 **How to Set Up and Run**

1. **Install dependencies:**
   ```bash
   pip install -r requirements_streamlit.txt
   # or
   pip install -r requirements.txt
   ```
2. **Create your `.env` file:**
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
3. **Run the app:**
   ```bash
   streamlit run streamlit_app.py
   # or (optional)
   python run_streamlit.py
   ```
4. **Open your browser:**
   - Go to [http://localhost:8501](http://localhost:8501)

---

## ❓ **Why are there two files for Streamlit?**

- **`streamlit_app.py`** is the actual web application. You always need this.
- **`run_streamlit.py`** is just a convenience script. It is NOT required. It helps new users by checking for `.env` and dependencies before launching the app. If you want a minimal repo, you can remove it and always use the standard Streamlit command.

---

## 🧹 **Cleaning Up the Repo**
- You can safely remove `src/main.py` and `setup.py` if you only want the Streamlit web app.
- Make sure `streamlit_app.py` is tracked in git and present in the repo.

---

## 📖 Usage Guide (Summary)

1. **Load Document:** Upload your PDF, wait for processing/caching.
2. **Run Compliance Check:** Click the button, view results and summary.
3. **Query Document:** Ask questions, get AI-powered answers with citations.
4. **Generate Report:** Download TXT/PDF compliance reports.

---

## 🛠️ Troubleshooting
- If you see "GEMINI_API_KEY not found", create a `.env` file in the root directory.
- If Streamlit is not installed, run `pip install -r requirements_streamlit.txt`.
- For large PDFs, ensure you have enough RAM and a stable internet connection.

---

## 📬 **Passing the Repo to Others?**
- Make sure `streamlit_app.py` is present and tracked in git.
- Tell users to use `streamlit run streamlit_app.py` to launch the app.
- Optionally, keep `run_streamlit.py` for easier onboarding.
- Remove unused files for clarity.

---

**This README is designed to make onboarding and usage as clear as possible for new users and collaborators.**

## ✨ Features

- **📄 Smart Document Upload**: Drag & drop PDF financial statements with intelligent caching
- **🔍 Comprehensive Compliance Checking**: 38-point BRD IDT checklist verification with AI-powered analysis
- **❓ Natural Language Querying**: Ask questions about uploaded documents with citation tracking
- **📊 Automated Report Generation**: Generate detailed compliance reports in TXT and PDF formats
- **🔄 Intelligent Caching**: Document-specific vector stores for lightning-fast repeated processing
- **📱 Modern Web Interface**: Beautiful, responsive Streamlit interface with real-time progress tracking
- **🎯 BRD IDT Focus**: Specialized for Business Requirements Document - Indirect Tax compliance

## 🚀 Quick Start

### 1. Prerequisites

- **Python 3.8+**
- **Gemini API Key** (free tier available at [Google AI Studio](https://aistudio.google.com/app/apikey))
- **Internet connection** for AI processing
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

### 2. Installation

```bash
# Clone or navigate to the project directory
cd "EY IDT"

# Install dependencies
pip install -r requirements_streamlit.txt
```

### 3. Environment Setup

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

**Get your Gemini API Key:**
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy and paste into your `.env` file

### 4. Launch the Application

**Option 1: Using the runner script (Recommended)**
```bash
python run_streamlit.py
```

**Option 2: Direct Streamlit command**
```bash
streamlit run streamlit_app.py
```

### 5. Access the App

The application will automatically open in your default web browser at:
```
http://localhost:8501
```

## 📖 Usage Guide

### 1. 📄 Load Document
- Click **"1. Load Document"** in the sidebar
- Upload your PDF financial statement (Annual Reports, Financial Statements, etc.)
- Watch the real-time processing progress
- **First time**: Document will be processed and cached
- **Subsequent times**: Uses cached data for instant loading

### 2. 🔍 Run Compliance Check
- Click **"2. Run Compliance Check"** in the sidebar
- Click **"Run BRD IDT Compliance Check"** button
- Monitor progress with the interactive progress bar
- View results in the comprehensive compliance table
- Check compliance summary statistics and trends

### 3. ❓ Query Document
- Click **"3. Query Document"** in the sidebar
- Enter your question in the text box
- Examples:
  - "Summarize all income tax related information"
  - "What are the key financial highlights?"
  - "Explain the revenue recognition policies"
  - "List all related party transactions"
- Click **"Submit Query"** to get AI-powered answers with citations

### 4. 📊 Generate Report
- Click **"4. Generate Report"** in the sidebar
- Click **"Generate Compliance Report"** button
- Preview the comprehensive report
- Download in **TXT** or **PDF** format
- Reports are automatically saved to the `reports/` directory

### 5. 🔄 Force Reprocess
- Click **"5. Force Reprocess Document"** in the sidebar
- Use this to clear cache and reprocess documents
- Useful when documents are updated or cache is corrupted

## 🏗️ Architecture & File Structure

```
EY IDT/
├── streamlit_app.py              # 🎯 Main Streamlit web application
├── run_streamlit.py              # 🚀 Convenient launcher script
├── requirements_streamlit.txt    # 📦 Streamlit-specific dependencies
├── requirements.txt              # 📦 Full project dependencies
├── README_Streamlit.md           # 📖 This documentation
├── .env                          # 🔐 Environment variables (create this)
├── config/
│   └── compliance_rules.yaml     # 📋 BRD IDT compliance rules (572 lines)
├── src/
│   ├── enhanced_document_processor.py  # 🤖 AI-powered document processing
│   ├── compliance_checker.py           # ✅ Compliance rule management
│   └── main.py                         # 💻 Original CLI version
├── financial_docs_chroma/        # 🗄️ Vector database cache (auto-created)
├── reports/                      # 📊 Generated reports (auto-created)
└── logs/                         # 📝 Application logs (auto-created)
```

## 🔧 Technical Details

### AI & Database Stack
- **🤖 Gemini AI**: Google's state-of-the-art language model for document analysis
- **🗄️ ChromaDB**: Vector database for semantic search and document caching
- **📄 PyMuPDF**: High-performance PDF processing
- **🌐 Streamlit**: Modern web framework for interactive applications

### Performance Benefits

| Feature | Traditional Approach | Our AI-Powered System |
|---------|-------------------|----------------------|
| **Query Speed** | Manual search | ⚡ Instant semantic search |
| **Accuracy** | Human-dependent | 🎯 AI-powered analysis |
| **Scalability** | Limited | 📈 Handles large documents |
| **Caching** | None | 💾 Intelligent vector caching |
| **Compliance** | Manual checking | 🤖 Automated rule verification |

### Compliance Rules Coverage

The system checks **38 comprehensive compliance points** including:

- **💰 Foreign Currency Transactions** - GSTR-9C Table 5N compliance
- **🤝 Related Party Transactions** - Rule 28 CGST Rules verification
- **🏗️ Business Expansion** - CWIP ITC eligibility
- **🔄 Merger/Demerger** - ITC-02 and GSTR-9/10 compliance
- **👔 Director Remuneration** - RCM applicability
- **📊 Trial Balance** - Unusual account identification
- **🏛️ Government Grants** - GST implications
- **💳 Sundry Creditors** - Rule 37 ITC reversal
- **💰 Advance Received** - GST applicability on services
- **🏢 Fixed Assets** - ITC reversals and capital goods
- **📦 Inventories** - Abnormal loss ITC reversal
- **⚠️ Contingent Liabilities** - Corporate guarantee implications

## 🐛 Troubleshooting

### Common Issues & Solutions

#### 1. **"GEMINI_API_KEY not found"**
```bash
# Solution: Create .env file
echo "GEMINI_API_KEY=your_actual_api_key_here" > .env
```

#### 2. **"Streamlit not installed"**
```bash
# Solution: Install dependencies
pip install -r requirements_streamlit.txt
```

#### 3. **Document processing fails**
- ✅ Ensure PDF is not corrupted
- ✅ Check file size (recommended < 50MB)
- ✅ Verify PDF contains text (not just images)
- ✅ Try with a different PDF file

#### 4. **Memory issues with large documents**
- ✅ Close other applications
- ✅ Consider splitting large documents
- ✅ Restart the application
- ✅ Use the force reprocess option

#### 5. **Slow performance**
- ✅ First run creates embeddings (slower)
- ✅ Subsequent runs use cached data (faster)
- ✅ Ensure stable internet connection for Gemini API
- ✅ Check your API key usage limits

### Performance Optimization Tips

- **💾 Use cached vector stores** for faster processing
- **🌐 Close unnecessary browser tabs** to free memory
- **⏰ Process documents during off-peak hours**
- **📏 Keep document size reasonable** (< 50MB)
- **🔄 Restart app periodically** for optimal performance

## 📊 Example Queries

Try these example queries with your financial statements:

### Financial Analysis
```
"Summarize all income tax related information"
"What are the key financial highlights?"
"Explain the revenue recognition policies"
"List all related party transactions"
```

### Compliance Checking
```
"What foreign currency risks are disclosed?"
"Check for GST compliance in fixed assets"
"Verify ITC reversals for sundry creditors"
"Analyze government grant implications"
```

### Executive Summary
```
"Provide an executive summary of the financial statements"
"What are the main compliance concerns?"
"Summarize the audit findings"
"List key financial ratios and trends"
```

## 🔐 API Usage & Costs

The application uses Google's Gemini AI API:

- **💰 Free Tier**: 15 requests per minute, 1500 requests per day
- **📊 Monitoring**: Track usage at [Google AI Studio](https://makersuite.google.com/app/apikey)
- **⚡ Performance**: Fast response times with cloud processing
- **🔒 Security**: Enterprise-grade security and privacy

## 🆚 Web vs CLI Version

| Feature | CLI Version | Web Version |
|---------|-------------|-------------|
| **Interface** | Command line | 🌐 Modern web UI |
| **Ease of Use** | Technical | 👥 User-friendly |
| **Visualization** | Text-only | 📊 Interactive charts |
| **Progress Tracking** | Basic | 🎯 Real-time progress |
| **Report Preview** | None | 👀 Live preview |
| **File Management** | Manual | 🖱️ Drag & drop |

## 🚀 Future Enhancements

- **📱 Mobile Optimization** - Responsive design for tablets and phones
- **🔗 Multi-Document Comparison** - Compare multiple financial statements
- **📈 Advanced Analytics** - Financial ratio analysis and trend detection
- **🔔 Real-time Notifications** - Compliance alerts and updates
- **📊 Interactive Dashboards** - Advanced data visualization
- **🔐 Enterprise Features** - Multi-user support and role-based access

## 🤝 Support & Contributing

### Getting Help
1. 📖 Check this troubleshooting section
2. 🔑 Verify your API key is valid
3. 📦 Ensure all dependencies are installed
4. 🐛 Check the logs in the `logs/` directory
5. 💻 Try the original CLI version for comparison

### Contributing
1. 🍴 Fork the repository
2. 🌿 Create a feature branch
3. ✏️ Make your changes
4. 🧪 Test thoroughly
5. 📤 Submit a pull request

## 📄 License

This project is for educational and professional use. Ensure compliance with:
- Google's Gemini API terms of service
- Your organization's data privacy policies
- Applicable financial regulations

---

**🎯 Ready to revolutionize your financial statement analysis with AI-powered insights?** 

Start your compliance journey today with the IDT GenAI Financial Statement Analyzer! 🚀 