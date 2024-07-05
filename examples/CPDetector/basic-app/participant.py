from pydantic import BaseModel
from typing import Optional


class Participant(BaseModel):
    id: str = None
    comments: Optional[str] = None
