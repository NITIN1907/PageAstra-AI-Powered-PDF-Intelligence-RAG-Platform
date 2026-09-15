import json
import os
import tempfile
import threading

import faiss
import numpy as np
from rank_bm25 import BM25Okapi

from app.service.embedding_service import EmbeddingService
from app.service.Pdf_service import PageContent


class SearchService:

    def __init__(self):

        self.dimension = 384

        # ==========================================
        # FAISS
        # ==========================================

        self.index = faiss.IndexFlatL2(
            self.dimension
        )

        # Must always remain in the same order
        # as FAISS vectors.
        self.pages = []

        # ==========================================
        # BM25
        # ==========================================

        self.bm25 = None

        # ==========================================
        # THREAD SAFETY
        # ==========================================

        self.lock = threading.Lock()

        # ==========================================
        # STORAGE
        # ==========================================

        self.storage_dir = "storage"

        self.index_path = os.path.join(
            self.storage_dir,
            "index.faiss"
        )

        self.manifest_path = os.path.join(
            self.storage_dir,
            "index_manifest.json"
        )

        os.makedirs(
            self.storage_dir,
            exist_ok=True
        )

    # ==================================================
    # TOKENIZATION
    # ==================================================

    @staticmethod
    def tokenize(text: str):

        return text.lower().split()

    # ==================================================
    # BUILD BM25
    # ==================================================

    def _build_bm25(self):

        if not self.pages:
            self.bm25 = None
            return

        tokenized_documents = [
            self.tokenize(page.text)
            for page in self.pages
        ]

        self.bm25 = BM25Okapi(
            tokenized_documents
        )

    # ==================================================
    # CREATE PAGE OBJECT
    # ==================================================

    @staticmethod
    def _to_page_content(chunk):

        return PageContent(
            document_id=chunk.document_id,
            document_name=chunk.document.filename,
            page_number=chunk.page_number,
            chunk_id=chunk.chunk_id,
            text=chunk.text
        )

    # ==================================================
    # ADD DOCUMENT
    # ==================================================

    def add_document(self, pages):

        if not pages:
            raise ValueError(
                "No chunks found"
            )

        # Generate embeddings BEFORE modifying
        # the existing FAISS index.
        embeddings = np.array(
            [
                EmbeddingService.embed(
                    page.text
                )
                for page in pages
            ],
            dtype="float32"
        )

        if embeddings.ndim != 2:
            raise ValueError(
                "Invalid embedding shape"
            )

        if embeddings.shape[1] != self.dimension:
            raise ValueError(
                f"Embedding dimension mismatch. "
                f"Expected {self.dimension}, "
                f"got {embeddings.shape[1]}"
            )

        with self.lock:

            # Add vectors
            self.index.add(
                embeddings
            )

            # Keep metadata in EXACT same order
            self.pages.extend(
                pages
            )

            # Rebuild BM25
            self._build_bm25()

            # Persist
            self.save()

        print(
            f"Added {len(pages)} chunks to FAISS"
        )

    # ==================================================
    # DENSE SEARCH
    # ==================================================

    def _dense_search(
        self,
        query: str,
        candidate_k: int
    ):

        if self.index.ntotal == 0:
            return []

        query_embedding = np.array(
            [
                EmbeddingService.embed(
                    query
                )
            ],
            dtype="float32"
        )

        actual_k = min(
            candidate_k,
            self.index.ntotal
        )

        distances, indices = (
            self.index.search(
                query_embedding,
                actual_k
            )
        )

        results = []

        for distance, idx in zip(
            distances[0],
            indices[0]
        ):

            if idx < 0:
                continue

            page = self.pages[idx]

            dense_score = (
                1.0 /
                (1.0 + float(distance))
            )

            results.append(
                {
                    "document_id":
                        page.document_id,

                    "document":
                        page.document_name,

                    "page":
                        page.page_number,

                    "chunk_id":
                        page.chunk_id,

                    "text":
                        page.text,

                    "distance":
                        float(distance),

                    "dense_score":
                        dense_score
                }
            )

        return results

    # ==================================================
    # BM25 SEARCH
    # ==================================================

    def _bm25_search(
        self,
        query: str,
        candidate_k: int
    ):

        if self.bm25 is None:
            return []

        query_tokens = self.tokenize(
            query
        )

        scores = self.bm25.get_scores(
            query_tokens
        )

        candidate_k = min(
            candidate_k,
            len(scores)
        )

        indices = np.argsort(
            scores
        )[::-1][:candidate_k]

        results = []

        for idx in indices:

            idx = int(idx)

            page = self.pages[idx]

            results.append(
                {
                    "document_id":
                        page.document_id,

                    "document":
                        page.document_name,

                    "page":
                        page.page_number,

                    "chunk_id":
                        page.chunk_id,

                    "text":
                        page.text,

                    "bm25_score":
                        float(scores[idx])
                }
            )

        return results

    # ==================================================
    # NORMALIZE SCORES
    # ==================================================

    @staticmethod
    def _normalize_scores(scores):

        if not scores:
            return {}

        values = np.array(
            list(scores.values()),
            dtype="float32"
        )

        minimum = values.min()
        maximum = values.max()

        if maximum == minimum:

            return {
                key: 1.0
                for key in scores
            }

        return {
            key: float(
                (value - minimum) /
                (maximum - minimum)
            )
            for key, value in scores.items()
        }

    # ==================================================
    # HYBRID SEARCH
    # ==================================================

    def search(
        self,
        query: str,
        top_k: int = 5
    ):

        if not query or not query.strip():
            raise ValueError(
                "Query cannot be empty"
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than 0"
            )

        if self.index.ntotal == 0:
            raise ValueError(
                "No documents have been indexed"
            )

        candidate_k = min(
            max(top_k * 4, 10),
            self.index.ntotal
        )

        # ==========================================
        # Dense retrieval
        # ==========================================

        dense_results = self._dense_search(
            query,
            candidate_k
        )

        # ==========================================
        # BM25 retrieval
        # ==========================================

        bm25_results = self._bm25_search(
            query,
            candidate_k
        )

        # ==========================================
        # Score maps
        # ==========================================

        dense_scores = {
            result["chunk_id"]:
                result["dense_score"]
            for result in dense_results
        }

        bm25_scores = {
            result["chunk_id"]:
                result["bm25_score"]
            for result in bm25_results
        }

        # ==========================================
        # Normalize
        # ==========================================

        normalized_dense = (
            self._normalize_scores(
                dense_scores
            )
        )

        normalized_bm25 = (
            self._normalize_scores(
                bm25_scores
            )
        )

        # ==========================================
        # Candidate union
        # ==========================================

        candidate_ids = (
            set(dense_scores)
            |
            set(bm25_scores)
        )

        metadata = {}

        for result in dense_results:

            metadata[
                result["chunk_id"]
            ] = result

        for result in bm25_results:

            chunk_id = result[
                "chunk_id"
            ]

            if chunk_id not in metadata:

                metadata[
                    chunk_id
                ] = result

        # ==========================================
        # Hybrid scoring
        # ==========================================

        results = []

        for chunk_id in candidate_ids:

            dense_score = (
                normalized_dense.get(
                    chunk_id,
                    0.0
                )
            )

            bm25_score = (
                normalized_bm25.get(
                    chunk_id,
                    0.0
                )
            )

            # 60% semantic retrieval
            # 40% keyword retrieval

            hybrid_score = (
                0.6 * dense_score
                +
                0.4 * bm25_score
            )

            item = metadata[
                chunk_id
            ].copy()

            item["dense_score"] = float(
                dense_score
            )

            item["bm25_score"] = float(
                bm25_score
            )

            item["hybrid_score"] = float(
                hybrid_score
            )

            results.append(
                item
            )

        # ==========================================
        # Sort
        # ==========================================

        results.sort(
            key=lambda item:
                item["hybrid_score"],
            reverse=True
        )

        return results[:top_k]

    # ==================================================
    # REBUILD FROM DATABASE
    # ==================================================

    def rebuild_from_database(
        self,
        chunks
    ):

        new_index = faiss.IndexFlatL2(
            self.dimension
        )

        new_pages = []

        if chunks:

            embeddings = np.array(
                [
                    EmbeddingService.embed(
                        chunk.text
                    )
                    for chunk in chunks
                ],
                dtype="float32"
            )

            if embeddings.shape[1] != self.dimension:
                raise ValueError(
                    "Embedding dimension mismatch"
                )

            new_index.add(
                embeddings
            )

            new_pages = [
                self._to_page_content(
                    chunk
                )
                for chunk in chunks
            ]

        with self.lock:

            self.index = new_index

            self.pages = new_pages

            self._build_bm25()

            self.save()

        print(
            "FAISS rebuilt from PostgreSQL: "
            f"{len(new_pages)} chunks"
        )

    # ==================================================
    # SAVE
    # ==================================================

    def save(self):

        if self.index is None:
            return

        # ==========================================
        # SAVE FAISS
        # ==========================================

        fd, temp_index_path = tempfile.mkstemp(
            suffix=".faiss",
            dir=self.storage_dir
        )

        os.close(fd)

        try:

            faiss.write_index(
                self.index,
                temp_index_path
            )

            os.replace(
                temp_index_path,
                self.index_path
            )

        finally:

            if os.path.exists(
                temp_index_path
            ):
                os.remove(
                    temp_index_path
                )

        # ==========================================
        # SAVE MANIFEST
        # ==========================================

        manifest = {
            "total_vectors":
                self.index.ntotal,

            "chunk_ids":
                [
                    page.chunk_id
                    for page in self.pages
                ]
        }

        fd, temp_manifest_path = tempfile.mkstemp(
            suffix=".json",
            dir=self.storage_dir
        )

        os.close(fd)

        try:

            with open(
                temp_manifest_path,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    manifest,
                    file,
                    indent=2
                )

            os.replace(
                temp_manifest_path,
                self.manifest_path
            )

        finally:

            if os.path.exists(
                temp_manifest_path
            ):
                os.remove(
                    temp_manifest_path
                )

    # ==================================================
    # LOAD
    # ==================================================

    def load(
        self,
        chunks
    ):

        if not os.path.exists(
            self.index_path
        ):
            return False

        if not os.path.exists(
            self.manifest_path
        ):
            return False

        try:

            index = faiss.read_index(
                self.index_path
            )

            with open(
                self.manifest_path,
                "r",
                encoding="utf-8"
            ) as file:

                manifest = json.load(
                    file
                )

            db_chunk_ids = [
                chunk.chunk_id
                for chunk in chunks
            ]

            saved_chunk_ids = (
                manifest.get(
                    "chunk_ids",
                    []
                )
            )

            saved_total_vectors = (
                manifest.get(
                    "total_vectors",
                    -1
                )
            )

            # ======================================
            # Validate FAISS count
            # ======================================

            if index.ntotal != len(chunks):

                print(
                    "FAISS/DB count mismatch. "
                    "Rebuilding..."
                )

                return False

            # ======================================
            # Validate manifest count
            # ======================================

            if saved_total_vectors != index.ntotal:

                print(
                    "Manifest/FAISS count mismatch. "
                    "Rebuilding..."
                )

                return False

            # ======================================
            # Validate ordering
            # ======================================

            if saved_chunk_ids != db_chunk_ids:

                print(
                    "FAISS/DB ordering mismatch. "
                    "Rebuilding..."
                )

                return False

            # ======================================
            # Restore metadata
            # ======================================

            pages = [
                self._to_page_content(
                    chunk
                )
                for chunk in chunks
            ]

            with self.lock:

                self.index = index

                self.pages = pages

                self._build_bm25()

            print(
                "FAISS loaded successfully: "
                f"{index.ntotal} vectors"
            )

            return True

        except Exception as e:

            print(
                f"FAISS load failed: {e}"
            )

            return False


search_service = SearchService()