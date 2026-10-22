"""Core multi-dataset Information Retrieval system.

Pipeline:
- Load 5 CSV datasets
- Preprocess text
- Build Whoosh inverted index
- Retrieve candidates using Whoosh
- Build Bag of Words with CountVectorizer
- Re-rank candidates using cosine similarity
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from whoosh import index
from whoosh.fields import ID, STORED, TEXT, Schema
from whoosh.qparser import OrGroup, QueryParser

from preprocessing import preprocess


@dataclass
class SearchResult:
    rank: int
    score: float
    source: str
    title: str
    content: str


class MultiDatasetIR:
    EXPECTED_SOURCES = ["etd-usk", "etd-ugm", "kompas", "tempo", "mojok"]

    def __init__(self, datasets_dir: str = "datasets", index_dir: str = "whoosh_index"):
        self.datasets_dir = Path(datasets_dir)
        self.index_dir = Path(index_dir)

    def _dataset_csv(self, source: str) -> Path:
        folder = self.datasets_dir / source
        candidates = sorted(folder.glob("*.csv"))
        if not candidates:
            raise FileNotFoundError(f"CSV untuk dataset '{source}' tidak ditemukan di {folder}")
        return candidates[0]

    def load_all_documents(self) -> pd.DataFrame:
        """Load dan gabungkan 5 dataset menjadi satu DataFrame."""
        frames = []

        for source in self.EXPECTED_SOURCES:
            csv_path = self._dataset_csv(source)
            df = pd.read_csv(csv_path, usecols=["judul", "konten"])
            df = df.fillna("")
            df["source"] = source
            frames.append(df)

        combined = pd.concat(frames, ignore_index=True)
        combined.insert(0, "doc_id", [f"DOC-{i:06d}" for i in range(1, len(combined) + 1)])
        combined["processed"] = (
            combined["judul"].astype(str) + " " + combined["konten"].astype(str)
        ).map(preprocess)
        return combined

    def build_index(self, recreate: bool = True) -> int:
        """Preprocess seluruh dataset lalu membuat Whoosh index."""
        if recreate and self.index_dir.exists():
            shutil.rmtree(self.index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        schema = Schema(
            doc_id=ID(stored=True, unique=True),
            source=ID(stored=True),
            title=TEXT(stored=True),
            content=STORED,
            processed=TEXT(stored=True),
        )

        ix = index.create_in(self.index_dir, schema)
        writer = ix.writer(limitmb=256)

        total = 0
        for source in self.EXPECTED_SOURCES:
            csv_path = self._dataset_csv(source)
            df = pd.read_csv(csv_path, usecols=["judul", "konten"]).fillna("")

            for _, row in df.iterrows():
                total += 1
                title = str(row["judul"])
                content = str(row["konten"])
                writer.add_document(
                    doc_id=f"DOC-{total:06d}",
                    source=source,
                    title=title,
                    content=content,
                    processed=preprocess(title + " " + content),
                )

                if total % 2000 == 0:
                    print(f"  Indexing: {total:,} dokumen")

        writer.commit()
        print(f"  Indexing: {total:,}/{total:,} dokumen")
        return total

    def _open_index(self):
        if not self.index_dir.exists() or not index.exists_in(self.index_dir):
            raise RuntimeError(
                "Index belum tersedia. Pilih menu [1] Load & Index Dataset terlebih dahulu."
            )
        return index.open_dir(self.index_dir)

    @staticmethod
    def _cosine_rerank(query_processed: str, candidates: List[dict]) -> List[tuple]:
        """Representasi BoW + cosine similarity untuk candidate reranking."""
        if not candidates:
            return []

        corpus = [query_processed] + [c["processed"] for c in candidates]
        vectorizer = CountVectorizer(token_pattern=r"(?u)\b\w+\b")
        matrix = vectorizer.fit_transform(corpus)
        similarities = cosine_similarity(matrix[0:1], matrix[1:]).flatten()

        ranked = list(zip(candidates, similarities))
        ranked.sort(key=lambda item: item[1], reverse=True)
        return ranked

    def search(self, query_text: str, top_k: int = 5, candidate_limit: int = 100) -> List[SearchResult]:
        query_processed = preprocess(query_text)
        if not query_processed:
            return []

        ix = self._open_index()
        parser = QueryParser("processed", schema=ix.schema, group=OrGroup.factory(0.9))
        whoosh_query = parser.parse(query_processed)

        candidates = []
        with ix.searcher() as searcher:
            hits = searcher.search(whoosh_query, limit=candidate_limit)
            for hit in hits:
                candidates.append(
                    {
                        "doc_id": hit["doc_id"],
                        "source": hit["source"],
                        "title": hit["title"],
                        "content": hit["content"],
                        "processed": hit["processed"],
                    }
                )

        ranked = self._cosine_rerank(query_processed, candidates)[:top_k]

        results = []
        for rank, (doc, score) in enumerate(ranked, start=1):
            results.append(
                SearchResult(
                    rank=rank,
                    score=float(score),
                    source=doc["source"],
                    title=doc["title"],
                    content=doc["content"],
                )
            )
        return results

    @staticmethod
    def snippet(text: str, max_chars: int = 220) -> str:
        compact = " ".join(str(text).split())
        if len(compact) <= max_chars:
            return compact
        return compact[:max_chars].rstrip() + "..."

    def dataset_summary(self) -> pd.DataFrame:
        rows = []
        for source in self.EXPECTED_SOURCES:
            path = self._dataset_csv(source)
            df = pd.read_csv(path, usecols=["judul", "konten"])
            rows.append({"dataset": source, "jumlah_dokumen": len(df)})
        return pd.DataFrame(rows)
