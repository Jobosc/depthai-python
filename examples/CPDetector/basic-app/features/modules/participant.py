from pydantic import BaseModel
from typing import Optional


class Participant(BaseModel):
    id: str
    comments: Optional[str] = None
