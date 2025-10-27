# 🚀 Office LLM Add-in

AI-powered Office Add-in untuk Microsoft Word dan Excel dengan kemampuan LLM (Large Language Model) menggunakan Google Gemini.

## ✨ Features

### 📝 Word Features
- ✅ **Text Rewriting** - Tulis ulang teks dengan berbagai gaya
- ✅ **Text Analysis** - Analisis readability, sentiment, grammar, style
- ✅ **Summarization** - Ringkas dokumen panjang
- ✅ **Grammar Check** - Pemeriksaan tata bahasa
- ✅ **Paraphrase** - Generate variasi parafrase
- ✅ **Content Generation** - Buat konten baru dengan AI
- ✅ **RAG Query** - Question answering dengan Retrieval-Augmented Generation
- ✅ **Semantic Search** - Pencarian dokumen dengan semantic similarity

### 📊 Excel Features
- ✅ **Formula Generation** - Generate formula Excel dengan natural language
- ✅ **Data Query** - Query data dengan bahasa natural
- ✅ **Data Analysis** - Analisis komprehensif dataset
- ✅ **Report Generation** - Generate laporan otomatis (executive, detailed, technical)
- ✅ **Trend Prediction** - Prediksi tren dari data
- ✅ **Dataset Comparison** - Bandingkan dua dataset
- ✅ **Data Explanation** - Penjelasan data dalam bahasa natural

## 🏗️ Architecture

```
llm-addin/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core functionality (RAG, summarization)
│   │   ├── models/         # Pydantic models
│   │   ├── services/       # Business logic services
│   │   ├── utils/          # Utilities
│   │   └── main.py         # FastAPI application
│   ├── data/               # Data storage (gitignored)
│   │   ├── chroma/         # ChromaDB vector store
│   │   ├── cache/          # SQLite cache
│   │   ├── logs/           # Application logs
│   │   └── uploads/        # Uploaded files
│   ├── test_api.py         # API test suite
│   ├── .env.example        # Environment template
│   └── requirements.txt    # Python dependencies
└── frontend/               # (Future) Office Add-in UI

```

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI
- **LLM**: Google Gemini (gemini-1.5-flash)
- **Vector DB**: ChromaDB
- **Embeddings**: Google Embedding API
- **Cache**: SQLite
- **Document Processing**: python-docx, pypdf, openpyxl
- **Data Analysis**: pandas, numpy

### Key Libraries
- `langchain` - LLM orchestration
- `chromadb` - Vector database
- `pydantic` - Data validation
- `fastapi` - Web framework
- `uvicorn` - ASGI server

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Google API Key (Gemini)

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/llm-addin.git
cd llm-addin
```

### 2. Setup Backend

#### Create Virtual Environment
```bash
cd backend

# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Configure Environment
```bash
# Copy template
copy .env.example .env   # Windows
cp .env.example .env     # Linux/Mac

# Edit .env dan isi GOOGLE_API_KEY
# Dapatkan API key dari: https://makersuite.google.com/app/apikey
```

**PENTING:** Isi `.env` dengan konfigurasi yang benar:
```env
GOOGLE_API_KEY=your-actual-api-key-here
```

#### Create Data Directories
```bash
# Windows
mkdir data\chroma data\cache data\logs data\uploads

# Linux/Mac
mkdir -p data/{chroma,cache,logs,uploads}
```

### 3. Run Server
```bash
# Development mode with auto-reload
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Server akan berjalan di: `http://localhost:8000`

### 4. Test API
```bash
# Run test suite
python test_api.py
```

### 5. Access Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Main Endpoints

#### Word LLM
- `POST /api/llm/rewrite` - Rewrite text
- `POST /api/llm/analyze` - Analyze text
- `POST /api/llm/summarize` - Summarize text
- `POST /api/llm/generate` - Generate content
- `POST /api/llm/grammar-check` - Check grammar
- `POST /api/llm/paraphrase` - Paraphrase text

#### Excel LLM
- `POST /api/excel/formula` - Generate formula
- `POST /api/excel/query` - Query data
- `POST /api/excel/llm/analyze-comprehensive` - Analyze dataset
- `POST /api/excel/llm/generate-report` - Generate report
- `POST /api/excel/llm/predict-trends` - Predict trends
- `POST /api/excel/llm/compare-datasets` - Compare datasets

#### Document Management
- `POST /api/documents/upload` - Upload document
- `POST /api/documents/search` - Semantic search
- `GET /api/documents/stats` - Get statistics

