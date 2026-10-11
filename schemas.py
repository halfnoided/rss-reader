from pydantic import BaseModel, ConfigDict
from datetime import datetime

class FeedCreate(BaseModel):
    url: str
    title: str
    
class FeedOut(BaseModel):
    id: int
    url: str
    title: str
    model_config = ConfigDict(from_attributes=True)

class ArticleOut(BaseModel):
    id: int
    feed: FeedOut
    link: str
    title: str
    time_published: datetime | None
    content: str | None
    is_favorite: bool = False
    model_config = ConfigDict(from_attributes=True)
