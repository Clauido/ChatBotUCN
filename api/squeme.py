from pydantic import BaseModel
from typing import List

class HistoryItem(BaseModel):
    query: str
    answer: str

class WebSocketMessage(BaseModel):
    query: str
    history: List[HistoryItem]

class BodyGenerate(BaseModel):
    query: str
    history: List[HistoryItem]