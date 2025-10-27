from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from typing import Dict, Any, List
from app.core.langchain_setup import LLMFactory
from loguru import logger
import json


class ExcelChains:
    """LangChain chains untuk Excel data analysis"""
    
    def __init__(self, llm=None):
        self.llm = llm or LLMFactory.create_llm()
    
    def create_formula_chain(self) -> LLMChain:
        """Create chain untuk formula generation"""
        template = """Anda adalah ahli formula Excel. Buatlah formula Excel berdasarkan deskripsi dan struktur data.

Struktur Data:
{data_structure}

Permintaan Pengguna:
{description}

{context_instruction}

Buatlah:
1. Formula Excel
2. Penjelasan cara kerjanya
3. Contoh hasil yang diharapkan
4. Formula alternatif (jika ada)

Format respons Anda sebagai:
FORMULA: [formula]
EXPLANATION: [penjelasan]
EXAMPLE: [contoh hasil]
ALTERNATIVES: [daftar formula alternatif]

Respons:"""
        
        prompt = PromptTemplate(
            input_variables=["data_structure", "description", "context_instruction"],
            template=template
        )
        
        return LLMChain(llm=self.llm, prompt=prompt)
    
    def create_query_chain(self) -> LLMChain:
        """Create chain untuk natural language data queries"""
        template = """Anda adalah asisten analisis data. Jawab pertanyaan berdasarkan ringkasan data yang diberikan.

Ringkasan Data:
{data_summary}

Statistik Data:
{statistics}

Pertanyaan:
{query}

{context_instruction}

Berikan jawaban yang jelas dan berdasarkan data yang:
1. Menjawab pertanyaan secara langsung
2. Mereferensikan poin data spesifik
3. Menyertakan kalkulasi atau wawasan yang relevan
4. Menyarankan visualisasi jika sesuai

Jawaban:"""
        
        prompt = PromptTemplate(
            input_variables=["data_summary", "statistics", "query", "context_instruction"],
            template=template
        )
        
        return LLMChain(llm=self.llm, prompt=prompt)
    
    def create_insight_chain(self) -> LLMChain:
        """Create chain untuk data insights"""
        template = """Anda adalah analis data. Berikan wawasan tentang dataset.

Ringkasan Data:
{data_summary}

Statistik:
{statistics}

Korelasi:
{correlations}

Jenis Wawasan: {insight_type}

{context_instruction}

Berikan wawasan yang mencakup:
1. Pola dan tren kunci
2. Hubungan atau korelasi yang menonjol
3. Anomali atau outlier
4. Rekomendasi yang dapat ditindaklanjuti

Wawasan:"""
        
        prompt = PromptTemplate(
            input_variables=["data_summary", "statistics", "correlations", "insight_type", "context_instruction"],
            template=template
        )
        
        return LLMChain(llm=self.llm, prompt=prompt)
    
    def create_chart_advisor_chain(self) -> LLMChain:
        """Create chain untuk chart recommendations"""
        template = """Anda adalah ahli visualisasi data. Rekomendasikan jenis grafik terbaik untuk data.

Struktur Data:
{data_structure}

Ringkasan Data:
{data_summary}

Tujuan: {purpose}

{context_instruction}

Analisis data dan rekomendasikan:
1. Jenis grafik terbaik dan alasannya
2. Konfigurasi sumbu dan data series
3. Opsi grafik alternatif
4. Best practices visualisasi untuk data ini

Format respons Anda sebagai:
RECOMMENDED: [jenis grafik]
REASON: [mengapa grafik ini terbaik]
CONFIGURATION: [cara mengaturnya]
ALTERNATIVES: [opsi lain]
TIPS: [tips visualisasi]

Respons:"""
        
        prompt = PromptTemplate(
            input_variables=["data_structure", "data_summary", "purpose", "context_instruction"],
            template=template
        )
        
        return LLMChain(llm=self.llm, prompt=prompt)
    
    def create_data_quality_chain(self) -> LLMChain:
        """Create chain untuk data quality assessment"""
        template = """Anda adalah ahli kualitas data. Nilai kualitas dataset ini.

Ringkasan Data:
{data_summary}

Nilai yang Hilang:
{missing_values}

Tipe Data:
{data_types}

Berikan penilaian yang mencakup:
1. Skor kualitas data keseluruhan (1-10)
2. Masalah yang ditemukan (nilai hilang, inkonsistensi, dll.)
3. Dampak dari masalah kualitas
4. Rekomendasi untuk perbaikan

Penilaian:"""
        
        prompt = PromptTemplate(
            input_variables=["data_summary", "missing_values", "data_types"],
            template=template
        )
        
        return LLMChain(llm=self.llm, prompt=prompt)
    
    def create_prediction_chain(self) -> LLMChain:
        """Create chain untuk simple predictions/trends"""
        template = """Anda adalah analis data. Berdasarkan data yang diberikan, buat prediksi atau identifikasi tren.

Ringkasan Data:
{data_summary}

Data Time Series (jika ada):
{time_series_data}

Statistik:
{statistics}

Analisis data dan berikan:
1. Tren yang teridentifikasi
2. Prediksi atau perkiraan (jika ada)
3. Tingkat kepercayaan dalam prediksi
4. Faktor yang mempengaruhi tren
5. Rekomendasi

Analisis:"""
        
        prompt = PromptTemplate(
            input_variables=["data_summary", "time_series_data", "statistics"],
            template=template
        )
        
        return LLMChain(llm=self.llm, prompt=prompt)
    
    def create_comparison_chain(self) -> LLMChain:
        """Create chain untuk comparing datasets"""
        template = """Bandingkan kedua dataset berikut.

Ringkasan Dataset 1:
{dataset1_summary}

Ringkasan Dataset 2:
{dataset2_summary}

Jenis Perbandingan: {comparison_type}

Berikan perbandingan yang mencakup:
1. Perbedaan kunci
2. Kesamaan
3. Perbandingan statistik
4. Wawasan dari perbandingan

Perbandingan:"""
        
        prompt = PromptTemplate(
            input_variables=["dataset1_summary", "dataset2_summary", "comparison_type"],
            template=template
        )
        
        return LLMChain(llm=self.llm, prompt=prompt)
    
    # Convenience methods
    
    def generate_formula(
        self,
        description: str,
        data_structure: Dict,
        context: str = None
    ) -> Dict[str, str]:
        """Generate Excel formula"""
        try:
            chain = self.create_formula_chain()
            
            data_structure_str = json.dumps(data_structure, indent=2)
            context_instruction = f"Additional Context: {context}" if context else ""
            
            result = chain.run(
                data_structure=data_structure_str,
                description=description,
                context_instruction=context_instruction
            )
            
            # Parse result
            parsed = {}
            for line in result.split('\n'):
                if line.startswith('FORMULA:'):
                    parsed['formula'] = line.replace('FORMULA:', '').strip()
                elif line.startswith('EXPLANATION:'):
                    parsed['explanation'] = line.replace('EXPLANATION:', '').strip()
                elif line.startswith('EXAMPLE:'):
                    parsed['example'] = line.replace('EXAMPLE:', '').strip()
                elif line.startswith('ALTERNATIVES:'):
                    parsed['alternatives'] = line.replace('ALTERNATIVES:', '').strip()
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error generating formula: {e}")
            raise
    
    def query_data(
        self,
        query: str,
        data_summary: str,
        statistics: Dict,
        context: str = None
    ) -> str:
        """Query data with natural language"""
        try:
            chain = self.create_query_chain()
            
            statistics_str = json.dumps(statistics, indent=2)
            context_instruction = f"Additional Context: {context}" if context else ""
            
            result = chain.run(
                data_summary=data_summary,
                statistics=statistics_str,
                query=query,
                context_instruction=context_instruction
            )
            
            return result.strip()
            
        except Exception as e:
            logger.error(f"Error querying data: {e}")
            raise
    
    def get_insights(
        self,
        data_summary: str,
        statistics: Dict,
        correlations: Dict,
        insight_type: str = "summary",
        context: str = None
    ) -> str:
        """Get data insights"""
        try:
            chain = self.create_insight_chain()
            
            statistics_str = json.dumps(statistics, indent=2)
            correlations_str = json.dumps(correlations, indent=2)
            context_instruction = f"Additional Context: {context}" if context else ""
            
            result = chain.run(
                data_summary=data_summary,
                statistics=statistics_str,
                correlations=correlations_str,
                insight_type=insight_type,
                context_instruction=context_instruction
            )
            
            return result.strip()
            
        except Exception as e:
            logger.error(f"Error getting insights: {e}")
            raise
    
    def recommend_chart(
        self,
        data_structure: Dict,
        data_summary: str,
        purpose: str = "general analysis",
        context: str = None
    ) -> Dict[str, str]:
        """Recommend chart type"""
        try:
            chain = self.create_chart_advisor_chain()
            
            data_structure_str = json.dumps(data_structure, indent=2)
            context_instruction = f"Additional Context: {context}" if context else ""
            
            result = chain.run(
                data_structure=data_structure_str,
                data_summary=data_summary,
                purpose=purpose,
                context_instruction=context_instruction
            )
            
            # Parse result
            parsed = {}
            for line in result.split('\n'):
                if line.startswith('RECOMMENDED:'):
                    parsed['recommended'] = line.replace('RECOMMENDED:', '').strip()
                elif line.startswith('REASON:'):
                    parsed['reason'] = line.replace('REASON:', '').strip()
                elif line.startswith('CONFIGURATION:'):
                    parsed['configuration'] = line.replace('CONFIGURATION:', '').strip()
                elif line.startswith('ALTERNATIVES:'):
                    parsed['alternatives'] = line.replace('ALTERNATIVES:', '').strip()
                elif line.startswith('TIPS:'):
                    parsed['tips'] = line.replace('TIPS:', '').strip()
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error recommending chart: {e}")
            raise


# Global instance
excel_chains = ExcelChains()