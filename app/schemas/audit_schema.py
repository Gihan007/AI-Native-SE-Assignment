"""Pydantic schemas for request/response validation."""

from typing import Dict, Optional, List, Any
from pydantic import BaseModel, HttpUrl


class AuditRequest(BaseModel):
    """Request schema for website audit."""
    
    url: HttpUrl = HttpUrl("https://example.com")
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com"
            }
        }


class HeadingsSchema(BaseModel):
    """Schema for heading counts."""
    
    h1: int
    h2: int
    h3: int


class LinksSchema(BaseModel):
    """Schema for link counts."""
    
    internal: int
    external: int


class ImagesSchema(BaseModel):
    """Schema for image metrics."""
    
    total: int
    missing_alt: int
    missing_alt_percent: float


class MetaSchema(BaseModel):
    """Schema for meta tags."""
    
    title: str
    description: str


class AuditResponse(BaseModel):
    """Response schema for audit results."""
    
    url: str
    word_count: int
    headings: HeadingsSchema
    cta_count: int
    links: LinksSchema
    images: ImagesSchema
    meta: MetaSchema
    content: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com",
                "word_count": 1500,
                "headings": {"h1": 1, "h2": 3, "h3": 5},
                "cta_count": 4,
                "links": {"internal": 12, "external": 5},
                "images": {"total": 8, "missing_alt": 1, "missing_alt_percent": 12.5},
                "meta": {
                    "title": "Example Page Title",
                    "description": "Example page description"
                },
                "content": "First 500 characters of visible text..."
            }
        }


class ErrorResponse(BaseModel):
    """Response schema for errors."""
    
    error: str
    details: Optional[str] = None


class CombinedAuditResponse(BaseModel):
    """Combined response schema for the /audit endpoint."""
    
    metrics: AuditResponse
    ai_insights: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "metrics": {
                    "url": "https://example.com",
                    "word_count": 1500,
                    "headings": {"h1": 1, "h2": 3, "h3": 5},
                    "cta_count": 4,
                    "links": {"internal": 12, "external": 5},
                    "images": {"total": 8, "missing_alt": 1, "missing_alt_percent": 12.5},
                    "meta": {
                        "title": "Example Page Title",
                        "description": "Example page description"
                    },
                    "content": "First 500 characters of visible text..."
                },
                "ai_insights": {
                    "seo_analysis": "Brief analysis of SEO structure...",
                    "cta_analysis": "Brief analysis of CTA effectiveness...",
                    "image_accessibility": "Brief analysis of image alt text coverage...",
                    "internal_linking": "Brief analysis of internal linking...",
                    "meta_tag_quality": "Brief analysis of meta tags...",
                    "overall_score": 72,
                    "summary": "Executive summary with key findings...",
                    "top_recommendations": [
                        {
                            "priority": 1,
                            "recommendation": "Specific actionable recommendation",
                            "reasoning": "Grounded in actual metrics"
                        }
                    ]
                }
            }
        }
