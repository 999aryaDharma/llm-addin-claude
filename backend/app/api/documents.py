"""
Document upload and management endpoints with async background processing
"""
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Query
from typing import List, Optional, Tuple
import logging
from pathlib import Path
import hashlib
from datetime import datetime

from app.models.document import (
    DocumentResponse,
    DocumentMetadata,
    DocumentType,
    DocumentStatus,
    DocumentListResponse,
    DocumentSearchRequest,
    DocumentSearchResponse,
    DocumentSearchResult
)
from app.core.chroma_engine import chroma_engine
from app.core.chunking import default_chunker
from app.core.summarizer import text_summarizer
from app.services.parser import document_parser
from app.utils.storage import storage_manager
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


import re
from datetime import datetime
import os

def _get_year_from_date(date_obj) -> Optional[int]:
    """Helper untuk mengekstrak tahun dari objek datetime."""
    if date_obj:
        return date_obj.year
    return None

def _is_generic(value: Optional[str], field_type: str) -> bool:
    """
    Cek apakah nilai metadata adalah string default/generik yang tidak berguna.
    """
    if not value:
        return True
    if isinstance(value, str):
        value_low = value.lower().strip()
    else:
        return True
    
    if not value_low:
        return True
    
    if field_type == "title":
        # Daftar judul generik yang sering muncul
        generics = ["untitled", "microsoft word", "word document", "document1", "draft", "abstrak"]
        return any(g in value_low for g in generics)
    
    if field_type == "author":
        # Daftar penulis generik
        generics = ["user", "admin", "owner", "author", "administrator"]
        return value_low in generics
        
    return False

def _find_year_from_text(text: str) -> Optional[int]:
    """
    Cari tahun publikasi (misal: 1990-2029) di dalam teks halaman pertama.
    """
    if not text:
        return None
    # Mencari 4 digit angka yang diawali dengan 199x atau 20xx
    match = re.search(r'\b(199\d|20[0-2]\d)\b', text)
    if match:
        return int(match.group(1))
    return None
    
def _find_title_from_text(text: str, max_lines_to_check: int = 15) -> Tuple[Optional[str], int]:
    """
    Menemukan judul yang paling mungkin dari beberapa baris pertama teks menggunakan sistem skor.
    Mengembalikan tuple (judul, index_baris).
    """
    if not text:
        return None, -1

    lines = text.split('\n')
    best_candidate = (None, -1, -1)  # (line, index, score)

    # Daftar kata kunci yang jika ada, baris tersebut BUKAN judul
    negative_keywords = ['abstrak', 'abstract', 'pendahuluan', 'introduction', 'issn', 'vol', 'no.', 'http:', 'https:', 'www.']
    
    for i, line in enumerate(lines[:max_lines_to_check]):
        line_stripped = line.strip()
        
        # Lewati baris yang terlalu pendek atau panjang
        if not (5 < len(line_stripped) < 200):
            continue

        # Beri penalti berat jika mengandung kata kunci negatif
        if any(keyword in line_stripped.lower() for keyword in negative_keywords):
            continue

        score = 0
        words = line_stripped.split()
        
        # Skor berdasarkan jumlah kata
        if 3 <= len(words) <= 25:
            score += 20

        # Skor berdasarkan kapitalisasi (ciri khas judul)
        capitalized_words = sum(1 for word in words if word and word[0].isupper())
        if capitalized_words / len(words) > 0.5: # Lebih dari 50% kata diawali huruf besar
            score += 30
        
        # Skor bonus jika semua kata diawali huruf besar (Title Case)
        if all(word[0].isupper() for word in words if word.isalpha()):
            score += 15

        # Penalti untuk baris pertama (seringkali header instansi)
        if i == 0:
            score -= 10
        
        if score > best_candidate[2]:
            best_candidate = (line_stripped, i, score)

    return best_candidate[0], best_candidate[1]

