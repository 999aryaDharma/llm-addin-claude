#!/usr/bin/env python3
"""
Office LLM Add-in API Test Script
Complete test suite for all endpoints - Updated v2.5.0
"""
import requests
import json
import time
from pathlib import Path
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8000"
TEST_FILE = "test_document.txt"
TEST_EXCEL_FILE = "test_data.xlsx"


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_section(title):
    """Print section header"""
    print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}  {title}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}\n")


def print_success(msg):
    print(f"{Colors.OKGREEN}✓{Colors.ENDC} {msg}")


def print_error(msg):
    print(f"{Colors.FAIL}✗{Colors.ENDC} {msg}")


def print_info(msg):
    print(f"{Colors.OKCYAN}ℹ{Colors.ENDC} {msg}")


# ============================================================================
# WORD DOCUMENT TESTS
# ============================================================================

def test_health():
    """Test health check"""
    print_section("1. Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(json.dumps(result, indent=2))

        if response.status_code == 200:
            print_success("Health check passed")
            return True
        else:
            print_error("Health check failed")
            return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False


def test_upload_document():
    """Test document upload"""
    print_section("2. Upload Word Document")

    # Create test file if not exists
    if not Path(TEST_FILE).exists():
        print_info(f"Creating test file: {TEST_FILE}")
        with open(TEST_FILE, 'w', encoding='utf-8') as f:
            f.write("""Test Document untuk Office LLM Add-in

Ini adalah dokumen test untuk menguji kemampuan pemrosesan dokumen.
Dokumen ini berisi teks contoh untuk pengujian.

Temuan Utama:
Pemrosesan dokumen berbasis AI dapat meningkatkan produktivitas secara signifikan
dengan mengotomatisasi tugas-tugas rutin dan memberikan wawasan yang berguna.

Rekomendasi:
1. Implementasikan ringkasan otomatis untuk dokumen panjang
2. Gunakan pencarian semantik untuk pencarian informasi yang cepat
3. Manfaatkan AI untuk pembuatan konten dan editing
4. Integrasikan dengan sistem manajemen dokumen yang ada
5. Latih model dengan data spesifik domain untuk hasil yang lebih baik

Kesimpulan:
Teknologi AI dalam pemrosesan dokumen memberikan nilai tambah yang signifikan
untuk organisasi modern yang menangani volume dokumen yang besar.
""")

    try:
        with open(TEST_FILE, 'rb') as f:
            files = {'file': (TEST_FILE, f, 'text/plain')}
            response = requests.post(f"{BASE_URL}/api/documents/upload", files=files)

        print(f"Status: {response.status_code}")
        result = response.json()
        print(json.dumps(result, indent=2))

        if response.status_code == 200:
            print_success(f"Document uploaded: {result.get('document_id')}")
            return result.get('document_id')
        else:
            print_error("Document upload failed")
            return None
    except Exception as e:
        print_error(f"Upload error: {str(e)}")
        return None


def test_search_documents(query="temuan utama"):
    """Test semantic search"""
    print_section("3. Search Documents (Semantic)")

    # Wait for processing
    print_info("Waiting 5 seconds for document indexing...")
    time.sleep(5)

    data = {
        "query": query,
        "limit": 3,
        "include_metadata": True
    }

    try:
        response = requests.post(f"{BASE_URL}/api/documents/search", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Query: {query}")
        print(f"Results found: {len(result.get('results', []))}")
        print(json.dumps(result, indent=2))

        if response.status_code == 200:
            print_success(f"Search completed: {len(result.get('results', []))} results")
            return True
        else:
            print_error("Search failed")
            return False
    except Exception as e:
        print_error(f"Search error: {str(e)}")
        return False


def test_query_rag(query="Apa rekomendasi utama dalam dokumen?"):
    """Test RAG query"""
    print_section("4. RAG Query (Question Answering)")

    data = {
        "query": query,
        "max_results": 3
    }

    try:
        response = requests.post(f"{BASE_URL}/api/query/search", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()

        print(f"Query: {result.get('query')}")
        print(f"\nAnswer:\n{result.get('answer')}")
        print(f"\nSources: {len(result.get('sources', []))} documents")

        if response.status_code == 200:
            print_success("RAG query successful")
            return True
        else:
            print_error("RAG query failed")
            return False
    except Exception as e:
        print_error(f"RAG query error: {str(e)}")
        return False


def test_rewrite():
    """Test text rewriting"""
    print_section("5. Text Rewrite")

    data = {
        "text": "Hasil nya sangat bagus dan kita dapat banyak data yang bermanfaat.",
        "instruction": "Perbaiki tata bahasa dan buat lebih profesional",
        "style": "formal",
        "use_context": False
    }

    try:
        response = requests.post(f"{BASE_URL}/api/llm/rewrite", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()

        print(f"\nOriginal:\n{result.get('original')}")
        print(f"\nRewritten:\n{result.get('rewritten')}")
        print(f"\nChanges: {len(result.get('changes', []))}")

        if response.status_code == 200:
            print_success("Text rewrite successful")
            return True
        else:
            print_error("Text rewrite failed")
            return False
    except Exception as e:
        print_error(f"Rewrite error: {str(e)}")
        return False


def test_analyze():
    """Test text analysis"""
    print_section("6. Text Analysis")

    # Test dengan text yang mengandung newline
    test_text = """Ini adalah contoh teks untuk analisis.
Teks ini memiliki beberapa kalimat.
Beberapa kalimat pendek.
Yang lain lebih panjang dan kompleks dengan struktur yang lebih rumit."""

    data = {
        "text": test_text,
        "analysis_type": "readability",
        "include_suggestions": True
    }

    try:
        response = requests.post(f"{BASE_URL}/api/llm/analyze", json=data)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"\nAnalysis Type: {result.get('metadata', {}).get('analysis_type')}")
            print(f"Text Length: {result.get('metadata', {}).get('text_length')}")

            # Check analysis structure
            analysis = result.get('analysis', {})
            print(f"\nAnalysis Keys: {list(analysis.keys())}")

            # Verify consistent keys (should be in English)
            expected_keys = ["reading_level", "readability_score", "vocabulary_complexity", "sentence_structure"]
            found_keys = [k for k in expected_keys if k in analysis]
            print(f"Expected Keys Found: {found_keys}")

            print(f"\nMetrics:")
            print(json.dumps(result.get('metrics', {}), indent=2))

            # Check suggestions
            suggestions = result.get('suggestions', [])
            print(f"\nSuggestions Count: {len(suggestions)}")
            if suggestions:
                print("Suggestions:")
                for i, sugg in enumerate(suggestions[:3], 1):
                    print(f"  {i}. {sugg[:100]}...")  # Truncate long suggestions
            else:
                print_error("⚠️  No suggestions found - this should not happen when include_suggestions=True")

            # Verify no Indonesian keys in top-level analysis
            indonesian_keys = ["saran_perbaikan", "level_pembaca", "skor_keterbacaan"]
            found_indonesian = [k for k in indonesian_keys if k in analysis]
            if found_indonesian:
                print_error(f"⚠️  Found Indonesian keys in analysis: {found_indonesian}")
            else:
                print_success("✓ All keys are in English (consistent)")

            print_success("Text analysis successful")
            return True
        else:
            print_error(f"Text analysis failed: {response.text}")
            return False
    except Exception as e:
        print_error(f"Analysis error: {str(e)}")
        return False


def test_summarize():
    """Test summarization"""
    print_section("7. Text Summarization")

    data = {
        "text": """
        Kecerdasan buatan telah merevolusi banyak industri. Dalam bidang kesehatan,
        AI membantu mendiagnosis penyakit dengan lebih akurat dan cepat. Dalam keuangan,
        AI mendeteksi penipuan dan mengelola risiko dengan efektif. Dalam manufaktur,
        AI mengoptimalkan proses produksi dan mengurangi pemborosan. Dampak AI terus
        berkembang seiring kemajuan teknologi. Perusahaan yang mengadopsi AI lebih awal
        mendapatkan keunggulan kompetitif yang signifikan.
        """,
        "summary_type": "concise",
        "max_length": 50
    }

    try:
        response = requests.post(f"{BASE_URL}/api/llm/summarize", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()

        print(f"\nSummary:\n{result.get('summary')}")
        print(f"\nKey Points:")
        for i, point in enumerate(result.get('key_points', []), 1):
            print(f"  {i}. {point}")
        print(f"\nMetadata:")
        print(json.dumps(result.get('metadata', {}), indent=2))

        if response.status_code == 200:
            print_success("Summarization successful")
            return True
        else:
            print_error("Summarization failed")
            return False
    except Exception as e:
        print_error(f"Summarization error: {str(e)}")
        return False


def test_grammar_check():
    """Test grammar checking"""
    print_section("8. Grammar Check")

    params = {"text": "Dia tidak suka apel. Mereka pergi ke toko kemarin dan membeli banyak barang."}

    try:
        response = requests.post(f"{BASE_URL}/api/llm/grammar-check", params=params)
        print(f"Status: {response.status_code}")
        result = response.json()

        print(f"\nGrammar Check Result:")
        print(json.dumps(result.get('result'), indent=2))

        if response.status_code == 200:
            print_success("Grammar check successful")
            return True
        else:
            print_error("Grammar check failed")
            return False
    except Exception as e:
        print_error(f"Grammar check error: {str(e)}")
        return False


def test_paraphrase():
    """Test paraphrasing"""
    print_section("9. Paraphrase Text")

    params = {
        "text": "Teknologi AI sangat membantu dalam meningkatkan produktivitas perusahaan.",
        "num_variations": 3
    }

    try:
        response = requests.post(f"{BASE_URL}/api/llm/paraphrase", params=params)
        print(f"Status: {response.status_code}")
        result = response.json()

        print(f"\nOriginal: {result.get('original')}")
        print(f"\nVariations:")
        for i, var in enumerate(result.get('variations', []), 1):
            print(f"  {i}. {var}")

        if response.status_code == 200:
            print_success("Paraphrase successful")
            return True
        else:
            print_error("Paraphrase failed")
            return False
    except Exception as e:
        print_error(f"Paraphrase error: {str(e)}")
        return False


def test_generate():
    """Test content generation"""
    print_section("10. Generate Content")

    data = {
        "prompt": "Tulis paragraf tentang manfaat AI dalam bisnis modern",
        "style": "formal",
        "length": "medium"
    }

    try:
        response = requests.post(f"{BASE_URL}/api/llm/generate", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()

        print(f"\nGenerated Content:\n{result.get('content')}")
        print(f"\nMetadata:")
        print(json.dumps(result.get('metadata', {}), indent=2))

        if response.status_code == 200:
            print_success("Content generation successful")
            return True
        else:
            print_error("Content generation failed")
            return False
    except Exception as e:
        print_error(f"Content generation error: {str(e)}")
        return False


# ============================================================================
# EXCEL TESTS
# ============================================================================

def test_excel_formula():
    """Test Excel formula generation"""
    print_section("11. Excel Formula Generation")

    data = {
        "description": "Hitung rata-rata dari kolom B jika kolom A lebih besar dari 100"
    }

    try:
        response = requests.post(f"{BASE_URL}/api/excel/formula", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()

        print(f"\nFormula: {result.get('formula')}")
        print(f"\nExplanation:\n{result.get('explanation')}")
        print(f"\nExample: {result.get('example')}")

        if response.status_code == 200:
            print_success("Formula generation successful")
            return True
        else:
            print_error("Formula generation failed")
            return False
    except Exception as e:
        print_error(f"Formula generation error: {str(e)}")
        return False


def test_excel_query():
    """Test Excel data query"""
    print_section("12. Excel Data Query")

    # Sample data
    data = {
        "query": "Berapa total penjualan?",
        "range_data": {
            "range_address": "A1:B5",
            "sheet_name": "Sales",
            "data": [
                ["Produk", "Penjualan"],
                ["A", 100],
                ["B", 150],
                ["C", 200],
                ["D", 175]
            ],
            "headers": ["Produk", "Penjualan"]
        },
        "include_analysis": True
    }

    try:
        response = requests.post(f"{BASE_URL}/api/excel/query", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()

        print(f"\nAnswer: {result.get('answer')}")
        print(f"\nSQL Equivalent: {result.get('sql_equivalent')}")
        print(f"\nVisualization Suggestion: {result.get('visualization_suggestion')}")

        if response.status_code == 200:
            print_success("Excel query successful")
            return True
        else:
            print_error("Excel query failed")
            return False
    except Exception as e:
        print_error(f"Excel query error: {str(e)}")
        return False


def test_excel_analyze():
    """Test Excel comprehensive analysis"""
    print_section("13. Excel Comprehensive Analysis")

    data = {
        "context": {
            "sheet_name": "Data",
            "range_address": "A1:C10",
            "data": [
                ["Bulan", "Penjualan", "Biaya"],
                ["Jan", 1000, 600],
                ["Feb", 1200, 650],
                ["Mar", 1100, 620],
                ["Apr", 1300, 680],
                ["Mei", 1250, 670],
                ["Jun", 1400, 700],
                ["Jul", 1350, 690],
                ["Agu", 1500, 720],
                ["Sep", 1450, 710]
            ]
        },
        "include_correlations": True,
        "include_predictions": True
    }

    try:
        response = requests.post(f"{BASE_URL}/api/excel/llm/analyze-comprehensive", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()

        print(f"\nAnalysis:")
        print(json.dumps(result.get('data', {}).get('insights'), indent=2))

        if response.status_code == 200:
            print_success("Excel analysis successful")
            return True
        else:
            print_error("Excel analysis failed")
            return False
    except Exception as e:
        print_error(f"Excel analysis error: {str(e)}")
        return False


def test_excel_report():
    """Test Excel report generation"""
    print_section("14. Excel Report Generation")

    data = {
        "context": {
            "sheet_name": "Sales",
            "range_address": "A1:B5",
            "data": [
                ["Produk", "Penjualan"],
                ["A", 100],
                ["B", 150],
                ["C", 200],
                ["D", 175]
            ]
        },
        "report_type": "executive",
        "include_charts": True
    }

    try:
        response = requests.post(f"{BASE_URL}/api/excel/llm/generate-report", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()

        print(f"\nReport:\n{result.get('data', {}).get('report', '')[:500]}...")

        if response.status_code == 200:
            print_success("Report generation successful")
            return True
        else:
            print_error("Report generation failed")
            return False
    except Exception as e:
        print_error(f"Report generation error: {str(e)}")
        return False


def run_all_tests():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}  OFFICE LLM ADD-IN API TEST SUITE v2.5.0{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}")

    tests = [
        # Core
        ("Health Check", test_health),

        # Word Document Tests
        ("Upload Document", test_upload_document),
        ("Search Documents", lambda: test_search_documents()),
        ("RAG Query", lambda: test_query_rag()),
        ("Text Rewrite", test_rewrite),
        ("Text Analysis", test_analyze),
        ("Summarization", test_summarize),
        ("Grammar Check", test_grammar_check),
        ("Paraphrase", test_paraphrase),
        ("Generate Content", test_generate),

        # Excel Tests
        ("Excel Formula", test_excel_formula),
        ("Excel Query", test_excel_query),
        ("Excel Analysis", test_excel_analyze),
        ("Excel Report", test_excel_report),
    ]

    results = []

    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, "✅ PASS" if success else "❌ FAIL"))
        except Exception as e:
            print_error(f"ERROR: {str(e)}")
            results.append((name, f"❌ ERROR: {str(e)[:50]}"))

        # Small delay between tests
        time.sleep(0.5)

    # Print summary
    print_section("TEST SUMMARY")
    for name, result in results:
        status_color = Colors.OKGREEN if "PASS" in result else Colors.FAIL
        print(f"{name:<30} {status_color}{result}{Colors.ENDC}")

    passed = sum(1 for _, r in results if "PASS" in r)
    total = len(results)

    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.ENDC}")

    if passed == total:
        print(f"{Colors.OKGREEN}🎉 All tests passed!{Colors.ENDC}")
    elif passed > total / 2:
        print(f"{Colors.WARNING}⚠️  Some tests failed{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Many tests failed{Colors.ENDC}")


if __name__ == "__main__":
    print(f"\n{Colors.OKCYAN}Starting API tests...{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Base URL: {BASE_URL}{Colors.ENDC}\n")

    run_all_tests()

    print(f"\n{Colors.OKBLUE}Tests completed!{Colors.ENDC}\n")
