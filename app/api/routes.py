"""API routes for the application."""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status
from app.schemas.audit_schema import AuditRequest, AuditResponse, ErrorResponse, CombinedAuditResponse
from app.services.scraper_service import ScraperService
from app.services.ai_analysis_service import AIAnalysisService

router = APIRouter()


@router.post(
    "/audit",
    response_model=CombinedAuditResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid URL or request"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def audit_website(request: AuditRequest) -> CombinedAuditResponse:
    """
    Audit a website, extract metrics, and generate AI insights.
    
    Fetches the website, parses HTML, extracts metrics, and uses Groq AI to generate insights.
    
    Returns:
    - Metrics: Word count, headings, CTAs, links, images, meta tags, content preview
    - AI Insights: SEO analysis, CTA effectiveness, image accessibility, internal linking,
                   meta tag quality, overall score, actionable summary, and prioritized recommendations
    
    Args:
        request: AuditRequest containing the URL to audit
        
    Returns:
        CombinedAuditResponse with metrics and ai_insights
        
    Raises:
        HTTPException: If URL is invalid or inaccessible
    """
    try:
        # Convert Pydantic HttpUrl to string
        url = str(request.url)
        
        # Step 1: Extract metrics
        metrics = ScraperService.extract_metrics(url)
        
        # Step 2: Generate AI insights using Groq
        ai_service = AIAnalysisService()
        ai_insights = ai_service.generate_insights(metrics)
        
        # Step 3: Return combined response (clean API response)
        return CombinedAuditResponse(
            metrics=metrics,
            ai_insights=ai_insights,
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        Status information
    """
    return {"status": "healthy", "message": "API is running"}
