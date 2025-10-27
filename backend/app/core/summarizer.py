"""
Text summarization module with batch processing for Word documents
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Optional, Dict, Any
import asyncio
import logging

from app.services.llm_service import llm_service
from app.config import settings

logger = logging.getLogger(__name__)


class TextSummarizer:
    """Summarize and analyze text content with batch processing"""
    
    def __init__(self):
        self.llm = llm_service.llm
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        self.batch_size = settings.SUMMARY_BATCH_SIZE
    
    async def summarize_text(
        self,
        text: str,
        summary_type: str = "concise"
    ) -> str:
        """
        Summarize text content using map-reduce with batch processing
        
        Args:
            text: Input text to summarize
            summary_type: Type of summary (concise, detailed, bullets)
            
        Returns:
            Summarized text
        """
        try:
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            logger.info(f"Split text into {len(chunks)} chunks")
            
            if len(chunks) <= 1:
                # Short text, direct summarization
                return await self._summarize_single(text, summary_type)
            
            # Batch process chunks
            chunk_summaries = await self._summarize_chunks_batch(chunks)
            
            # Combine summaries
            combined = "\n\n".join(chunk_summaries)
            
            # Final summarization
            final_summary = await self._summarize_single(combined, summary_type)
            
            # Format based on summary type
            if summary_type == "bullets":
                final_summary = await self._format_as_bullets(final_summary)
            
            return final_summary
            
        except Exception as e:
            logger.error(f"Error summarizing text: {str(e)}")
            raise
    
    async def _summarize_chunks_batch(self, chunks: List[str]) -> List[str]:
        """
        Summarize chunks in batches for efficiency
        
        Args:
            chunks: List of text chunks
            
        Returns:
            List of chunk summaries
        """
        all_summaries = []
        
        # Process in batches
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i:i + self.batch_size]
            logger.info(f"Processing batch {i//self.batch_size + 1}/{(len(chunks)-1)//self.batch_size + 1}")
            
            # Create tasks for batch
            tasks = [self._summarize_chunk(chunk, idx) for idx, chunk in enumerate(batch)]
            
            # Execute batch concurrently
            batch_summaries = await asyncio.gather(*tasks)
            all_summaries.extend(batch_summaries)
        
        return all_summaries
    
    async def _summarize_chunk(self, chunk: str, chunk_idx: int) -> str:
        """
        Summarize a single chunk

        Args:
            chunk: Text chunk
            chunk_idx: Chunk index for logging

        Returns:
            Chunk summary
        """
        try:
            prompt = f"""Buatlah ringkasan singkat dari teks berikut dengan tetap mempertahankan informasi kunci:

{chunk}

Ringkasan:"""

            summary = await llm_service.generate_text(prompt)
            logger.debug(f"Summarized chunk {chunk_idx}")
            return summary

        except Exception as e:
            logger.error(f"Error summarizing chunk {chunk_idx}: {str(e)}")
            return chunk[:200]  # Fallback to truncated chunk
    
    async def _summarize_single(self, text: str, summary_type: str = "concise") -> str:
        """Summarize a single text without chunking"""
        try:
            prompt_templates = {
                "concise": "Buatlah ringkasan singkat dari teks berikut:\n\n{text}\n\nRingkasan:",
                "detailed": "Buatlah ringkasan terperinci yang mencakup semua poin utama:\n\n{text}\n\nRingkasan Terperinci:",
                "bullets": "Buatlah ringkasan dalam bentuk poin-poin:\n\n{text}\n\nRingkasan Poin:"
            }

            template = prompt_templates.get(summary_type, prompt_templates["concise"])
            prompt = template.format(text=text)

            summary = await llm_service.generate_text(prompt)
            return summary

        except Exception as e:
            logger.error(f"Error in single summarization: {str(e)}")
            raise
    
    async def extract_key_points(self, text: str, num_points: int = 5) -> List[str]:
        """Extract key points from text"""
        try:
            prompt = f"""Ekstrak {num_points} poin penting dari teks berikut.
Kembalikan hanya poin-poin penting dalam bentuk daftar bernomor.

Teks:
{text}

Poin Penting:"""

            response = await llm_service.generate_text(prompt)

            # Parse response into list
            points = [
                line.strip().lstrip('0123456789.-) ')
                for line in response.split('\n')
                if line.strip() and any(c.isalnum() for c in line)
            ]

            return points[:num_points]

        except Exception as e:
            logger.error(f"Error extracting key points: {str(e)}")
            raise
    
    async def analyze_writing_style(self, text: str) -> Dict[str, Any]:
        """Analyze writing style and tone"""
        try:
            prompt = f"""Analisis gaya penulisan dari teks berikut dan berikan:
1. Tone keseluruhan (misalnya: formal, santai, akademis, persuasif)
2. Level pembaca (misalnya: pemula, menengah, lanjutan)
3. Fitur gaya penulisan yang menonjol
4. Saran untuk perbaikan

Teks:
{text}

Kembalikan dalam format JSON dengan keys: tone, reading_level, features (array), suggestions (array)"""

            response = await llm_service.generate_json(prompt)

            return response

        except Exception as e:
            logger.error(f"Error analyzing style: {str(e)}")
            raise
    
    async def _format_as_bullets(self, text: str) -> str:
        """Format text as bullet points"""
        prompt = f"""Ubah teks berikut menjadi poin-poin yang jelas dan ringkas:

{text}

Poin-poin:"""

        return await llm_service.generate_text(prompt)
    
    async def generate_outline(self, text: str) -> Dict[str, Any]:
        """Generate an outline from text"""
        try:
            prompt = f"""Buatlah outline hierarkis dari teks berikut.
Sertakan bagian utama dan sub-bagian.

Teks:
{text[:3000]}

Kembalikan dalam format JSON dengan struktur:
{{
  "sections": [
    {{
      "title": "Judul Bagian",
      "subsections": ["Sub-bagian 1", "Sub-bagian 2"]
    }}
  ]
}}"""

            response = await llm_service.generate_json(prompt)

            return response

        except Exception as e:
            logger.error(f"Error generating outline: {str(e)}")
            raise
    
    async def compare_texts(self, text1: str, text2: str) -> Dict[str, Any]:
        """Compare two texts and identify differences"""
        try:
            prompt = f"""Bandingkan kedua teks berikut dan identifikasi:
1. Perbedaan utama dalam konten
2. Perbedaan dalam gaya/tone
3. Skor kemiripan (0-100)

Teks 1:
{text1[:2000]}

Teks 2:
{text2[:2000]}

Kembalikan dalam format JSON dengan keys: content_differences (array), style_differences (array), similarity_score (number), summary (string)"""

            response = await llm_service.generate_json(prompt)

            return response

        except Exception as e:
            logger.error(f"Error comparing texts: {str(e)}")
            raise
    
    async def summarize_for_context(self, text: str) -> str:
        """
        Create a summary optimized for use as context in RAG

        Args:
            text: Input text

        Returns:
            Context-optimized summary
        """
        try:
            prompt = f"""Buatlah ringkasan komprehensif yang mempertahankan:
- Topik dan tema utama
- Fakta kunci dan poin data
- Hubungan dan koneksi penting
- Istilah teknis dan definisi

Teks:
{text}

Ringkasan Konteks:"""

            summary = await llm_service.generate_text(prompt)
            return summary

        except Exception as e:
            logger.error(f"Error creating context summary: {str(e)}")
            raise


# Global instance
text_summarizer = TextSummarizer()