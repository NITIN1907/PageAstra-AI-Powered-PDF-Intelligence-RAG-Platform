from app.service.search_service import search_service
from app.service.reranker_service import reranker_service
from app.prompt.System_prompt import PromptService
from app.service.groq_service import GroqService


class RAGService:

    # =================================
    # CONFIGURATION
    # =================================

    RETRIEVAL_TOP_K = 20

    FINAL_TOP_K = 5

    RELEVANCE_THRESHOLD = 0.35

    MIN_RELEVANT_RESULTS = 1

    # =================================
    # ASK
    # =================================

    @staticmethod
    def ask(
        query,
        history
    ):

        # =================================
        # STEP 1
        # HYBRID RETRIEVAL
        # =================================

        candidates = search_service.search(
            query,
            top_k=RAGService.RETRIEVAL_TOP_K
        )

        if not candidates:

            return RAGService._refusal()

        # =================================
        # STEP 2
        # RERANK
        # =================================

        reranked = reranker_service.rerank(
            query=query,
            documents=candidates,
            top_k=RAGService.FINAL_TOP_K
        )

        if not reranked:

            return RAGService._refusal()

        # =================================
        # STEP 3
        # RELEVANCE GATE
        # =================================

        relevant_context = [

            item

            for item in reranked

            if item["hybrid_score"]
            >= RAGService.RELEVANCE_THRESHOLD

        ]

        if len(relevant_context) < (
            RAGService.MIN_RELEVANT_RESULTS
        ):

            return RAGService._refusal()

        # =================================
        # STEP 4
        # BUILD GROUNDED PROMPT
        # =================================

        prompt = PromptService.build(
            relevant_context,
            query
        )

        # =================================
        # STEP 5
        # CONVERSATION HISTORY
        # =================================

        messages = history.copy()

        messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        # =================================
        # STEP 6
        # LLM
        # =================================

        return GroqService.stream(
            messages
        )

    # =================================
    # REFUSAL
    # =================================

    @staticmethod
    def _refusal():

        return iter(
            [
                "I don't have enough information "
                "in the provided documents."
            ]
        )