def _find_author_from_text(lines: List[str], title_line_index: int) -> Optional[str]:
    """
    Cari baris yang kemungkinan adalah penulis, di bawah baris judul.
    """
    if title_line_index == -1 or not lines:
        return None

    # Cek 5 baris di bawah judul
    search_range = range(title_line_index + 1, min(title_line_index + 6, len(lines)))
    
    potential_authors = []

    for i in search_range:
        line = lines[i].strip()
        
        # Lewati baris kosong
        if not line:
            continue
            
        # Jika baris terlalu panjang, itu mungkin abstrak atau paragraf, hentikan.
        if len(line) > 150:
            break
            
        # Cek keyword 'by' or 'oleh'
        match = re.search(r'\b(by|oleh)\b:?\s+(.*)', line, re.IGNORECASE)
        if match:
            author_name = match.group(2).strip()
            # Hindari mengambil teks yang terlalu panjang setelah 'by'
            if 0 < len(author_name) < 100:
                potential_authors.append(author_name)
                continue # Lanjut ke baris berikutnya jika sudah ketemu format ini
                
        # Heuristik kedua: Cek jika baris itu sendiri adalah nama
        # Misal: "John Doe, Jane Smith", "Jane Smith, PhD"
        # Ciri: pendek (2-7 kata), banyak huruf besar
        words = line.split()
        if 2 <= len(words) <= 10:
            # Cek jika setidaknya 2 kata diawali huruf besar (heuristik untuk nama) atau mengandung ','
            capitalized_words = sum(1 for word in words if word and word[0].isupper())
            if capitalized_words >= 2 or ',' in line:
                potential_authors.append(line)

    # Gabungkan semua penulis potensial yang ditemukan (misal: ada beberapa baris penulis)
    if potential_authors:
        # Bersihkan dari duplikat dan gabungkan
        unique_authors = list(dict.fromkeys(potential_authors))
        return ", ".join(unique_authors)

    return None

