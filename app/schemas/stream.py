from enum import Enum
from typing import Any

from pydantic import BaseModel


class StreamEventType(str, Enum):

    STATUS = "status"
    TOKEN = "token"
    SOURCE = "source"
    DONE = "done"
    ERROR = "error"


class StreamEvent(BaseModel):

    type: StreamEventType
    data: dict[str, Any] | None = None


def status_event(message: str) -> StreamEvent:

    return StreamEvent(
        type=StreamEventType.STATUS,
        data={
            "message": message
        }
    )


def token_event(content: str) -> StreamEvent:

    return StreamEvent(
        type=StreamEventType.TOKEN,
        data={
            "content": content
        }
    )


def source_event(
    document: str,
    page: int
) -> StreamEvent:

    return StreamEvent(
        type=StreamEventType.SOURCE,
        data={
            "document": document,
            "page": page
        }
    )


def done_event() -> StreamEvent:

    return StreamEvent(
        type=StreamEventType.DONE
    )


def error_event(message: str) -> StreamEvent:

    return StreamEvent(
        type=StreamEventType.ERROR,
        data={
            "message": message
        }
    )