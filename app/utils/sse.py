from app.schemas.stream import StreamEvent

def format_sse(event: StreamEvent) -> str:

    return f"data: {event.model_dump_json()}\n\n"