"""
LangChain chains for document and data comparison
"""
from langchain_core.prompts import PromptTemplate
from typing import Dict, Any, List
import logging

from app.services.llm_service import llm_service
from app.utils.output_parsers import comparison_parser

logger = logging.getLogger(__name__)


class ComparisonChains:
    """Chains for comparing documents and datasets"""
    
    def __init__(self):
        self.llm = llm_service.llm
    
    async def compare_word_documents(
        self,
        doc1_content: str,
        doc2_content: str,
        doc1_name: str = "Document 1",
        doc2_name: str = "Document 2"
    ) -> Dict[str, Any]:
        """
        Compare two Word documents
        
        Args:
            doc1_content: Content of first document
            doc2_content: Content of second document
            doc1_name: Name of first document
            doc2_name: Name of second document
            
        Returns:
            Comparison analysis
        """
        try:
            prompt_template = """Bandingkan kedua dokumen berikut dan berikan analisis terperinci.

Dokumen 1 ({doc1_name}):
{doc1_content}

Dokumen 2 ({doc2_name}):
{doc2_content}

Berikan:
1. Skor kemiripan (0-100)
2. Perbedaan kunci dalam konten
3. Kesamaan kunci
4. Ringkasan keseluruhan perbandingan

{format_instructions}
"""
            
            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["doc1_name", "doc2_name", "doc1_content", "doc2_content"],
                partial_variables={
                    "format_instructions": comparison_parser.get_format_instructions()
                }
            )
            
            chain = prompt | self.llm | comparison_parser
            
            result = await chain.ainvoke({
                "doc1_name": doc1_name,
                "doc2_name": doc2_name,
                "doc1_content": doc1_content[:5000],  # Limit length
                "doc2_content": doc2_content[:5000]
            })
            
            return result.dict()
            
        except Exception as e:
            logger.error(f"Error comparing documents: {str(e)}")
            raise
    
    async def compare_excel_datasets(
        self,
        dataset1: Dict[str, Any],
        dataset2: Dict[str, Any],
        dataset1_name: str = "Dataset 1",
        dataset2_name: str = "Dataset 2"
    ) -> Dict[str, Any]:
        """
        Compare two Excel datasets
        
        Args:
            dataset1: Analysis of first dataset
            dataset2: Analysis of second dataset
            dataset1_name: Name of first dataset
            dataset2_name: Name of second dataset
            
        Returns:
            Comparison results
        """
        try:
            # Create summaries
            summary1 = self._create_dataset_summary(dataset1, dataset1_name)
            summary2 = self._create_dataset_summary(dataset2, dataset2_name)
            
            prompt = f"""Bandingkan kedua dataset Excel berikut:

{summary1}

{summary2}

Berikan:
1. Perbedaan struktural (baris, kolom, tipe data)
2. Perbandingan kualitas data
3. Kolom umum dan karakteristiknya
4. Rekomendasi untuk penggabungan atau analisis bersama

Kembalikan dalam format JSON dengan keys: structural_differences, quality_comparison, common_columns, recommendations"""
            
            response = await llm_service.generate_json(prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"Error comparing datasets: {str(e)}")
            raise
    
    def _create_dataset_summary(
        self,
        dataset_analysis: Dict[str, Any],
        name: str
    ) -> str:
        """Create a text summary of dataset analysis"""
        summary = f"{name}:\n"
        summary += f"- Shape: {dataset_analysis['shape']['rows']} rows × {dataset_analysis['shape']['columns']} columns\n"
        summary += f"- Data Quality: {dataset_analysis['data_quality']['completeness_score']:.1f}%\n"
        summary += f"- Columns:\n"
        
        for col in dataset_analysis['columns'][:10]:
            summary += f"  • {col['name']} ({col['dtype']}): {col['non_null_count']} values\n"
        
        return summary
    
    async def find_document_versions(
        self,
        documents: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Identify different versions of the same document
        
        Args:
            documents: List of documents with 'name' and 'content'
            
        Returns:
            Version analysis
        """
        try:
            if len(documents) < 2:
                return {"versions": [], "message": "Need at least 2 documents"}
            
            # Create document summaries
            doc_summaries = []
            for i, doc in enumerate(documents):
                doc_summaries.append(
                    f"Document {i+1} ({doc['name']}):\n{doc['content'][:500]}..."
                )
            
            all_docs = "\n\n".join(doc_summaries)
            
            prompt = f"""Analisis dokumen-dokumen ini dan identifikasi apakah ada yang merupakan versi dari dokumen yang sama:

{all_docs}

Berikan:
1. Kelompok dokumen yang merupakan versi satu sama lain
2. Untuk setiap kelompok, identifikasi urutan yang mungkin (mana yang terlama/terbaru)
3. Perubahan besar antara versi

Kembalikan dalam format JSON."""
            
            response = await llm_service.generate_json(prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"Error finding versions: {str(e)}")
            raise
    
    async def merge_document_suggestions(
        self,
        doc1_content: str,
        doc2_content: str
    ) -> Dict[str, Any]:
        """
        Suggest how to merge two documents
        
        Args:
            doc1_content: First document content
            doc2_content: Second document content
            
        Returns:
            Merge suggestions
        """
        try:
            prompt = f"""Diberikan kedua dokumen ini, sarankan cara terbaik untuk menggabungkannya:

Dokumen 1:
{doc1_content[:2000]}

Dokumen 2:
{doc2_content[:2000]}

Berikan:
1. Strategi penggabungan (append, interleave, cherry-pick)
2. Bagian yang harus dipertahankan dari setiap dokumen
3. Konflik potensial
4. Struktur akhir yang disarankan

Kembalikan dalam format JSON."""
            
            response = await llm_service.generate_json(prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating merge suggestions: {str(e)}")
            raise
    
    async def compare_formula_approaches(
        self,
        formula1: str,
        formula2: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Compare two Excel formulas
        
        Args:
            formula1: First formula
            formula2: Second formula
            context: Description of what the formula should do
            
        Returns:
            Comparison of formulas
        """
        try:
            prompt = f"""Bandingkan kedua formula Excel berikut:

Konteks: {context}

Formula 1: {formula1}
Formula 2: {formula2}

Analisis:
1. Apakah keduanya menghasilkan hasil yang sama?
2. Mana yang lebih efisien?
3. Mana yang lebih mudah dibaca?
4. Kelebihan dan kekurangan masing-masing
5. Rekomendasi Anda

Kembalikan dalam format JSON."""
            
            response = await llm_service.generate_json(prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"Error comparing formulas: {str(e)}")
            raise


# Global instance
comparison_chains = ComparisonChains()