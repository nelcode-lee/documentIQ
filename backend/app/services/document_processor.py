"""Document processor for parsing and chunking documents."""

import os
import tempfile
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import tiktoken

# PDF processing
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    try:
        import PyPDF2
        HAS_PYPDF2 = True
    except ImportError:
        HAS_PYPDF2 = False

# DOCX processing
try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

# LangChain for intelligent chunking
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False


class DocumentChunk:
    """Represents a chunk of a document."""
    
    def __init__(
        self,
        content: str,
        chunk_index: int,
        metadata: Optional[Dict] = None,
        page_number: Optional[int] = None,
        section_header: Optional[str] = None
    ):
        self.content = content
        self.chunk_index = chunk_index
        self.metadata = metadata or {}
        self.page_number = page_number
        self.section_header = section_header
        
        # Add section header to content if available
        if section_header:
            self.full_content = f"{section_header}\n\n{content}"
        else:
            self.full_content = content
    
    def to_dict(self) -> Dict:
        """Convert chunk to dictionary."""
        return {
            "content": self.content,
            "full_content": self.full_content,
            "chunk_index": self.chunk_index,
            "metadata": self.metadata,
            "page_number": self.page_number,
            "section_header": self.section_header
        }


class DocumentProcessor:
    """Process and chunk documents for RAG."""
    
    def __init__(
        self,
        chunk_size: int = 500,  # ~500 tokens (~375-625 words) - optimized for precise retrieval
        chunk_overlap: int = 125,  # ~125 tokens overlap (25% overlap for context)
        min_chunk_size: int = 100  # Minimum chunk size in tokens
    ):
        """
        Initialize document processor.
        
        Args:
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap between chunks in tokens
            min_chunk_size: Minimum chunk size in tokens
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        
        # Initialize tokenizer for accurate token counting
        try:
            # Use cl100k_base (GPT-3.5/4 tokenizer)
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except:
            self.tokenizer = None
        
        # Initialize LangChain text splitter for intelligent chunking
        if HAS_LANGCHAIN:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size * 4,  # Approximate: 1 token ≈ 4 chars
                chunk_overlap=chunk_overlap * 4,
                length_function=len,
                separators=[
                    "\n\n\n",  # Triple newlines (major sections)
                    "\n\n",    # Double newlines (paragraphs)
                    "\n",      # Single newlines
                    ". ",      # Sentences
                    " ",       # Words
                    ""         # Characters
                ]
            )
        else:
            self.text_splitter = None
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        # Fallback: approximate 1 token = 4 characters
        return len(text) // 4
    
    async def process_document(
        self,
        file_path: str,
        file_extension: str,
        title: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Tuple[str, List[DocumentChunk], Dict]:
        """
        Process a document file.
        
        Args:
            file_path: Path to the document file
            file_extension: File extension (.pdf, .docx, .txt)
            title: Document title
            category: Document category
            tags: Document tags
            
        Returns:
            Tuple of (extracted_text, chunks, metadata)
        """
        # Extract text based on file type
        if file_extension == '.pdf':
            text, metadata = await self._extract_pdf(file_path)
        elif file_extension == '.docx':
            text, metadata = await self._extract_docx(file_path)
        elif file_extension == '.txt':
            text, metadata = await self._extract_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        # Add provided metadata
        metadata['title'] = title or metadata.get('title', os.path.basename(file_path))
        metadata['category'] = category
        metadata['tags'] = tags or []
        metadata['processed_at'] = datetime.utcnow().isoformat()
        
        # Chunk the document
        chunks = await self._chunk_text(text, metadata)
        
        return text, chunks, metadata
    
    async def _extract_pdf(self, file_path: str) -> Tuple[str, Dict]:
        """Extract text from PDF file."""
        metadata = {'type': 'pdf', 'pages': 0}
        
        if HAS_PYMUPDF:
            # Use PyMuPDF (fitz) - better quality
            doc = fitz.open(file_path)
            pages = []
            metadata['pages'] = len(doc)
            
            for page_num, page in enumerate(doc, start=1):
                page_text = page.get_text()
                if page_text.strip():
                    pages.append(f"--- Page {page_num} ---\n{page_text}")
            
            # Extract metadata if available
            if doc.metadata:
                if doc.metadata.get('title'):
                    metadata['title'] = doc.metadata['title']
                if doc.metadata.get('author'):
                    metadata['author'] = doc.metadata['author']
            
            doc.close()
            return '\n\n'.join(pages), metadata
            
        elif HAS_PYPDF2:
            # Fallback to PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                pages = []
                metadata['pages'] = len(pdf_reader.pages)
                
                for page_num, page in enumerate(pdf_reader.pages, start=1):
                    page_text = page.extract_text()
                    if page_text.strip():
                        pages.append(f"--- Page {page_num} ---\n{page_text}")
                
                # Extract metadata
                if pdf_reader.metadata:
                    if pdf_reader.metadata.get('/Title'):
                        metadata['title'] = pdf_reader.metadata['/Title']
                    if pdf_reader.metadata.get('/Author'):
                        metadata['author'] = pdf_reader.metadata['/Author']
                
                return '\n\n'.join(pages), metadata
        else:
            raise ImportError("No PDF library available. Install PyMuPDF or PyPDF2")
    
    async def _extract_docx(self, file_path: str) -> Tuple[str, Dict]:
        """Extract text from DOCX file."""
        if not HAS_DOCX:
            raise ImportError("python-docx not installed")
        
        doc = Document(file_path)
        paragraphs = []
        current_section = None
        metadata = {'type': 'docx', 'sections': []}
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            
            # Detect headings (Word headings have style)
            if para.style and 'Heading' in para.style.name:
                level = int(para.style.name.split()[-1]) if para.style.name.split()[-1].isdigit() else 1
                if level <= 2:  # Track major headings
                    current_section = text
                    metadata['sections'].append(text)
                paragraphs.append(f"\n{'#' * level} {text}\n")
            else:
                paragraphs.append(text)
        
        # Extract metadata
        if doc.core_properties.title:
            metadata['title'] = doc.core_properties.title
        if doc.core_properties.author:
            metadata['author'] = doc.core_properties.author
        
        return '\n\n'.join(paragraphs), metadata
    
    async def _extract_txt(self, file_path: str) -> Tuple[str, Dict]:
        """Extract text from TXT file."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            text = file.read()
        
        metadata = {'type': 'txt'}
        return text, metadata
    
    async def _chunk_text(self, text: str, metadata: Dict) -> List[DocumentChunk]:
        """Chunk text into smaller pieces with structure preservation."""
        if not text or not text.strip():
            return []
        
        chunks = []
        
        # Split text into sections (by page markers or major headings)
        sections = self._split_into_sections(text)
        
        chunk_index = 0
        for section_text, section_header, page_num in sections:
            # Chunk this section
            section_chunks = self._chunk_section(
                section_text,
                section_header,
                page_num,
                chunk_index,
                metadata
            )
            chunks.extend(section_chunks)
            chunk_index += len(section_chunks)
        
        return chunks
    
    def _split_into_sections(self, text: str) -> List[Tuple[str, Optional[str], Optional[int]]]:
        """Split text into logical sections."""
        sections = []
        lines = text.split('\n')
        current_section = []
        current_header = None
        current_page = None
        
        for line in lines:
            # Detect page markers
            if line.strip().startswith('--- Page'):
                if current_section:
                    sections.append(('\n'.join(current_section), current_header, current_page))
                current_section = []
                # Extract page number
                try:
                    current_page = int(line.split('Page')[1].split('---')[0].strip())
                except:
                    current_page = None
                current_header = None
                continue
            
            # Detect headers (lines that are all caps, short, and followed by blank line)
            stripped = line.strip()
            if (stripped and 
                len(stripped) < 100 and 
                stripped.isupper() and 
                (stripped.startswith('#') or not any(c.islower() for c in stripped))):
                # Check if next line is blank or content
                if current_section and len(current_section) > 0:
                    # Save current section
                    sections.append(('\n'.join(current_section), current_header, current_page))
                    current_section = []
                current_header = stripped
                continue
            
            # Detect markdown headers
            if stripped.startswith('#'):
                if current_section:
                    sections.append(('\n'.join(current_section), current_header, current_page))
                    current_section = []
                current_header = stripped.lstrip('#').strip()
                continue
            
            current_section.append(line)
        
        # Add final section
        if current_section:
            sections.append(('\n'.join(current_section), current_header, current_page))
        
        # If no sections found, treat entire text as one section
        if not sections:
            sections.append((text, None, None))
        
        return sections
    
    def _chunk_section(
        self,
        section_text: str,
        section_header: Optional[str],
        page_number: Optional[int],
        start_chunk_index: int,
        metadata: Dict
    ) -> List[DocumentChunk]:
        """Chunk a section of text."""
        if not section_text or not section_text.strip():
            return []
        
        chunks = []
        
        # Use LangChain splitter if available
        if self.text_splitter:
            text_chunks = self.text_splitter.split_text(section_text)
        else:
            # Fallback: simple chunking by character count
            chunk_char_size = self.chunk_size * 4
            chunk_overlap_chars = self.chunk_overlap * 4
            text_chunks = []
            start = 0
            
            while start < len(section_text):
                end = start + chunk_char_size
                chunk = section_text[start:end]
                
                # Try to break at sentence or paragraph boundary
                if end < len(section_text):
                    # Look for paragraph break
                    last_para = chunk.rfind('\n\n')
                    if last_para > chunk_char_size * 0.5:  # If found in second half
                        chunk = chunk[:last_para + 2]
                        end = start + len(chunk)
                    else:
                        # Look for sentence break
                        last_sentence = max(
                            chunk.rfind('. '),
                            chunk.rfind('.\n'),
                            chunk.rfind('! '),
                            chunk.rfind('? ')
                        )
                        if last_sentence > chunk_char_size * 0.5:
                            chunk = chunk[:last_sentence + 2]
                            end = start + len(chunk)
                
                text_chunks.append(chunk.strip())
                start = end - chunk_overlap_chars
        # Filter and create chunk objects
        chunk_index = start_chunk_index
        for text_chunk in text_chunks:
            text_chunk = text_chunk.strip()
            if not text_chunk:
                continue
            
            # Check minimum size (in tokens)
            token_count = self.count_tokens(text_chunk)
            if token_count < self.min_chunk_size:
                # Merge with previous chunk if too small
                if chunks:
                    chunks[-1].content += f"\n\n{text_chunk}"
                    chunks[-1].full_content = chunks[-1].content
                    if section_header and not chunks[-1].section_header:
                        chunks[-1].section_header = section_header
                        chunks[-1].full_content = f"{section_header}\n\n{chunks[-1].content}"
                else:
                    # First chunk, keep it even if small
                    chunk = DocumentChunk(
                        content=text_chunk,
                        chunk_index=chunk_index,
                        metadata=metadata.copy(),
                        page_number=page_number,
                        section_header=section_header
                    )
                    chunks.append(chunk)
                    chunk_index += 1
            else:
                chunk = DocumentChunk(
                    content=text_chunk,
                    chunk_index=chunk_index,
                    metadata=metadata.copy(),
                    page_number=page_number,
                    section_header=section_header
                )
                chunks.append(chunk)
                chunk_index += 1
        
        return chunks
