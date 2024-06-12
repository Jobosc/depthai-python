from pydantic import BaseModel
from typing import Optional


class Participant(BaseModel):
    ID: str = None
    comments: Optional[str] = None
