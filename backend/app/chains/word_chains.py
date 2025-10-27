from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser, StructuredOutputParser, ResponseSchema
from typing import Dict, Any, List
from app.core.langchain_setup import LLMFactory
from loguru import logger


class WordChains:
    """LangChain chains untuk Word processing"""
    
    def __init__(self, llm=None):
        self.llm = llm or LLMFactory.create_llm()
    
    def create_rewrite_chain(self) -> LLMChain:
        """Create chain untuk text rewriting"""
        template = """Anda adalah asisten penulisan yang ahli. Tulis ulang teks berikut sesuai dengan instruksi.

Teks Asli:
{text}

Instruksi:
{instruction}

{style_instruction}

{context_instruction}

Berikan teks yang ditulis ulang dengan:
1. Mengikuti instruksi dengan tepat
2. Mempertahankan makna asli dan informasi kunci
3. Meningkatkan kejelasan dan keterbacaan
4. Menggunakan tone dan gaya yang sesuai

Teks yang Ditulis Ulang:"""
        
        prompt = PromptTemplate(
            input_variables=["text", "instruction", "style_instruction", "context_instruction"],
            template=template
        )
        
        return LLMChain(llm=self.llm, prompt=prompt)
    
    def create_analysis_chain(self) -> LLMChain:
        """Create chain untuk text analysis"""
        template = """Anda adalah analis teks yang ahli. Analisis teks berikut dan berikan wawasan.

Teks:
{text}

Jenis Analisis: {analysis_type}

{context_instruction}

Berikan analisis komprehensif yang mencakup:
1. Observasi kunci tentang teks
2. Penilaian gaya penulisan dan tone
3. Kekuatan dan area untuk perbaikan
4. Saran spesifik yang dapat ditindaklanjuti

Analisis:"""
        
        prompt = PromptTemplate(
            input_variables=["text", "analysis_type", "context_instruction"],
            template=template
        )
        
        return LLMChain(llm=self.llm, prompt=prompt)
    
    def create_query_chain(self) -> LLMChain:
        """Create chain untuk answering queries with context"""
        template = """Anda adalah asisten yang membantu menjawab pertanyaan berdasarkan konteks yang diberikan.

Konteks:
{context}

Pertanyaan:
{query}

Instruksi:
- Jawab hanya berdasarkan konteks yang diberikan
- Jika konteks tidak mengandung informasi yang cukup, katakan demikian
- Jadilah ringkas namun lengkap
- Kutip bagian spesifik dari konteks jika relevan

Jawaban:"""
        
        prompt = PromptTemplate(
            input_variables=["context", "query"],
            template=template
        )
        
        return LLMChain(llm=self.llm, prompt=prompt)
    
    def create_summary_chain(self) -> LLMChain:
        """Create chain untuk summarization"""
        template = """Ringkas teks berikut secara ringkas dengan tetap mempertahankan informasi kunci.

Teks:
{text}

Jenis Ringkasan: {summary_type}

{additional_instructions}

Berikan ringkasan {summary_type} yang menangkap poin-poin esensial.

Ringkasan:"""
        
        prompt = PromptTemplate(
            input_variables=["text", "summary_type", "additional_instructions"],
            template=template
        )
        
        return LLMChain(llm=self.llm, prompt=prompt)
    
    def create_comparison_chain(self) -> LLMChain:
        """Create chain untuk document comparison"""
        template = """Bandingkan kedua dokumen berikut dan identifikasi perbedaan dan kesamaannya.

Dokumen 1:
{doc1}

Dokumen 2:
{doc2}

Jenis Perbandingan: {comparison_type}

Berikan perbandingan terperinci yang mencakup:
1. Perbedaan kunci
2. Kesamaan
3. Perubahan penting dalam konten, gaya, atau struktur
4. Penilaian keseluruhan

Perbandingan:"""
        
        prompt = PromptTemplate(
            input_variables=["doc1", "doc2", "comparison_type"],
            template=template
        )
        
        return LLMChain(llm=self.llm, prompt=prompt)
    
    def create_grammar_check_chain(self) -> LLMChain:
        """Create chain untuk grammar and style checking"""
        template = """Anda adalah editor ahli. Tinjau teks berikut untuk masalah tata bahasa, ejaan, dan gaya.

Teks:
{text}

Berikan:
1. Daftar kesalahan tata bahasa dan ejaan beserta koreksinya
2. Saran gaya untuk perbaikan
3. Penilaian keterbacaan
4. Rekomendasi keseluruhan

Tinjauan:"""
        
        prompt = PromptTemplate(
            input_variables=["text"],
            template=template
        )
        
        return LLMChain(llm=self.llm, prompt=prompt)
    
    def create_citation_chain(self) -> LLMChain:
        """Create chain untuk fact-checking and citation"""
        template = """Anda adalah asisten pemeriksaan fakta. Tinjau teks berikut untuk klaim yang memerlukan sitasi atau verifikasi.

Teks:
{text}

{context_instruction}

Identifikasi:
1. Klaim faktual yang harus disitasi
2. Pernyataan yang berpotensi dipertanyakan
3. Rekomendasi untuk verifikasi
4. Format sitasi yang disarankan jika berlaku

Analisis:"""
        
        prompt = PromptTemplate(
            input_variables=["text", "context_instruction"],
            template=template
        )
        
        return LLMChain(llm=self.llm, prompt=prompt)
    
    def create_section_outline_chain(self) -> LLMChain:
        """Create chain untuk generating section outlines"""
        template = """Berdasarkan konten berikut, buatlah outline bagian yang logis.

Konten:
{content}

Persyaratan:
- Buat bagian hierarkis yang jelas
- Gunakan heading yang deskriptif
- Pastikan alur yang logis
- Sertakan sub-bagian jika sesuai

{additional_requirements}

Outline:"""
        
        prompt = PromptTemplate(
            input_variables=["content", "additional_requirements"],
            template=template
        )
        
        return LLMChain(llm=self.llm, prompt=prompt)
    
    # Convenience methods to run chains
    
    def rewrite_text(self, text: str, instruction: str, style: str = None, context: str = None) -> str:
        """Rewrite text according to instruction"""
        try:
            chain = self.create_rewrite_chain()
            
            style_instruction = f"Writing Style: {style}" if style else ""
            context_instruction = f"Additional Context: {context}" if context else ""
            
            result = chain.run(
                text=text,
                instruction=instruction,
                style_instruction=style_instruction,
                context_instruction=context_instruction
            )
            
            return result.strip()
            
        except Exception as e:
            logger.error(f"Error in rewrite_text: {e}")
            raise
    
    def analyze_text(self, text: str, analysis_type: str = "general", context: str = None) -> str:
        """Analyze text"""
        try:
            chain = self.create_analysis_chain()
            
            context_instruction = f"Additional Context: {context}" if context else ""
            
            result = chain.run(
                text=text,
                analysis_type=analysis_type,
                context_instruction=context_instruction
            )
            
            return result.strip()
            
        except Exception as e:
            logger.error(f"Error in analyze_text: {e}")
            raise
    
    def answer_query(self, query: str, context: str) -> str:
        """Answer query based on context"""
        try:
            chain = self.create_query_chain()
            result = chain.run(query=query, context=context)
            return result.strip()
            
        except Exception as e:
            logger.error(f"Error in answer_query: {e}")
            raise
    
    def summarize(self, text: str, summary_type: str = "brief") -> str:
        """Summarize text"""
        try:
            chain = self.create_summary_chain()
            
            additional_instructions = ""
            if summary_type == "brief":
                additional_instructions = "Batasi dalam 3 kalimat."
            elif summary_type == "detailed":
                additional_instructions = "Berikan ringkasan komprehensif dengan semua poin kunci."
            
            result = chain.run(
                text=text,
                summary_type=summary_type,
                additional_instructions=additional_instructions
            )
            
            return result.strip()
            
        except Exception as e:
            logger.error(f"Error in summarize: {e}")
            raise


# Global instance
word_chains = WordChains()