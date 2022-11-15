from beanie import Document, Indexed, Link
from typing import Optional
from pydantic import List, BaseModel

class Preferences(BaseModel):
    """The user preferences model."""
    campus: Optional[str]
    duration: Optional[int]

class SearchHistory(Document):
    """The user search history model."""
    start_time: int
    end_time: int
    campus: str
    day: str


class User(Document):
    telegram_id = Indexed(int)
    chat_id = Indexed(int)
    first_name = Optional[str]
    last_name = Optional[str]
    username = Optional[str]
    preferences = Optional[Preferences]
    search_history = List[Link[SearchHistory]]