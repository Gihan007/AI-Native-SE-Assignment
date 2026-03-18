"""Setup Instructions for AIAnalysisService with Groq"""

# QUICK START
# ===========

# 1. Install dependencies (Groq already added to requirements.txt):
#    pip install -r requirements.txt

# 2. Set Groq API key (automatically loaded from .env file):
#    The .env file already contains your API key.
#    Or set environment variable:
#    
#    Windows PowerShell:  $env:GROQ_API_KEY = "gsk_..."
#    Windows CMD:         set GROQ_API_KEY=gsk_...
#    Linux/Mac:           export GROQ_API_KEY="gsk_..."

# 3. Add to your routes.py:

from app.services.ai_analysis_service import AIAnalysisService

@router.post("/audit-with-ai")
async def audit_with_ai(request: AuditRequest):
    """Get metrics + AI insights in one call"""
    try:
        url = str(request.url)
        
        # Step 1: Extract metrics
        metrics = ScraperService.extract_metrics(url)
        
        # Step 2: Generate AI insights using Groq
        ai_service = AIAnalysisService()
        ai_insights = ai_service.generate_insights(metrics)
        
        # Step 3: Return both
        return {
            "metrics": metrics,
            "ai_insights": ai_insights,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 4. Test the endpoint:
#    curl -X POST http://localhost:8000/audit-with-ai \
#      -H "Content-Type: application/json" \
#      -d '{"url": "https://example.com"}'


# WHAT YOU GET
# ============

# The service analyzes using Groq's mixtral-8x7b-32768 model:
# ✓ SEO structure (heading hierarchy, meta tags, content)
# ✓ CTA effectiveness (quantity and placement)
# ✓ Image accessibility (alt text coverage)
# ✓ Internal linking (structure and quantity)
# ✓ Meta tag quality (title and description)
# ✓ Overall page quality score (0-100)
# ✓ Actionable summary with top recommendations

# Response format:
# {
#   "metrics": { ... AuditResponse ... },
#   "ai_insights": {
#     "seo_analysis": "Detailed SEO analysis...",
#     "cta_analysis": "CTA effectiveness...",
#     "image_accessibility": "Alt text quality...",
#     "internal_linking": "Link structure...",
#     "meta_tag_quality": "Meta tags quality...",
#     "overall_score": 82,
#     "summary": "Key findings and recommendations..."
#   }
# }


# KEY FEATURES
# ============

# 1. Open Source LLM
#    - Uses Groq's mixtral-8x7b-32768 model
#    - Free tier with generous API limits
#    - Fast inference speeds

# 2. Non-intrusive
#    - Doesn't modify ScraperService
#    - Works with existing AuditResponse schema
#    - Completely independent service

# 3. Safe AI Integration
#    - Never fabricates metrics
#    - Only analyzes provided factual data
#    - Prompt explicitly prevents hallucination

# 4. Error Handling
#    - Handles API errors gracefully
#    - Returns meaningful error messages
#    - Doesn't crash on LLM failures

# 5. Production Ready
#    - Uses official Groq Python client
#    - Proper logging
#    - Environment variable support
#    - Type hints throughout

# 6. Flexible
#    - Pass custom API key or use .env file
#    - Can be called independently or in pipeline
#    - Easy to extend for other analysis types


# ARCHITECTURE
# ============

"""
User Request
    ↓
FastAPI Route
    ↓
ScraperService.extract_metrics(url)
    ↓ (returns AuditResponse with factual metrics)
    ↓
AIAnalysisService.generate_insights(metrics)
    ↓ (sends factual metrics + content to Groq)
    ↓
Groq API (mixtral-8x7b-32768)
    ↓ (analyzes metrics, returns JSON)
    ↓
AIAnalysisService parses & validates response
    ↓
Combined Response (metrics + insights)
    ↓
User receives actionable audit report
"""
