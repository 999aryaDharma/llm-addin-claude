"""
LangChain configuration and model initialization
"""
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.memory import ConversationBufferMemory
from typing import Optional

from app.config import settings


class LangChainManager:
    """Centralized LangChain model management"""
    
    def __init__(self):
        self._llm = None
        self._embeddings = None
        self._memory = {}
    
    def get_llm(
        self, 
        temperature: float = 0.7,
        model: str = "gemini-pro"
    ) -> ChatGoogleGenerativeAI:
        """Get LLM instance"""
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=temperature,
            convert_system_message_to_human=True
        )
    
    def get_embeddings(self) -> GoogleGenerativeAIEmbeddings:
        """Get embeddings model"""
        if self._embeddings is None:
            self._embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=settings.GEMINI_API_KEY
            )
        return self._embeddings
    
    def get_memory(self, session_id: str) -> ConversationBufferMemory:
        """Get or create conversation memory"""
        if session_id not in self._memory:
            self._memory[session_id] = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
        return self._memory[session_id]
    
    def clear_memory(self, session_id: str):
        """Clear conversation memory"""
        if session_id in self._memory:
            del self._memory[session_id]


# Global instance
langchain_manager = LangChainManager()


# Reusable Prompt Templates
WORD_REWRITE_TEMPLATE = """Tulis ulang teks berikut dengan gaya {style}.

Konteks referensi (jika ada):
{context}

Teks asli:
{text}

Instruksi tambahan:
- Pertahankan makna utama
- Sesuaikan dengan gaya {style}
- Jaga panjang teks serupa dengan aslinya

Hasil tulis ulang:"""

WORD_SUMMARIZE_TEMPLATE = """Buat ringkasan yang jelas dan padat dari teks berikut.

Konteks dokumen:
{context}

Teks untuk diringkas:
{text}

Panjang target: {length} kata

Ringkasan:"""

EXCEL_FORMULA_TEMPLATE = """Buat formula Excel berdasarkan deskripsi berikut.

Data Context:
- Kolom tersedia: {columns}
- Range data: {range}
- Sheet: {sheet_name}

Deskripsi tugas:
{description}

Output dalam format:
Formula: [formula Excel yang valid]
Penjelasan: [penjelasan singkat cara kerja formula]
Contoh: [contoh penggunaan]

Response:"""

EXCEL_QUERY_TEMPLATE = """Analisis data Excel dan jawab pertanyaan berikut.

Data Summary:
{data_summary}

Kolom: {columns}
Jumlah baris: {row_count}

Pertanyaan:
{question}

Berikan jawaban yang:
1. Langsung menjawab pertanyaan
2. Didukung oleh data
3. Menyertakan angka spesifik jika relevan
4. Singkat dan jelas

Jawaban:"""

EXCEL_INSIGHT_TEMPLATE = """Analisis dataset Excel ini dan berikan insight mendalam.

Data Summary:
{data_summary}

Kolom dan tipe data:
{column_info}

Statistik dasar:
{statistics}

Berikan insight dalam format:
1. Pola utama yang terlihat
2. Anomali atau outlier
3. Rekomendasi analisis lanjutan
4. Pertanyaan yang bisa dijawab dari data ini

Insight:"""

COMPARISON_TEMPLATE = """Bandingkan dua sumber berikut berdasarkan pertanyaan.

Pertanyaan: {question}

Sumber 1 ({source1_title}):
{source1_content}

Sumber 2 ({source2_title}):
{source2_content}

Berikan perbandingan dalam format:
- Persamaan: [poin-poin persamaan]
- Perbedaan: [poin-poin perbedaan]
- Kesimpulan: [sintesis dari kedua sumber]

Perbandingan:"""


def create_word_prompt(task: str) -> PromptTemplate:
    """Create prompt template for Word tasks"""
    templates = {
        "rewrite": WORD_REWRITE_TEMPLATE,
        "summarize": WORD_SUMMARIZE_TEMPLATE
    }
    
    template = templates.get(task, WORD_REWRITE_TEMPLATE)
    
    return PromptTemplate(
        template=template,
        input_variables=list(set(
            [var for var in ["text", "style", "context", "length"] 
             if f"{{{var}}}" in template]
        ))
    )


def create_excel_prompt(task: str) -> PromptTemplate:
    """Create prompt template for Excel tasks"""
    templates = {
        "formula": EXCEL_FORMULA_TEMPLATE,
        "query": EXCEL_QUERY_TEMPLATE,
        "insight": EXCEL_INSIGHT_TEMPLATE
    }
    
    template = templates.get(task, EXCEL_QUERY_TEMPLATE)
    
    return PromptTemplate(
        template=template,
        input_variables=list(set(
            [var for var in ["description", "columns", "range", "sheet_name", 
                            "question", "data_summary", "row_count", "column_info", 
                            "statistics"]
             if f"{{{var}}}" in template]
        ))
    )


def create_comparison_prompt() -> PromptTemplate:
    """Create prompt for document comparison"""
    return PromptTemplate(
        template=COMPARISON_TEMPLATE,
        input_variables=[
            "question", "source1_title", "source1_content",
            "source2_title", "source2_content"
        ]
    )