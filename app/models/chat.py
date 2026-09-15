from pydantic import BaseModel

class chatRequest(BaseModel):
    message:str