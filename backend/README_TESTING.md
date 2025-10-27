# 🧪 Testing Guide - Office LLM Add-in API

## Cara Menjalankan Test API

### 1. Persiapan

Pastikan backend server sudah berjalan:

```bash
# Dari direktori backend
cd D:\llm-addin(claude)\backend

# Aktifkan virtual environment (jika menggunakan)
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Jalankan server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server harus berjalan di `http://localhost:8000`

### 2. Install Dependencies Test (jika belum)

```bash
pip install requests
```

### 3. Jalankan Test

#### Opsi 1: Jalankan Semua Test
```bash
python test_api.py
```

#### Opsi 2: Jalankan Test Spesifik
Buka `test_api.py` dan panggil fungsi test tertentu:

```python
# Di akhir file, ganti run_all_tests() dengan:
if __name__ == "__main__":
    test_health()
    test_analyze()
    # dll...
```

### 4. Konfigurasi

Edit konfigurasi di `test_api.py`:

```python
# Configuration
BASE_URL = "http://localhost:8000"  # Ganti jika server di tempat lain
TEST_FILE = "test_document.txt"
TEST_EXCEL_FILE = "test_data.xlsx"
```

## 📋 Daftar Test yang Tersedia

### ✅ Core Tests
1. **Health Check** - Test kesehatan API

### ✅ Word Document Tests (10 tests)
2. **Upload Document** - Upload dokumen Word/text
3. **Search Documents** - Pencarian semantik
4. **RAG Query** - Question answering dengan RAG
5. **Text Rewrite** - Menulis ulang teks
6. **Text Analysis** - Analisis teks (readability, sentiment, grammar, style)
7. **Summarization** - Ringkasan teks
8. **Grammar Check** - Pemeriksaan tata bahasa
9. **Paraphrase** - Parafrase teks
10. **Generate Content** - Generate konten baru

### ✅ Excel Tests (4 tests)
11. **Excel Formula** - Generate formula Excel
12. **Excel Query** - Query data Excel dengan natural language
13. **Excel Analysis** - Analisis komprehensif data Excel
14. **Excel Report** - Generate laporan dari data Excel

**Total: 14 Tests**

## 🎯 Output Test

### Format Output
Test akan menampilkan:
- ✅ `PASS` - Test berhasil (hijau)
- ❌ `FAIL` - Test gagal (merah)
- ❌ `ERROR` - Test error (merah)

### Contoh Output:
```
======================================================================
  OFFICE LLM ADD-IN API TEST SUITE v2.5.0
======================================================================

======================================================================
  1. Health Check
======================================================================

Status: 200
{
  "status": "healthy",
  "version": "2.5.0",
  ...
}
✓ Health check passed

...

======================================================================
  TEST SUMMARY
======================================================================

Health Check                   ✅ PASS
Upload Document                ✅ PASS
Search Documents               ✅ PASS
RAG Query                      ✅ PASS
Text Rewrite                   ✅ PASS
Text Analysis                  ✅ PASS
Summarization                  ✅ PASS
Grammar Check                  ✅ PASS
Paraphrase                     ✅ PASS
Generate Content               ✅ PASS
Excel Formula                  ✅ PASS
Excel Query                    ✅ PASS
Excel Analysis                 ✅ PASS
Excel Report                   ✅ PASS

Total: 14/14 tests passed
🎉 All tests passed!
```

## 🔧 Troubleshooting

### Error: Connection Refused
```
✗ Health check error: Connection refused
```
**Solusi:** Pastikan backend server berjalan di `http://localhost:8000`

### Error: 422 Unprocessable Content
```
✗ Text analysis failed: 422 Unprocessable Content
```
**Solusi:**
- Middleware sanitasi sudah ditambahkan di `main.py`
- Cek log server untuk detail error
- Pastikan request body valid

### Error: 500 Internal Server Error
```
✗ Excel query failed: 500 Internal Server Error
```
**Solusi:**
- Cek log server untuk stack trace
- Pastikan semua dependencies terinstall
- Cek konfigurasi Google API Key di `.env`

### Error: Missing API Key
```
Error: GOOGLE_API_KEY not found
```
**Solusi:**
- Buat file `.env` di direktori backend
- Tambahkan: `GOOGLE_API_KEY=your-api-key-here`

## 📝 Test dengan Data Custom

### Upload File Custom
```python
# Ganti TEST_FILE dengan path file Anda
TEST_FILE = "path/to/your/document.txt"
```

### Test dengan Query Custom
```python
# Ganti parameter di fungsi test
test_search_documents(query="query Anda")
test_query_rag(query="Pertanyaan Anda?")
```

### Test Excel dengan Data Custom
```python
# Edit data di test_excel_query():
data = {
    "query": "Pertanyaan Anda?",
    "range_data": {
        "data": [
            ["Header1", "Header2"],
            ["Data1", "Data2"],
            # ... data Anda
        ]
    }
}
```

## 🚀 Tips

1. **Run test bertahap** - Jalankan test satu per satu untuk debugging
2. **Cek logs** - Monitor console server untuk error detail
3. **Delay antar test** - Test sudah include delay 0.5s antar test
4. **Document indexing** - Test search menunggu 5 detik untuk indexing
5. **API rate limits** - Jika test gagal, tunggu beberapa detik dan coba lagi

## 📊 Monitoring

Selama test berjalan, monitor:
1. **Console server** - Lihat request logs dan error
2. **Test output** - Lihat status setiap test
3. **Summary** - Lihat hasil akhir semua test

## 🔍 Debugging

Jika test gagal:

1. **Enable verbose logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **Print response detail:**
```python
print(f"Response: {response.text}")
print(f"Headers: {response.headers}")
```

3. **Cek server logs:**
```bash
# Di terminal server, Anda akan melihat:
INFO:     127.0.0.1:xxxxx - "POST /api/llm/analyze HTTP/1.1" 200 OK
```

## ✨ Update Test

Untuk menambah test baru:

1. Buat fungsi test:
```python
def test_new_feature():
    """Test new feature"""
    print_section("15. New Feature Test")

    data = {...}
    response = requests.post(f"{BASE_URL}/api/new-endpoint", json=data)

    if response.status_code == 200:
        print_success("Test passed")
        return True
    else:
        print_error("Test failed")
        return False
```

2. Tambahkan ke `run_all_tests()`:
```python
tests = [
    ...
    ("New Feature", test_new_feature),
]
```

---

**Happy Testing! 🎉**
