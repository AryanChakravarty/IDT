import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
import logging

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedDocumentProcessor:
    def __init__(self, persist_directory: str = "./financial_docs_chroma"):
        """Initialize the enhanced document processor with ChromaDB."""
        self.persist_directory = persist_directory
        self.embeddings = None
        self.vectorstore = None
        self.llm = None
        
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        if self.api_key:
            self._initialize_gemini()
        else:
            logger.warning("GEMINI_API_KEY not found. Will use Ollama fallback.")
    
    def _initialize_gemini(self):
        """Initialize Gemini embeddings and model."""
        try:
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            
            # Initialize embeddings
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=self.api_key,
                task_type="retrieval_document"
            )
            
            # Initialize LLM
            self.llm = ChatGoogleGenerativeAI(
                model="models/gemini-1.5-flash-8b",
                temperature=0.1,
                google_api_key=self.api_key,
                max_output_tokens=4096,
                top_p=0.95,
                top_k=40
            )
            
            logger.info("Gemini initialized successfully!")
            
        except Exception as e:
            logger.error(f"Error initializing Gemini: {e}")
            self.embeddings = None
            self.llm = None
    
    def load_and_chunk_documents(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Load PDF and split into chunks with enhanced processing."""
        try:
            logger.info(f"Loading document: {pdf_path}")
            
            # Load PDF
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            
            logger.info(f"Loaded {len(documents)} pages from PDF")
            
            # Add metadata
            for doc in documents:
                doc.metadata["source"] = Path(pdf_path).name
                doc.metadata["page_number"] = doc.metadata.get("page", "Unknown")
            
            # Log some sample content
            if documents:
                sample_content = documents[0].page_content[:200] + "..." if len(documents[0].page_content) > 200 else documents[0].page_content
                logger.info(f"Sample content from first page: {sample_content}")
            
            # Split into chunks with better parameters for financial documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=2000,      # Larger chunks for financial context
                chunk_overlap=400,    # Good overlap for continuity
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""]  # Better separators for financial text
            )
            
            chunks = text_splitter.split_documents(documents)
            
            logger.info(f"Created {len(chunks)} chunks from {len(documents)} pages")
            
            # Convert to our format
            processed_chunks = []
            for chunk in chunks:
                processed_chunks.append({
                    'text': chunk.page_content,
                    'page': chunk.metadata.get('page_number', 'Unknown'),
                    'source': chunk.metadata.get('source', 'Unknown')
                })
            
            logger.info(f"Processed {len(processed_chunks)} chunks")
            
            # Log sample chunk
            if processed_chunks:
                sample_chunk = processed_chunks[0]['text'][:200] + "..." if len(processed_chunks[0]['text']) > 200 else processed_chunks[0]['text']
                logger.info(f"Sample chunk content: {sample_chunk}")
            
            return processed_chunks
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            raise
    
    def create_vector_store(self, chunks: List[Dict[str, Any]]):
        """Create and persist the vector store."""
        if not self.embeddings:
            logger.warning("No embeddings available. Skipping vector store creation.")
            return
        
        try:
            logger.info("Creating vector store...")
            
            # Convert chunks to LangChain documents
            from langchain.schema import Document
            documents = []
            for chunk in chunks:
                doc = Document(
                    page_content=chunk['text'],
                    metadata={
                        'page': chunk['page'],
                        'source': chunk['source']
                    }
                )
                documents.append(doc)
            
            # Create vector store
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            
            logger.info(f"Vector store created and saved to {self.persist_directory}")
            
        except Exception as e:
            logger.error(f"Error creating vector store: {e}")
            raise
    
    def load_or_create_vector_store(self, pdf_path: str, document_name: str = None):
        """Load existing vector store or create new one."""
        try:
            # Use provided document name or extract from path
            if document_name:
                doc_name = Path(document_name).stem
            else:
                doc_name = Path(pdf_path).stem
            
            doc_specific_persist_dir = os.path.join(self.persist_directory, doc_name)
            
            # Check if document-specific vector store exists
            if os.path.exists(doc_specific_persist_dir) and self.embeddings:
                logger.info(f"Loading existing vector store for {doc_name}...")
                try:
                    self.vectorstore = Chroma(
                        persist_directory=doc_specific_persist_dir,
                        embedding_function=self.embeddings
                    )
                    
                    # Check if vector store has content
                    collection = self.vectorstore._collection
                    if collection.count() > 0:
                        logger.info(f"Vector store loaded successfully with {collection.count()} documents!")
                        return True
                    else:
                        logger.warning("Vector store exists but is empty. Will recreate...")
                        
                except Exception as e:
                    logger.warning(f"Error loading vector store: {e}")
            
            # Create new vector store
            if self.embeddings:
                logger.info(f"Creating new vector store for {doc_name}...")
                chunks = self.load_and_chunk_documents(pdf_path)
                
                if not chunks:
                    logger.error("No chunks created from document")
                    return False
                
                # Create document-specific directory
                os.makedirs(doc_specific_persist_dir, exist_ok=True)
                
                # Update persist directory for this document
                self.persist_directory = doc_specific_persist_dir
                self.create_vector_store(chunks)
                
                logger.info(f"Vector store created successfully with {len(chunks)} chunks")
                return False
            else:
                logger.warning("No embeddings available. Using basic processing.")
                return False
                
        except Exception as e:
            logger.error(f"Error with vector store: {e}")
            raise
    
    def query_document(self, query: str) -> Dict[str, Any]:
        """Query the document using semantic search."""
        if not self.vectorstore or not self.llm:
            logger.warning("Vector store or LLM not available. Using fallback.")
            return self._fallback_query(query)
        
        try:
            logger.info(f"Searching for: {query}")
            
            # Get relevant documents
            docs = self.vectorstore.similarity_search(
                query,
                k=6  # Get more context for financial documents
            )
            
            logger.info(f"Found {len(docs)} relevant documents")
            
            if not docs:
                logger.warning("No documents found in similarity search")
                return {
                    'query': query,
                    'answer': "I couldn't find any relevant information in the document to answer your question.",
                    'citations': []
                }
            
            # Log found documents
            for i, doc in enumerate(docs):
                logger.info(f"Document {i+1}: Page {doc.metadata.get('page', 'Unknown')}, Content preview: {doc.page_content[:100]}...")
            
            # Create context
            context = "\n\n".join([
                f"[Page {doc.metadata.get('page', 'Unknown')}]\n{doc.page_content}"
                for doc in docs
            ])
            
            logger.info(f"Context length: {len(context)} characters")
            
            # Create prompt
            prompt = PromptTemplate(
                template="""You are a financial document analysis expert. Analyze the following financial document 
                and provide a detailed answer to the question. Be thorough in your search and include ALL relevant 
                information.

                Important Instructions:
                1. Search through ALL provided context thoroughly
                2. Include ALL mentions of the topic, even if they seem minor
                3. Provide specific page numbers and citations
                4. If you find multiple mentions, include them all
                5. If you find related information, include that too
                6. Do not assume information is not present - search carefully

                Document Context:
                {context}

                Question: {question}

                Please provide a comprehensive answer that includes:
                1. All relevant information found in the document
                2. Specific citations with page numbers
                3. Any related or contextual information
                4. If you find multiple mentions, list them all

                Answer:""",
                input_variables=["context", "question"]
            )
            
            # Generate response
            chain = prompt | self.llm
            response = chain.invoke({"context": context, "question": query})
            
            logger.info(f"Generated response: {response.content[:200]}...")
            
            # Extract citations
            citations = self._extract_citations(response.content)
            
            return {
                'query': query,
                'answer': response.content,
                'citations': citations
            }
            
        except Exception as e:
            logger.error(f"Error in document query: {e}")
            return self._fallback_query(query)
    
    def _fallback_query(self, query: str) -> Dict[str, Any]:
        """Fallback query method when vector store is not available."""
        return {
            'query': query,
            'answer': "Vector store not available. Please ensure Gemini API key is configured.",
            'citations': []
        }
    
    def _extract_citations(self, text: str) -> List[Dict[str, Any]]:
        """Extract concise citations from the LLM response - just page numbers and key headings."""
        citations = []
        lines = text.split('\n')
        current_citation = None
        
        for line in lines:
            # Look for page references
            if any(marker in line for marker in ['Page', 'page', 'p.', 'p ']):
                if current_citation:
                    citations.append(current_citation)
                try:
                    page_text = line.lower()
                    if 'page' in page_text:
                        page_num = int(''.join(filter(str.isdigit, page_text.split('page')[1])))
                    elif 'p.' in page_text:
                        page_num = int(''.join(filter(str.isdigit, page_text.split('p.')[1])))
                    else:
                        page_num = int(''.join(filter(str.isdigit, page_text)))
                    
                    # Extract only the key heading/topic, not the full text
                    text_part = line.split(']')[1].strip() if ']' in line else line
                    # Take only first 50 characters as a key heading
                    key_heading = text_part[:50].strip()
                    if len(text_part) > 50:
                        key_heading += "..."
                    
                    current_citation = {
                        'page': page_num,
                        'text': key_heading
                    }
                except:
                    continue
            elif current_citation and line.strip():
                # Only add brief context if it's a heading or key term
                line_stripped = line.strip()
                if (len(line_stripped) < 100 and 
                    (line_stripped.isupper() or 
                     line_stripped.endswith(':') or 
                     any(word in line_stripped.lower() for word in ['section', 'note', 'schedule', 'table']))):
                    current_citation['text'] += f" | {line_stripped}"
        
        if current_citation:
            citations.append(current_citation)
        
        # Remove duplicates and limit to 3 most relevant citations
        unique_citations = []
        seen_pages = set()
        for citation in citations:
            if citation['page'] not in seen_pages and len(unique_citations) < 3:
                unique_citations.append(citation)
                seen_pages.add(citation['page'])
        
        return unique_citations
    
    def verify_compliance(self, rule_key: str, compliance_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Verify compliance using semantic search for BRD IDT checklist."""
        if not self.vectorstore or not self.llm:
            logger.warning("Vector store or LLM not available. Using fallback.")
            return self._fallback_compliance(rule_key, compliance_rules)
        
        try:
            if rule_key not in compliance_rules:
                raise ValueError(f"Unknown compliance rule: {rule_key}")
            
            rule = compliance_rules[rule_key]
            
            # Build comprehensive search query
            search_terms = []
            search_terms.extend(rule.get('keywords', []))
            search_terms.append(rule.get('name', ''))
            search_terms.append(rule.get('sub_part', ''))
            
            # Add verification points to search terms
            if rule.get('verification_points'):
                for point in rule['verification_points']:
                    # Extract key terms from verification points
                    key_terms = [term.strip() for term in point.split() if len(term.strip()) > 3]
                    search_terms.extend(key_terms[:5])  # Limit to first 5 terms per point
            
            search_query = " ".join(search_terms)
            logger.info(f"Searching for compliance rule '{rule['name']}' with query: {search_query}")
            
            # Get relevant documents
            docs = self.vectorstore.similarity_search(
                search_query,
                k=6  # Increased for comprehensive compliance checking
            )
            
            if not docs:
                return {
                    'rule_name': rule['name'],
                    'description': rule['description'],
                    'verification_result': "No relevant information found in the document for this compliance requirement.",
                    'citations': []
                }
            
            # Create context
            context = "\n\n".join([
                f"[Page {doc.metadata.get('page', 'Unknown')}]\n{doc.page_content}"
                for doc in docs
            ])
            
            # Create comprehensive compliance verification prompt
            verification_points_text = ""
            if rule.get('verification_points'):
                verification_points_text = "\n".join([f"- {point}" for point in rule['verification_points']])
            
            prompt = PromptTemplate(
                template="""You are a financial compliance expert specializing in GST and BRD IDT requirements. 
                Analyze the following financial document and verify compliance with the specified rule.

                **COMPLIANCE RULE DETAILS:**
                Rule Name: {rule_name}
                Part: {part}
                Sub-part: {sub_part}
                Description: {rule_description}
                
                **VERIFICATION POINTS:**
                {verification_points}

                **VERIFICATION REQUIREMENTS:**
                {verification_prompt}

                **DOCUMENT CONTEXT:**
                {context}

                **ANALYSIS REQUIREMENTS:**
                Please provide a comprehensive compliance analysis with:

                1. **Compliance Status**: 
                   - ✅ COMPLIANT (if all requirements are met)
                   - ❌ NON-COMPLIANT (if requirements are not met)
                   - ⚠️ PARTIALLY COMPLIANT (if some requirements are met)
                   - ℹ️ NO IMPACT (if this item has no GST implications)

                2. **Detailed Findings**: 
                   - Specific evidence from the document
                   - Page numbers and citations
                   - Quantified amounts or percentages where applicable
                   - Identification of any gaps or issues

                3. **Evidence and Citations**: 
                   - Direct quotes from the document
                   - Page numbers for all references
                   - Supporting documentation mentioned

                4. **Risk Assessment**: 
                   - Potential compliance risks
                   - Impact on GST liability
                   - Recommendations for remediation

                5. **Recommendations**: 
                   - Specific actions required
                   - Documentation needed
                   - Follow-up procedures

                **ANALYSIS:**""",
                input_variables=["rule_name", "part", "sub_part", "rule_description", "verification_points", "verification_prompt", "context"]
            )
            
            # Generate response
            chain = prompt | self.llm
            response = chain.invoke({
                "rule_name": rule['name'],
                "part": rule.get('part', ''),
                "sub_part": rule.get('sub_part', ''),
                "rule_description": rule['description'],
                "verification_points": verification_points_text,
                "verification_prompt": rule['verification_prompt'],
                "context": context
            })
            
            # Extract citations
            citations = self._extract_citations(response.content)
            
            return {
                'rule_name': rule['name'],
                'description': rule['description'],
                'verification_result': response.content,
                'citations': citations
            }
            
        except Exception as e:
            logger.error(f"Error in compliance verification for rule {rule_key}: {e}")
            return {
                'rule_name': rule.get('name', 'Unknown'),
                'description': rule.get('description', ''),
                'verification_result': f"Error during compliance verification: {str(e)}",
                'citations': []
            }
    
    def _fallback_compliance(self, rule_key: str, compliance_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback compliance method."""
        rule = compliance_rules.get(rule_key, {})
        return {
            'rule_name': rule.get('name', rule_key),
            'description': rule.get('description', ''),
            'verification_result': "Vector store not available. Please ensure Gemini API key is configured.",
            'citations': []
        } 