"""
LLM operations for Word documents
Rewrite, analyze, summarize, grammar check, and generate content
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional, Dict, Any, List
import logging

from app.models.query import (
    RewriteRequest, 
    AnalyzeRequest,
    SummarizeRequest,
    GenerateRequest
)
from app.core.summarizer import text_summarizer
from app.core.chroma_engine import chroma_engine
from app.core.cache_manager import cache_manager
from app.services.llm_service import llm_service
from app.chains.comparison_chains import comparison_chains

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/rewrite")
async def rewrite_text(request: RewriteRequest):
    """
    Rewrite text with specific instructions and style
    
    Args:
        text: Text to rewrite
        instruction: Rewriting instruction (e.g., "make it more formal")
        style: Writing style (formal, casual, academic, persuasive)
        context: Optional context from document
        use_context: Whether to use document context from RAG
    """
    try:
        # Build context if needed
        full_context = ""
        if request.use_context and request.context:
            # Search for relevant context
            results = await chroma_engine.query_similar(
                query_text=request.text,
                n_results=3
            )
            full_context = "\n\n".join(results["documents"])
        elif request.context:
            full_context = request.context
        
        # Build prompt
        style_instructions = {
            "formal": "Gunakan bahasa formal, hindari kontraksi, pertahankan tone profesional.",
            "casual": "Gunakan bahasa santai dan percakapan. Bersikaplah ramah dan mudah didekati.",
            "academic": "Gunakan bahasa akademis. Jadilah tepat dan objektif.",
            "persuasive": "Gunakan bahasa persuasif untuk meyakinkan pembaca. Sertakan argumen kuat.",
            "concise": "Jadilah ringkas dan to the point. Hapus kata-kata yang tidak perlu."
        }

        style_guide = style_instructions.get(request.style, "")

        prompt = f"""Tulis ulang teks berikut sesuai dengan instruksi ini:

Instruksi: {request.instruction}
Gaya: {request.style} - {style_guide}

{f"Konteks dari dokumen:\n{full_context}\n" if full_context else ""}

Teks Asli:
{request.text}

Teks yang Ditulis Ulang:"""
        
        # Generate rewrite
        rewritten = await llm_service.generate_text(prompt)
        
        # Calculate changes
        changes = []
        if request.text != rewritten:
            word_diff = len(rewritten.split()) - len(request.text.split())
            changes.append({
                "type": "length",
                "description": f"Word count changed by {word_diff} words",
                "original_length": len(request.text.split()),
                "new_length": len(rewritten.split())
            })
            
            if request.style:
                changes.append({
                    "type": "style",
                    "description": f"Style changed to {request.style}"
                })
        
        return {
            "success": True,
            "original": request.text,
            "rewritten": rewritten,
            "changes": changes,
            "metadata": {
                "instruction": request.instruction,
                "style": request.style,
                "used_context": bool(full_context)
            }
        }
        
    except Exception as e:
        logger.error(f"Error in rewrite: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_text(request: AnalyzeRequest):
    """
    Analyze text for style, tone, readability, and quality

    Args:
        text: Text to analyze
        analysis_type: Type of analysis (general, style, grammar, readability, sentiment)
        include_suggestions: Include improvement suggestions
    """
    try:
        # Clean text to prevent JSON parsing issues
        import json
        clean_text = request.text.strip()

        # Basic metrics
        words = clean_text.split()
        sentences = [s.strip() for s in clean_text.split('.') if s.strip()]

        metrics = {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_words_per_sentence": len(words) / max(len(sentences), 1),
            "character_count": len(clean_text),
            "paragraph_count": len([p for p in clean_text.split('\n\n') if p.strip()])
        }

        # Perform analysis based on type
        if request.analysis_type == "style":
            analysis = await text_summarizer.analyze_writing_style(clean_text)
            
        elif request.analysis_type == "readability":
            prompt = f"""Analisis keterbacaan teks ini:

{clean_text}

