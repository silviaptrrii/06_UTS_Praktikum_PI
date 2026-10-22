# UTS Praktikum Penelusuran Informasi
## Multi-Dataset Information Retrieval System (CLI-Based)

Proyek ini membangun sistem Information Retrieval berbasis CLI yang menggabungkan lima dataset: `etd-usk`, `etd-ugm`, `kompas`, `tempo`, dan `mojok`.

## Fitur

- Case folding, tokenization, dan stopword removal.
- Indexing dan candidate retrieval menggunakan Whoosh.
- Representasi Bag of Words menggunakan `CountVectorizer`.
- Ranking dokumen menggunakan cosine similarity.
- Menampilkan 5 dokumen teratas.
- Mendukung seluruh lima dataset dalam satu sistem.

## Struktur Folder

```text
.
├── main.py
├── ir_system.py
├── preprocessing.py
├── requirements.txt
├── sample_queries.txt
├── README.md
├── tests/
│   └── test_preprocessing.py
└── datasets/
    ├── etd-usk/
    │   └── data.csv
    ├── etd-ugm/
    │   └── data.csv
    ├── kompas/
    │   └── data.csv
    ├── tempo/
    │   └── data.csv
    └── mojok/
        └── data.csv
```

Folder `whoosh_index/` akan dibuat otomatis setelah menu **Load & Index Dataset** dijalankan.

## Instalasi

Gunakan Python 3.10+.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
.venv\Scripts\activate
```

Instal dependency:

```bash
pip install -r requirements.txt
```

## Menjalankan Program

```bash
python main.py
```

Menu:

```text
=== INFORMATION RETRIEVAL SYSTEM ===
[1] Load & Index Dataset
[2] Search Query
[3] Exit
====================================
```

### Pertama Kali Menjalankan

Pilih menu **[1] Load & Index Dataset**. Program akan:

1. Membaca lima dataset CSV.
2. Melakukan preprocessing teks.
3. Menggabungkan judul dan konten dokumen.
4. Membuat Whoosh inverted index.

Setelah index selesai, pilih **[2] Search Query**.

## Pipeline Pencarian

```text
Query Pengguna
      ↓
Preprocessing
      ↓
Whoosh Candidate Retrieval
      ↓
CountVectorizer (Bag of Words)
      ↓
Cosine Similarity
      ↓
Sorting Descending
      ↓
Top 5 Dokumen
```

Whoosh digunakan untuk mendapatkan kandidat dokumen secara efisien. Kandidat tersebut kemudian direpresentasikan menggunakan Bag of Words bersama query. Skor akhir yang ditampilkan berasal dari cosine similarity.

## Contoh Query

```text
machine learning prediksi harga apartemen
pembelajaran matematika mind mapping
pesawat penerbangan
```

## Pengujian Preprocessing

Dari root folder proyek:

```bash
python -m unittest discover -s tests -v
```

## Catatan Library

Proyek hanya menggunakan library yang diizinkan pada soal:

- Python standard library
- pandas
- scikit-learn
- Whoosh

Tidak menggunakan NLTK, Sastrawi, spaCy, Elasticsearch, atau library IR eksternal lain.

## Identitas Tim

- No. Kelompok: **[ISI NOMOR KELOMPOK]**
- Anggota 1: **[Roseline Balqist - 2408107010079]**
- Anggota 2: **[Silvia Putri - 2408107010086]**


