from app.storage.chat_memory import baatien
from app.service.RAG_Service import RAGService

from app.schemas.stream import (
    status_event,
    token_event,
    done_event,
    error_event
)


class ChatService:

    @staticmethod
    def stream(query):

        try:

            # -------------------------
            # STATUS
            # -------------------------

            yield status_event(
                "Searching documents..."
            )


            # -------------------------
            # RAG
            # -------------------------

            answer = RAGService.ask(
                query,
                baatien
            )


            # -------------------------
            # TOKEN STREAM
            # -------------------------

            full_answer = ""

            for chunk in answer:

                full_answer += chunk

                yield token_event(chunk)


            # -------------------------
            # SAVE MEMORY
            # -------------------------

            baatien.append({
                "role": "user",
                "content": query
            })

            baatien.append({
                "role": "assistant",
                "content": full_answer
            })


            # -------------------------
            # DONE
            # -------------------------

            yield done_event()


        except Exception as e:

            print("CHAT ERROR:", e)

            yield error_event(
                str(e)
            )