Berikan dalam format JSON dengan struktur berikut:
{{
  "reading_level": "pemula|menengah|lanjutan",
  "readability_score": 0-100,
  "vocabulary_complexity": "penjelasan kompleksitas kosa kata",
  "sentence_structure": "analisis struktur kalimat",
  "suggestions": ["saran 1", "saran 2", "saran 3"]
}}

Pastikan menggunakan key "suggestions" (bukan "saran_perbaikan") untuk array saran perbaikan."""

            analysis = await llm_service.generate_json(prompt)

        elif request.analysis_type == "sentiment":
            prompt = f"""Analisis sentimen dan tone dari teks ini:

{clean_text}

Berikan dalam format JSON dengan struktur berikut:
{{
  "overall_sentiment": "positif|negatif|netral",
  "sentiment_score": -1 hingga 1,
  "emotional_tone": "penjelasan tone emosional",
  "key_emotions": ["emosi 1", "emosi 2"],
  "suggestions": ["saran 1", "saran 2"]
}}

Gunakan key dalam bahasa Inggris dengan underscore."""

            analysis = await llm_service.generate_json(prompt)

        elif request.analysis_type == "grammar":
            prompt = f"""Periksa tata bahasa dan penggunaan bahasa dalam teks ini:

{clean_text}

Berikan dalam format JSON dengan struktur berikut:
{{
  "errors": [
    {{"type": "grammar|punctuation|word_choice", "text": "teks error", "correction": "koreksi"}}
  ],
  "suggestions": ["saran perbaikan 1", "saran perbaikan 2"],
  "score": 0-100,
  "summary": "ringkasan hasil pengecekan"
}}

Pastikan menggunakan key yang konsisten dalam bahasa Inggris."""

            analysis = await llm_service.generate_json(prompt)

        else:  # general
            prompt = f"""Berikan analisis komprehensif dari teks ini:

{clean_text}

Berikan dalam format JSON dengan struktur berikut:
{{
  "overall_assessment": "penilaian keseluruhan",
  "strengths": ["kekuatan 1", "kekuatan 2"],
  "weaknesses": ["kelemahan 1", "kelemahan 2"],
  "key_themes": ["tema 1", "tema 2"],
  "suggestions": ["saran perbaikan 1", "saran perbaikan 2"]
}}

