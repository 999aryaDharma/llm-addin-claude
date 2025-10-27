from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    TokenTextSplitter,
    MarkdownTextSplitter
)
from langchain_core.documents import Document
from typing import List, Optional
from loguru import logger


class DocumentChunker:
    """Handle document chunking dengan berbagai strategi"""
    
    def __init__(
        self,
        chunk_size: int = 1500,
        chunk_overlap: int = 100,
        length_function: callable = len
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.length_function = length_function
    
    def chunk_text(
        self,
        text: str,
        metadata: Optional[dict] = None,
        splitter_type: str = "recursive"
    ) -> List[Document]:
        """
        Chunk text into documents
        
        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk
            splitter_type: Type of splitter ('recursive', 'token', 'markdown')
            
        Returns:
            List of Document objects
        """
        try:
            # Select splitter
            if splitter_type == "token":
                splitter = TokenTextSplitter(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap
                )
            elif splitter_type == "markdown":
                splitter = MarkdownTextSplitter(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap
                )
            else:  # recursive (default)
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                    length_function=self.length_function,
                    separators=["\n\n", "\n", ". ", " ", ""]
                )
            
            # Split text
            chunks = splitter.split_text(text)
            
            # Create documents
            documents = []
            for i, chunk in enumerate(chunks):
                doc_metadata = metadata.copy() if metadata else {}
                doc_metadata.update({
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                })
                
                documents.append(Document(
                    page_content=chunk,
                    metadata=doc_metadata
                ))
            
            logger.info(f"Chunked text into {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error chunking text: {e}")
            raise
    
    def chunk_by_sections(
        self,
        text: str,
        section_headers: List[str],
        metadata: Optional[dict] = None
    ) -> List[Document]:
        """
        Chunk text by section headers (untuk Word documents)
        
        Args:
            text: Full text
            section_headers: List of section header texts
            metadata: Base metadata
            
        Returns:
            List of Document objects, one per section
        """
        try:
            documents = []
            current_pos = 0
            
            for i, header in enumerate(section_headers):
                # Find header position
                header_pos = text.find(header, current_pos)
                if header_pos == -1:
                    continue
                
                # Find next header or end of text
                next_pos = len(text)
                if i + 1 < len(section_headers):
                    next_header_pos = text.find(section_headers[i + 1], header_pos + len(header))
                    if next_header_pos != -1:
                        next_pos = next_header_pos
                
                # Extract section content
                section_content = text[header_pos:next_pos].strip()
                
                # Create document
                doc_metadata = metadata.copy() if metadata else {}
                doc_metadata.update({
                    "section_header": header,
                    "section_index": i,
                    "total_sections": len(section_headers)
                })
                
                documents.append(Document(
                    page_content=section_content,
                    metadata=doc_metadata
                ))
                
                current_pos = next_pos
            
            logger.info(f"Chunked into {len(documents)} sections")
            return documents
            
        except Exception as e:
            logger.error(f"Error chunking by sections: {e}")
            raise
    
    def smart_chunk(
        self,
        text: str,
        doc_type: str,
        metadata: Optional[dict] = None
    ) -> List[Document]:
        """
        Smart chunking based on document type
        
        Args:
            text: Text to chunk
            doc_type: Document type ('word', 'excel', 'pdf', 'markdown')
            metadata: Metadata to attach
            
        Returns:
            List of Document objects
        """
        if doc_type == "markdown":
            return self.chunk_text(text, metadata, splitter_type="markdown")
        elif doc_type == "word":
            # Use recursive splitter with paragraph separators
            return self.chunk_text(text, metadata, splitter_type="recursive")
        elif doc_type == "excel":
            # For Excel, might want token-based to preserve data structure
            return self.chunk_text(text, metadata, splitter_type="token")
        else:
            return self.chunk_text(text, metadata, splitter_type="recursive")


# Global instance
default_chunker = DocumentChunker()