async def process_document_background(
    file_path: Path,
    document_id: str,
    filename: str,
    doc_type: DocumentType
):
    """
    Background task to process uploaded document for RAG
    - Parse document
    - Extract metadata (title, author, year)
    - Chunk text
    - Generate embeddings
    - Store in ChromaDB
    - Generate summary
    """
    try:
        logger.info(f"Starting background processing for {document_id}")
        
        # Parse document to get text content
        content = await document_parser.parse_file(file_path, doc_type)
        logger.info(f"Parsed document {document_id}: {len(content)} characters")
        
        # Extract title, author, year using smart parsing logic
        from typing import List, Any, Optional, Tuple
        from docx import Document as DocxDocument
        import pypdf
        
        # Fallback default: nama file
        filename_title = os.path.basename(file_path).rsplit('.', 1)[0].replace('_', ' ').replace('-', ' ').title()
        
        # Nilai dari properti file
        meta_title: Optional[str] = None
        meta_author: Optional[str] = None
        meta_year: Optional[int] = None
        
        # Nilai dari analisis konten
        text_title: Optional[str] = None
        text_author: Optional[str] = None
        text_year: Optional[int] = None
        title_line_index: int = -1

        try:
            # --- Ekstraksi metadata berdasarkan tipe file ---
            if doc_type == DocumentType.WORD:
                doc = DocxDocument(file_path)
                props = doc.core_properties
                meta_title = props.title
                meta_author = props.author
                date_to_use = props.modified or props.created
                meta_year = _get_year_from_date(date_to_use)
                
                # Ambil teks dari ~5 paragraf pertama untuk halaman pertama
                first_page_text = "\n".join([p.text for p in doc.paragraphs[:5]])
                
            elif doc_type == DocumentType.PDF:
                with open(file_path, 'rb') as f:
                    reader = pypdf.PdfReader(f)
                    if reader.pages:
                        # Ambil teks halaman pertama untuk analisis
                        first_page_text = reader.pages[0].extract_text() or ""
                    
                    meta = reader.metadata
                    if meta:
                        meta_title = meta.title
                        meta_author = meta.author
                        meta_year = _get_year_from_date(meta.creation_date)
            elif doc_type == DocumentType.TEXT:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content_to_parse = f.read()
                first_page_text = content_to_parse[:2000] # Ambil 2000 karakter pertama
            else:
                first_page_text = content[:2000]  # Default fallback
        
            # --- Langkah 2: Logika Heuristik "Pintar" ---
            
            # 2a. Dapatkan semua baris dari teks halaman pertama
            first_page_lines = first_page_text.split('\n')

            # 2b. Coba cari judul & index-nya
            text_title, title_line_index = _find_title_from_text(first_page_text)
            
            # 2c. Coba cari penulis berdasarkan index judul
            text_author = _find_author_from_text(first_page_lines, title_line_index)

            # 2d. Coba cari tahun
            text_year = _find_year_from_text(first_page_text)

            # --- Langkah 3: Tentukan Nilai Final ---
            
            # JUDUL: Prioritaskan meta title JIKA tidak generik,
            # lalu text title JIKA tidak generik,
            # baru filename.
            final_title = filename_title # Default fallback
            if not _is_generic(meta_title, "title"):
                final_title = meta_title
            elif not _is_generic(text_title, "title"):
                final_title = text_title

            # PENULIS: Prioritaskan meta author JIKA tidak generik,
            # baru penulis dari teks JIKA ditemukan.
            final_author = "Unknown Author"
            if not _is_generic(meta_author, "author"):
                final_author = meta_author
            elif text_author: # <-- Gunakan hasil pencarian teks
                final_author = text_author

            # TAHUN: Prioritaskan tahun dari teks (publikasi)
            # baru tahun dari file (kreasi/modifikasi).
            final_year = text_year if text_year else meta_year
            
            logger.info(f"Extracted metadata: title='{final_title}', author='{final_author}', year={final_year}")
        
        except Exception as e:
            logger.error(f"Error extracting metadata from {filename}: {e}")
            final_title = filename_title
            final_author = "Unknown Author"
            final_year = None
        
        # Chunk document
        chunks = default_chunker.smart_chunk(content, doc_type)
        logger.info(f"Created {len(chunks)} chunks from {document_id}")
        
        # Prepare metadata for chunks
        chunk_metadatas = []
        chunk_texts = []
        chunk_ids = []
        
        for idx, chunk in enumerate(chunks):
            chunk_id = f"{document_id}_chunk_{idx}"
            chunk_ids.append(chunk_id)
            chunk_texts.append(chunk.page_content)
            chunk_metadatas.append({
                "document_id": document_id,
                "filename": filename,
                "document_type": doc_type.value,
                "chunk_index": idx,
                "title": final_title,
                "author": final_author,
                "year": final_year,
                "timestamp": datetime.now().isoformat()
            })
        
        # Add to ChromaDB (this generates embeddings internally)
        await chroma_engine.add_documents(
            texts=chunk_texts,
            metadatas=chunk_metadatas,
            ids=chunk_ids
        )
        logger.info(f"Added {len(chunks)} chunks to ChromaDB for {document_id}")
        
        # Generate summary for context
        summary = await text_summarizer.summarize_for_context(content[:10000])
        logger.info(f"Generated summary for {document_id}")
        
        # Update document status (you may want to store this in a database)
        logger.info(f"Document {document_id} processed successfully")
        
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}", exc_info=True)
        # Update status to failed


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Upload a document and process it in background for RAG
    
    - Saves file
    - Returns immediately with document ID
    - Processes in background (chunking, embedding, indexing)
    """
    try:
        # Validate file type
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
            )
        
        # Determine document type
        doc_type_map = {
            ".docx": DocumentType.WORD,
            ".xlsx": DocumentType.EXCEL,
            ".pdf": DocumentType.PDF,
            ".txt": DocumentType.TEXT
        }
        doc_type = doc_type_map.get(file_ext, DocumentType.TEXT)
        
        # Read file content
        content = await file.read()
        
        # Check file size
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE} bytes"
            )
        
        # Generate document ID
        document_id = hashlib.sha256(
            f"{file.filename}_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Save file
        file_path = await storage_manager.save_file(
            content,
            file.filename,
            subfolder=doc_type.value
        )
        logger.info(f"Saved file {file.filename} to {file_path}")
        
        # Create metadata
        metadata = DocumentMetadata(
            document_id=document_id,
            filename=file.filename,
            document_type=doc_type,
            size=len(content),
            status=DocumentStatus.PROCESSING
        )
        
        # Add background task for processing
        background_tasks.add_task(
            process_document_background,
            file_path,
            document_id,
            file.filename,
            doc_type
        )
        
        return DocumentResponse(
            success=True,
            document_id=document_id,
            message=f"Document uploaded successfully. Processing in background.",
            metadata=metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    """Get document information by ID"""
    try:
        # Get from ChromaDB
        doc = chroma_engine.get_document(f"{document_id}_chunk_0")
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Extract metadata
        metadata_dict = doc["metadata"]
        metadata = DocumentMetadata(
            document_id=document_id,
            filename=metadata_dict.get("filename", "unknown"),
            document_type=DocumentType(metadata_dict.get("document_type", "text")),
            size=0,  # Not stored in chunk metadata
            status=DocumentStatus.INDEXED
        )
        
        return DocumentResponse(
            success=True,
            document_id=document_id,
            message="Document found",
            metadata=metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{document_id}", response_model=DocumentResponse)
async def delete_document(document_id: str):
    """Delete a document and all its chunks"""
    try:
        # Delete from ChromaDB by metadata filter
        chroma_engine.delete_by_metadata({"document_id": document_id})
        
        return DocumentResponse(
            success=True,
            document_id=document_id,
            message="Document deleted successfully"
        )
        
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    document_type: Optional[DocumentType] = None
):
    """List all documents with pagination"""
    try:
        offset = (page - 1) * page_size
        
        # Build filter
        filter_metadata = {}
        if document_type:
            filter_metadata["document_type"] = document_type.value
        
        # Get documents from ChromaDB
        result = chroma_engine.list_documents(
            limit=page_size,
            offset=offset,
            filter_metadata=filter_metadata if filter_metadata else None
        )
        
        # Group by document_id (since we get chunks)
        documents_dict = {}
        for idx, metadata in enumerate(result["metadatas"]):
            doc_id = metadata["document_id"]
            if doc_id not in documents_dict:
                documents_dict[doc_id] = DocumentMetadata(
                    document_id=doc_id,
                    filename=metadata["filename"],
                    document_type=DocumentType(metadata["document_type"]),
                    size=0,
                    status=DocumentStatus.INDEXED
                )
        
        documents = list(documents_dict.values())
        
        return DocumentListResponse(
            documents=documents,
            total=len(documents),
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=DocumentSearchResponse)
async def search_documents(request: DocumentSearchRequest):
    """
    Semantic search across documents
    """
    try:
        # Build metadata filter
        filter_metadata = {}
        if request.document_ids:
            # ChromaDB doesn't support "in" operator directly, so we'll filter after
            pass
        if request.document_types:
            # Filter by first type only (ChromaDB limitation)
            filter_metadata["document_type"] = request.document_types[0].value
        
        # Perform semantic search
        results = await chroma_engine.query_similar(
            query_text=request.query,
            n_results=request.limit,
            filter_metadata=filter_metadata if filter_metadata else None
        )
        
        # Format results
        search_results = []
        for idx in range(len(results["documents"])):
            # Filter by document_ids if specified
            doc_id = results["metadatas"][idx]["document_id"]
            if request.document_ids and doc_id not in request.document_ids:
                continue
            
            result = DocumentSearchResult(
                document_id=doc_id,
                chunk_id=results["ids"][idx],
                content=results["documents"][idx],
                score=float(1 - results["distances"][idx]),  # Convert distance to similarity
                metadata=results["metadatas"][idx] if request.include_metadata else None
            )
            search_results.append(result)
        
        return DocumentSearchResponse(
            query=request.query,
            results=search_results[:request.limit],
            total_found=len(search_results)
        )
        
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=dict)
async def get_collection_stats():
    """Get statistics about the document collection"""
    try:
        stats = chroma_engine.get_collection_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))