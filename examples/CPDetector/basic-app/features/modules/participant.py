from typing import Optional

from pydantic import BaseModel


class Participant(BaseModel):
    id: str
    comments: Optional[str] = None



