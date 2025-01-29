from pydantic import BaseModel
from typing import List
from langchain_core.output_parsers import BaseOutputParser

class HistoryItem(BaseModel):
    query: str
    answer: str

class WebSocketMessage(BaseModel):
    query: str
    history: List[HistoryItem]

class BodyGenerate(BaseModel):
    query: str
    history: List[HistoryItem]

class LineListOutputParser(BaseOutputParser[List[str]]):
    """Output parser for a list of lines."""

    def parse(self, text: str) -> List[str]:
        lines = text.strip().split("\n")
        return list(filter(None, lines))  # Remove empty lines
