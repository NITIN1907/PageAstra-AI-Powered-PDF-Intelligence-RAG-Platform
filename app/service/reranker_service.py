from sentence_transformers import CrossEncoder


class RerankerService:

    def __init__(self):
        self.model = None

    def get_model(self):

        if self.model is None:
            self.model = CrossEncoder(
                "cross-encoder/ms-marco-MiniLM-L-6-v2",
                device="cpu"
            )

        return self.model

    # =================================
    # RERANK
    # =================================

    def rerank(
        self,
        query: str,
        documents: list[dict],
        top_k: int = 5
    ):

        if not documents:
            return []

        # -------------------------
        # CREATE QUERY-DOCUMENT PAIRS
        # -------------------------

        pairs = [
            [
                query,
                document["text"]
            ]
            for document in documents
        ]

        # -------------------------
        # SCORE
        # -------------------------

        model = self.get_model()

        scores = model.predict(
            pairs
        )

        # -------------------------
        # ATTACH SCORES
        # -------------------------

        reranked = []

        for document, score in zip(
            documents,
            scores
        ):

            result = document.copy()

            result["rerank_score"] = float(
                score
            )

            reranked.append(
                result
            )

        # -------------------------
        # SORT
        # -------------------------

        reranked.sort(
            key=lambda item:
                item["rerank_score"],
            reverse=True
        )

        # -------------------------
        # TOP K
        # -------------------------

        return reranked[:top_k]


reranker_service = RerankerService()
