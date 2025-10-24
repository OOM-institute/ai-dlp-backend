from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Request Models
class GeneratePageRequest(BaseModel):
    industry: str = Field(..., min_length=1, max_length=100)
    offer: str = Field(..., min_length=1, max_length=500)
    target_audience: str = Field(..., min_length=1, max_length=200)
    brand_tone: str = Field(..., min_length=1, max_length=200)
    website_url: Optional[str] = None

class EditSectionRequest(BaseModel):
    section_id: str
    data: Dict[str, Any]

class ReorderSectionsRequest(BaseModel):
    sections: List[Dict[str, Any]]

class PublishPageRequest(BaseModel):
    page_id: str

# Response Models
class SectionData(BaseModel):
    id: str
    type: str
    order: int
    data: Dict[str, Any]

class PageSpecResponse(BaseModel):
    pageId: str
    version: int
    sections: List[SectionData]
    user_context: Optional[Dict[str, str]] = None

class PublishResponse(BaseModel):
    page_id: str
    version: int
    url: str
    message: str

# Database Models (MongoDB documents)
class PageDocument(BaseModel):
    page_id: str
    version: int
    sections: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    user_id: Optional[str] = None
    published: bool = False
    # NEW: Store context for regeneration
    user_context: Dict[str, str] = {}
    crawled_context: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "page_id": "landing-001",
                "version": 1,
                "sections": [],
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00",
                "user_id": "user-123",
                "published": False,
                "user_context": {
                    "industry": "SaaS",
                    "offer": "AI tool",
                    "target_audience": "Developers",
                    "brand_tone": "Modern"
                },
                "crawled_context": None
            }
        }