Gunakan key dalam bahasa Inggris dengan underscore."""

            analysis = await llm_service.generate_json(prompt)
        
        # Extract suggestions - handle multiple possible keys
        suggestions = []
        if request.include_suggestions:
            if isinstance(analysis, dict):
                # Try multiple possible key names for suggestions
                suggestions = (
                    analysis.get("suggestions") or
                    analysis.get("saran_perbaikan") or
                    analysis.get("improvements") or
                    analysis.get("saran") or
                    []
                )
                # Ensure it's a list
                if not isinstance(suggestions, list):
                    suggestions = []

                # Move suggestions to top-level if found in nested keys
                # and remove from analysis to avoid duplication
                if analysis.get("saran_perbaikan"):
                    del analysis["saran_perbaikan"]
                if analysis.get("saran"):
                    del analysis["saran"]

        # Normalize analysis keys to English with underscore
        if isinstance(analysis, dict):
            # Create a mapping of Indonesian to English keys
            key_mapping = {
                "level_pembaca": "reading_level",
                "skor_keterbacaan": "readability_score",
                "kompleksitas_kosakata": "vocabulary_complexity",
                "analisis_struktur_kalimat": "sentence_structure",
                "sentimen_keseluruhan": "overall_sentiment",
                "skor_sentimen": "sentiment_score",
                "tone_emosional": "emotional_tone",
                "emosi_kunci": "key_emotions",
                "kesalahan": "errors",
                "ringkasan": "summary",
                "penilaian_keseluruhan": "overall_assessment",
                "kekuatan": "strengths",
                "kelemahan": "weaknesses",
                "tema_kunci": "key_themes",
            }

            # Normalize keys
            normalized_analysis = {}
            for key, value in analysis.items():
                # Use mapped key if available, otherwise keep original
                new_key = key_mapping.get(key, key)
                normalized_analysis[new_key] = value

            analysis = normalized_analysis

        # Ensure analysis is JSON serializable
        if isinstance(analysis, str):
            try:
                analysis = json.loads(analysis)
            except:
                analysis = {"result": analysis}

        # Sanitize the entire response to remove control characters
        import re

        def sanitize_value(obj):
            """Recursively sanitize values"""
            if isinstance(obj, dict):
                return {k: sanitize_value(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [sanitize_value(item) for item in obj]
            elif isinstance(obj, str):
                # Remove control characters except \n, \r, \t
                return re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', obj)
            else:
                return obj

        response_data = {
            "success": True,
            "analysis": sanitize_value(analysis),
            "metrics": metrics,
            "suggestions": sanitize_value(suggestions[:10]),  # Limit to 10
            "metadata": {
                "analysis_type": request.analysis_type,
                "text_length": len(clean_text)
            }
        }

        return response_data

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in analyze: {str(e)}")
        logger.error(f"Analysis result that caused error: {analysis if 'analysis' in locals() else 'N/A'}")
        raise HTTPException(status_code=422, detail=f"Invalid JSON in response: {str(e)}")
    except Exception as e:
        logger.error(f"Error in analyze: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize")
async def summarize_text(request: SummarizeRequest):
    """
    Summarize text content
    
    Args:
        text: Text to summarize
        summary_type: Type of summary (concise, detailed, bullets)
        max_length: Maximum length of summary in words
        document_id: Optional document ID for context
    """
    try:
        # Check cache first if document_id provided
        cache_key = None
        if request.document_id:
            cache_key = f"summary_{request.document_id}_{request.summary_type}"
            cached = cache_manager.get(cache_key)
            if cached:
                logger.info(f"Cache hit for summary: {cache_key}")
                return cached
        
        # Generate summary
        summary = await text_summarizer.summarize_text(
            text=request.text,
            summary_type=request.summary_type
        )
        
        # Truncate if needed
        if request.max_length:
            words = summary.split()
            if len(words) > request.max_length:
                summary = " ".join(words[:request.max_length]) + "..."
        
        # Extract key points
        key_points = await text_summarizer.extract_key_points(
            request.text,
            num_points=5
        )
        
        response = {
            "success": True,
            "summary": summary,
            "key_points": key_points,
            "metadata": {
                "original_length": len(request.text.split()),
                "summary_length": len(summary.split()),
                "compression_ratio": len(summary) / len(request.text),
                "summary_type": request.summary_type
            }
        }
        
        # Cache result
        if cache_key:
            cache_manager.set(cache_key, response, ttl=3600)
        
        return response
        
    except Exception as e:
        logger.error(f"Error in summarize: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate_content(request: GenerateRequest):
    """
    Generate new content based on prompt and context
    
    Args:
        prompt: Generation prompt
        context: Optional context
        style: Writing style
        length: Desired length (short, medium, long)
        document_id: Optional document ID for context
    """
    try:
        # Get context from document if provided
        full_context = request.context or ""
        
        if request.document_id:
            results = await chroma_engine.query_similar(
                query_text=request.prompt,
                n_results=3,
                filter_metadata={"document_id": request.document_id}
            )
            doc_context = "\n\n".join(results["documents"])
            full_context = f"{full_context}\n\n{doc_context}" if full_context else doc_context
        
        # Length guidelines
        length_guide = {
            "short": "Tulis 1-2 paragraf (100-150 kata).",
            "medium": "Tulis 3-5 paragraf (250-400 kata).",
            "long": "Tulis 6+ paragraf (500+ kata)."
        }

        # Build generation prompt
        generation_prompt = f"""Buatlah konten berdasarkan hal berikut:

Prompt: {request.prompt}

Persyaratan:
- Gaya: {request.style}
- Panjang: {length_guide.get(request.length, length_guide['medium'])}

