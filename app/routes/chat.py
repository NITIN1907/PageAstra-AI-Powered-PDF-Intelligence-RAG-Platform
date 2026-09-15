from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.chat import chatRequest
from app.service.chat_service import ChatService
from app.utils.sse import format_sse

router = APIRouter()


@router.post("/chat/stream")
def chat_stream(request: chatRequest):

    def event_stream():

        for chunk in ChatService.stream(request.message):
            yield format_sse(chunk)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )

# @router.post("/chat/stream")
# def chat_stream(request: chatRequest):

#     def test_stream():

#         for chunk in ChatService.stream(request.message):
#             print("ROUTE CHUNK:", repr(chunk))
#             yield chunk

#     return StreamingResponse(
#         test_stream(),
#         media_type="text/plain"
#     )