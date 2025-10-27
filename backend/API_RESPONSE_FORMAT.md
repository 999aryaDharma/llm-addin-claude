# 📋 API Response Format - Konsistensi Structure

## Endpoint: `/api/llm/analyze`

### Request Format
```json
{
  "text": "string",
  "analysis_type": "readability|sentiment|grammar|style|general",
  "include_suggestions": true
}
```

### Response Format (Konsisten)

Semua response mengikuti struktur yang sama:

```json
{
  "success": true,
  "analysis": {
    // Analysis-specific fields (in English)
  },
  "metrics": {
    "word_count": 65,
    "sentence_count": 3,
    "avg_words_per_sentence": 21.67,
    "character_count": 392,
    "paragraph_count": 1
  },
  "suggestions": [
    "saran 1",
    "saran 2",
    "saran 3"
  ],
  "metadata": {
    "analysis_type": "readability",
    "text_length": 392
  }
}
```

## Analysis Types & Expected Keys

### 1. Readability Analysis
**analysis_type**: `"readability"`

**Expected Keys** (konsisten dalam bahasa Inggris):
```json
{
  "analysis": {
    "reading_level": "pemula|menengah|lanjutan",
    "readability_score": 0-100,
    "vocabulary_complexity": "penjelasan",
    "sentence_structure": "analisis struktur"
  },
  "suggestions": ["saran 1", "saran 2"]
}
```

### 2. Sentiment Analysis
**analysis_type**: `"sentiment"`

**Expected Keys**:
```json
{
  "analysis": {
    "overall_sentiment": "positif|negatif|netral",
    "sentiment_score": -1.0 to 1.0,
    "emotional_tone": "penjelasan",
    "key_emotions": ["emosi 1", "emosi 2"]
  },
  "suggestions": ["saran 1", "saran 2"]
}
```

### 3. Grammar Check
**analysis_type**: `"grammar"`

**Expected Keys**:
```json
{
  "analysis": {
    "errors": [
      {
        "type": "grammar|punctuation|word_choice",
        "text": "teks error",
        "correction": "koreksi"
      }
    ],
    "score": 0-100,
    "summary": "ringkasan"
  },
  "suggestions": ["saran 1", "saran 2"]
}
```

### 4. Style Analysis
**analysis_type**: `"style"`

**Expected Keys**:
```json
{
  "analysis": {
    "tone": "formal|casual|academic|persuasive",
    "reading_level": "pemula|menengah|lanjutan",
    "features": ["fitur 1", "fitur 2"],
    "suggestions": ["saran 1", "saran 2"]
  }
}
```

### 5. General Analysis
**analysis_type**: `"general"`

**Expected Keys**:
```json
{
  "analysis": {
    "overall_assessment": "penilaian",
    "strengths": ["kekuatan 1", "kekuatan 2"],
    "weaknesses": ["kelemahan 1", "kelemahan 2"],
    "key_themes": ["tema 1", "tema 2"]
  },
  "suggestions": ["saran 1", "saran 2"]
}
```

## ✅ Aturan Konsistensi

### 1. Key Names (Nama Field)
- ✅ **Selalu gunakan bahasa Inggris** dengan underscore (`snake_case`)
- ❌ **Jangan gunakan bahasa Indonesia** untuk key names
- ✅ Contoh baik: `reading_level`, `readability_score`, `suggestions`
- ❌ Contoh buruk: `level_pembaca`, `skor_keterbacaan`, `saran_perbaikan`

### 2. Suggestions Field
- ✅ **Selalu di top-level** sebagai array `suggestions`
- ❌ **Jangan nested** di dalam `analysis`
- ✅ Selalu array, bukan object
- ✅ Harus terisi jika `include_suggestions: true`

### 3. Content Language (Isi Konten)
- ✅ **Konten/nilai** boleh bahasa Indonesia
- ✅ Contoh: `"reading_level": "Menengah"` ← Key Inggris, value Indonesia
- ✅ Penjelasan dalam suggestions boleh bahasa Indonesia

### 4. Normalization
Backend akan otomatis menormalisasi key dari Indonesia ke Inggris:
- `level_pembaca` → `reading_level`
- `skor_keterbacaan` → `readability_score`
- `saran_perbaikan` → dipindahkan ke top-level `suggestions`

## 🔄 Migration Guide

### Before (Inconsistent):
```json
{
  "analysis": {
    "level_pembaca": "Menengah",
    "skor_keterbacaan": 68,
    "saran_perbaikan": ["saran 1", "saran 2"]  // ❌ Di dalam analysis
  },
  "suggestions": []  // ❌ Kosong
}
```

### After (Consistent):
```json
{
  "analysis": {
    "reading_level": "Menengah",           // ✅ Key dalam Inggris
    "readability_score": 68                // ✅ Key dalam Inggris
  },
  "suggestions": ["saran 1", "saran 2"]    // ✅ Di top-level
}
```

## 🧪 Testing

Test untuk memverifikasi konsistensi:

```python
# Test consistency
response = requests.post("/api/llm/analyze", json={
    "text": "test text",
    "analysis_type": "readability",
    "include_suggestions": True
})

result = response.json()

# Verify structure
assert "suggestions" in result  # Top-level
assert len(result["suggestions"]) > 0  # Not empty
assert "analysis" in result

# Verify English keys
analysis = result["analysis"]
assert "reading_level" in analysis  # ✅ English
assert "level_pembaca" not in analysis  # ❌ Indonesian

print("✓ Response format is consistent!")
```

## 📌 Notes

1. **Backward Compatibility**: Backend tetap menerima key Indonesia dari LLM dan otomatis menormalisasi
2. **Client Side**: Frontend/client bisa always expect English keys
3. **Content Language**: Isi/konten tetap bahasa Indonesia sesuai prompt
4. **Error Handling**: Jika LLM return format berbeda, backend akan normalize otomatis

---

**Last Updated**: 2025-01-XX
**Version**: 2.5.0