{f"Konteks yang perlu dipertimbangkan:\n{full_context}\n" if full_context else ""}

Konten yang Dihasilkan:"""
        
        # Generate
        content = await llm_service.generate_text(generation_prompt)
        
        return {
            "success": True,
            "content": content,
            "metadata": {
                "prompt": request.prompt,
                "style": request.style,
                "length": request.length,
                "word_count": len(content.split()),
                "used_context": bool(full_context)
            }
        }
        
    except Exception as e:
        logger.error(f"Error in generate: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/grammar-check")
async def check_grammar(text: str):
    """
    Check grammar and suggest corrections
    
    Args:
        text: Text to check
    """
    try:
        prompt = f"""Periksa teks ini untuk masalah tata bahasa, ejaan, dan gaya:

{text}

Berikan:
1. Masalah yang ditemukan (dengan lokasi dan jenis)
2. Koreksi yang disarankan
3. Skor tata bahasa keseluruhan (0-100)
4. Penjelasan masalah utama

Kembalikan dalam format JSON dengan keys: issues (array), corrections (array), score (number), summary (string)"""
        
        result = await llm_service.generate_json(prompt)
        
        return {
            "success": True,
            "result": result,
            "metadata": {
                "text_length": len(text),
                "word_count": len(text.split())
            }
        }
        
    except Exception as e:
        logger.error(f"Error in grammar check: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paraphrase")
async def paraphrase_text(
    text: str,
    num_variations: int = 3
):
    """
    Generate paraphrased variations of text
    
    Args:
        text: Text to paraphrase
        num_variations: Number of variations to generate
    """
    try:
        prompt = f"""Buatlah {num_variations} versi parafrase yang berbeda dari teks ini.
Pertahankan makna yang sama tetapi gunakan kata dan struktur kalimat yang berbeda.

Asli:
{text}

Versi parafrase (sebagai array JSON):"""
        
        variations = await llm_service.generate_json(prompt)
        
        return {
            "success": True,
            "original": text,
            "variations": variations if isinstance(variations, list) else [variations],
            "metadata": {
                "num_variations": num_variations,
                "original_length": len(text.split())
            }
        }
        
    except Exception as e:
        logger.error(f"Error in paraphrase: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_documents(
    document_id_1: str,
    document_id_2: str,
    comparison_type: str = "content"
):
    """
    Compare two documents
    
    Args:
        document_id_1: First document ID
        document_id_2: Second document ID
        comparison_type: Type of comparison (content, style, structure)
    """
    try:
        # Get documents
        doc1_results = await chroma_engine.query_similar(
            query_text="",
            n_results=10,
            filter_metadata={"document_id": document_id_1}
        )
        
        doc2_results = await chroma_engine.query_similar(
            query_text="",
            n_results=10,
            filter_metadata={"document_id": document_id_2}
        )
        
        if not doc1_results["documents"] or not doc2_results["documents"]:
            raise HTTPException(status_code=404, detail="One or both documents not found")
        
        # Combine chunks
        doc1_content = "\n\n".join(doc1_results["documents"][:5])
        doc2_content = "\n\n".join(doc2_results["documents"][:5])
        
        # Use comparison chain
        result = await comparison_chains.compare_word_documents(
            doc1_content=doc1_content,
            doc2_content=doc2_content,
            doc1_name=document_id_1,
            doc2_name=document_id_2
        )
        
        return {
            "success": True,
            "comparison": result,
            "metadata": {
                "document_id_1": document_id_1,
                "document_id_2": document_id_2,
                "comparison_type": comparison_type
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in compare: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-outline")
async def extract_outline(text: str):
    """
    Extract hierarchical outline from text
    
    Args:
        text: Text to extract outline from
    """
    try:
        outline = await text_summarizer.generate_outline(text)
        
        return {
            "success": True,
            "outline": outline,
            "metadata": {
                "text_length": len(text.split())
            }
        }
        
    except Exception as e:
        logger.error(f"Error extracting outline: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))