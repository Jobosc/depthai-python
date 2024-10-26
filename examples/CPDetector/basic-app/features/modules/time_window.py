from datetime import datetime

from pydantic import BaseModel


class TimeWindow(BaseModel):
    start: datetime
    end: datetime