#### RAG Query
- `POST /api/query/search` - Question answering with RAG

### Example Request

```bash
# Text Analysis
curl -X POST "http://localhost:8000/api/llm/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Ini adalah contoh teks untuk analisis.",
    "analysis_type": "readability",
    "include_suggestions": true
  }'
```

## 🧪 Testing

### Run All Tests
```bash
python test_api.py
```

### Run Specific Test
Edit `test_api.py`:
```python
if __name__ == "__main__":
    test_health()
    test_analyze()
```

### Test Coverage
- ✅ 14 comprehensive tests
- ✅ Word document tests (10)
- ✅ Excel tests (4)
- ✅ Core functionality tests

Lihat [README_TESTING.md](backend/README_TESTING.md) untuk detail lengkap.

## 📋 Configuration

### Environment Variables

Lihat [.env.example](backend/.env.example) untuk daftar lengkap.

**Required:**
- `GOOGLE_API_KEY` - Google Gemini API key

**Optional (with defaults):**
- `API_PORT=8000`
- `LLM_MODEL=gemini-1.5-flash`
- `TEMPERATURE=0.7`
- `CHUNK_SIZE=1000`
- `LOG_LEVEL=INFO`

## 🔒 Security

### Best Practices
1. ✅ **JANGAN** commit file `.env` ke git
2. ✅ Gunakan API key yang berbeda untuk dev/production
3. ✅ Rotate API keys secara berkala
4. ✅ Set CORS_ORIGINS yang spesifik di production
5. ✅ Generate SECRET_KEY dan ENCRYPTION_KEY yang kuat

### Generate Secret Keys
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 🐛 Troubleshooting

### Error: GOOGLE_API_KEY not found
**Solusi:** Pastikan file `.env` sudah dibuat dan berisi `GOOGLE_API_KEY`

### Error: 422 Unprocessable Content
**Solusi:** Middleware sanitasi sudah ditambahkan untuk handle control characters

### Error: ChromaDB connection failed
**Solusi:** Pastikan direktori `data/chroma` exists dan writable

### Error: Import error
**Solusi:** Install dependencies: `pip install -r requirements.txt`

## 📖 Documentation

- [Testing Guide](backend/README_TESTING.md) - Panduan testing lengkap
- [API Response Format](backend/API_RESPONSE_FORMAT.md) - Format response API
- [Swagger Docs](http://localhost:8000/docs) - Interactive API docs

## 🚧 Development

### Project Structure
```
backend/app/
├── api/              # API route handlers
│   ├── llm.py       # Word LLM endpoints
│   ├── llm_excel.py # Excel LLM endpoints
│   ├── documents.py # Document management
│   └── query.py     # RAG query endpoints
├── core/            # Core business logic
│   ├── chroma_engine.py    # Vector DB
│   ├── summarizer.py       # Text summarization
│   ├── summarizer_excel.py # Excel analysis
│   └── cache_manager.py    # Caching
├── models/          # Pydantic models
├── services/        # Business services
│   ├── llm_service.py     # LLM wrapper
│   ├── parser.py          # Document parser
│   └── excel_parser.py    # Excel parser
└── utils/           # Utilities
```

### Code Style
- Python: PEP 8
- Type hints: Menggunakan typing
- Docstrings: Google style
- Async/await untuk I/O operations

### Adding New Features

1. **Add new endpoint** di `app/api/`
2. **Add business logic** di `app/services/`
3. **Add model** di `app/models/`
4. **Add test** di `test_api.py`
5. **Update documentation**

## 📝 API Response Consistency

Semua endpoint mengikuti format response yang konsisten:
- ✅ Key names dalam bahasa Inggris (snake_case)
- ✅ Suggestions di top-level (bukan nested)
- ✅ Structure yang predictable

Lihat [API_RESPONSE_FORMAT.md](backend/API_RESPONSE_FORMAT.md) untuk detail.

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Your Name - [@yourusername](https://github.com/yourusername)

## 🙏 Acknowledgments

- Google Gemini for LLM capabilities
- FastAPI for excellent web framework
- ChromaDB for vector storage
- LangChain for LLM orchestration

## 📞 Support

- 📧 Email: your.email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/llm-addin/issues)
- 📖 Docs: [Documentation](https://docs.yourproject.com)

---

**Made with ❤️ using Google Gemini & FastAPI**
