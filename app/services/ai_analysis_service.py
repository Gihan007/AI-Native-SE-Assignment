"""AI Analysis Service for website audit insights using Groq."""

import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from groq import Groq, APIError, APIConnectionError, RateLimitError

from app.schemas.audit_schema import AuditResponse
from app.core.config import AUDIT_LOG_FILE

logger = logging.getLogger(__name__)


class AIAnalysisService:
    """Service for generating AI-powered audit insights."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AIAnalysisService with Groq client.

        Args:
            api_key: Groq API key. If None, uses GROQ_API_KEY env var.

        Raises:
            ValueError: If no API key is provided and GROQ_API_KEY is not set.
        """
        api_key = api_key or os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "Groq API key not provided. "
                "Set GROQ_API_KEY environment variable or pass api_key parameter."
            )

        self.client = Groq(api_key=api_key)
        self.model = "openai/gpt-oss-120b"
        self.temperature = 0.2
        # Leave room for full structured JSON output on long pages.
        self.max_tokens = 2200
        
        # Set up prompts directory path
        service_dir = Path(__file__).parent
        self.prompts_dir = service_dir.parent / "prompts"

    def generate_insights(self, audit: AuditResponse) -> Dict[str, Any]:
        """
        Generate AI insights based on extracted audit metrics.

        Args:
            audit: AuditResponse schema with extracted website metrics.

        Returns:
            Dictionary with structured JSON analysis including:
            - seo_analysis
            - cta_analysis
            - image_accessibility
            - internal_linking
            - meta_tag_quality
            - overall_score
            - summary
            - top_recommendations
            - error (optional)
        """
        system_prompt = self._get_system_prompt()
        metrics_payload = self._format_metrics_for_prompt(audit)
        user_prompt = self._build_analysis_prompt(metrics_payload, audit.content)
        raw_response = None
        error_details = None
        
        try:
            raw_response = self._request_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=self.temperature,
            )

            try:
                analysis = self._parse_response(raw_response)
            except json.JSONDecodeError as first_parse_error:
                logger.warning(
                    "Initial AI response was invalid JSON for %s. Retrying with strict JSON mode.",
                    audit.url,
                )
                strict_user_prompt = (
                    user_prompt
                    + "\n\nCRITICAL: Return ONLY valid JSON. Do not include markdown, explanation, "
                    + "or any text outside the JSON object."
                )
                raw_response = self._request_completion(
                    system_prompt=system_prompt,
                    user_prompt=strict_user_prompt,
                    temperature=0.0,
                    response_format={"type": "json_object"},
                )
                try:
                    analysis = self._parse_response(raw_response)
                except json.JSONDecodeError:
                    # Preserve the first parse error details, which are usually the most useful.
                    raise first_parse_error

            # Log successful interaction
            self._log_ai_interaction(
                url=audit.url,
                metrics=metrics_payload,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                raw_response=raw_response,
                parsed_response=analysis,
            )

            logger.info("AI analysis completed for %s", audit.url)
            return analysis

        except (APIError, APIConnectionError, RateLimitError) as e:
            error_details = str(e)
            logger.error("Groq API error while analyzing %s: %s", audit.url, error_details)
            
            # Log failed interaction
            self._log_ai_interaction(
                url=audit.url,
                metrics=metrics_payload,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                raw_response=raw_response,
                error=error_details,
            )
            
            return self._error_response(
                error="AI analysis failed",
                details=error_details,
                summary="Analysis could not be completed because the AI provider returned an error.",
            )
        except json.JSONDecodeError as e:
            error_details = str(e)
            logger.error("Failed to parse AI response for %s: %s", audit.url, error_details)
            
            # Log failed interaction with raw response for debugging
            self._log_ai_interaction(
                url=audit.url,
                metrics=metrics_payload,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                raw_response=raw_response,
                error=f"JSON parsing error: {error_details}",
            )
            
            return self._error_response(
                error="Failed to parse AI response",
                details=error_details,
                summary="The AI returned output that was not valid JSON.",
            )
        except Exception as e:
            error_details = str(e)
            logger.error("Unexpected error during AI analysis for %s: %s", audit.url, error_details)
            
            # Log failed interaction
            self._log_ai_interaction(
                url=audit.url,
                metrics=metrics_payload,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                raw_response=raw_response,
                error=error_details,
            )
            
            return self._error_response(
                error="Unexpected error during analysis",
                details=error_details,
                summary="An unexpected error occurred during analysis.",
            )

    def _request_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        response_format: Optional[Dict[str, str]] = None,
    ) -> str:
        """Request a completion from Groq and return message content."""
        request_payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "temperature": temperature,
            "max_tokens": self.max_tokens,
        }

        if response_format is not None:
            request_payload["response_format"] = response_format

        response = self.client.chat.completions.create(**request_payload)
        return response.choices[0].message.content or ""

    def _get_system_prompt(self) -> str:
        """Load the system prompt from file."""
        system_prompt_file = self.prompts_dir / "system_prompt.md"
        
        if not system_prompt_file.exists():
            logger.warning("System prompt file not found at %s", system_prompt_file)
            # Fallback to inline prompt
            return (
                "You are a senior website auditor specializing in SEO, UX, accessibility, "
                "content structure, and conversion optimization.\n\n"
                "You are given factual metrics extracted from a webpage. "
                "You must analyze ONLY the provided metrics and content preview.\n\n"
                "Critical rules:\n"
                "1. NEVER invent or assume metrics that are not provided.\n"
                "2. Be cautious when interpreting raw DOM counts.\n"
                "3. Multiple H1s may sometimes result from duplicated rendering or hidden DOM structure; "
                "do not overstate the issue without caution.\n"
                "4. Missing alt text may include decorative images; recommend reviewing informative vs decorative images.\n"
                "5. CTA counts represent CTA-like elements detected heuristically; do not claim perfect semantic accuracy.\n"
                "6. Keep recommendations practical, concise, and tied to the provided metrics.\n"
                "7. Recommendations must be specific and actionable (e.g., 'Add alt text to informational images' "
                "not 'improve accessibility').\n"
                "8. Output ONLY valid JSON.\n"
            )
        
        content = system_prompt_file.read_text(encoding="utf-8")
        # Extract text content, removing markdown headers
        lines = []
        for line in content.split("\n"):
            if not line.startswith("#"):
                lines.append(line)
        return "\n".join(lines).strip()

    def _build_analysis_prompt(self, metrics: Dict[str, Any], content_preview: str) -> str:
        """
        Build the analysis prompt by loading template and replacing placeholders.

        Args:
            metrics: Structured metrics dictionary.
            content_preview: Preview of page content.

        Returns:
            Complete prompt for analysis.
        """
        metrics_json = json.dumps(metrics, indent=2)
        content_preview_truncated = content_preview[:700]
        
        # Load the user prompt template
        user_prompt_file = self.prompts_dir / "user_prompt.md"
        
        if not user_prompt_file.exists():
            logger.warning("User prompt file not found at %s", user_prompt_file)
            # Fall back to inline generation
            return self._build_analysis_prompt_fallback(metrics, content_preview)
        
        template = user_prompt_file.read_text(encoding="utf-8")
        
        # Replace placeholders
        prompt = template.replace("{METRICS_JSON}", metrics_json)
        prompt = prompt.replace("{CONTENT_PREVIEW}", content_preview_truncated)
        
        return prompt
    
    def _build_analysis_prompt_fallback(self, metrics: Dict[str, Any], content_preview: str) -> str:
        """Fallback prompt generation if template file is not found."""
        metrics_json = json.dumps(metrics, indent=2)
        content_preview_truncated = content_preview[:700]

        prompt = (
            "Analyze the following website audit metrics.\n\n"
            "IMPORTANT:\n"
            "- Use ONLY the provided metrics and content preview.\n"
            "- Do NOT fabricate facts.\n"
            "- Be specific, grounded, and cautious.\n"
            "- If a metric may be inflated by raw DOM structure, mention that possibility briefly.\n"
            "- Treat CTA count as \"CTA-like elements detected\" rather than perfect human-classified CTAs.\n"
            "- Treat missing alt text carefully: some images may be decorative, so do not insist every image needs descriptive alt text.\n"
            "- Keep each section concise but useful.\n\n"
            "SCORING RUBRIC (0-100 total):\n"
            "- SEO structure and headings: 25 points\n"
            "- CTA clarity and conversion focus: 20 points\n"
            "- Image accessibility: 20 points\n"
            "- Internal linking: 15 points\n"
            "- Meta tag quality: 20 points\n\n"
            "FACTUAL METRICS:\n"
            + metrics_json + "\n\n"
            "CONTENT PREVIEW:\n"
            + content_preview_truncated + "\n\n"
            "Return ONLY a valid JSON object in this exact structure:\n"
            "{\n"
            "  \"seo_analysis\": \"2-4 sentences grounded in the metrics.\",\n"
            "  \"cta_analysis\": \"2-4 sentences grounded in the metrics.\",\n"
            "  \"image_accessibility\": \"2-4 sentences grounded in the metrics.\",\n"
            "  \"internal_linking\": \"2-4 sentences grounded in the metrics.\",\n"
            "  \"meta_tag_quality\": \"2-4 sentences grounded in the metrics.\",\n"
            "  \"overall_score\": 0,\n"
            "  \"summary\": \"A concise executive summary with the most important findings.\",\n"
            "  \"top_recommendations\": [\n"
            "    {\n"
            "      \"priority\": 1,\n"
            "      \"recommendation\": \"Specific, actionable recommendation text.\",\n"
            "      \"reasoning\": \"Clear reasoning tied directly to extracted metric(s).\"\n"
            "    },\n"
            "    {\n"
            "      \"priority\": 2,\n"
            "      \"recommendation\": \"Specific, actionable recommendation text.\",\n"
            "      \"reasoning\": \"Clear reasoning tied directly to extracted metric(s).\"\n"
            "    },\n"
            "    {\n"
            "      \"priority\": 3,\n"
            "      \"recommendation\": \"Specific, actionable recommendation text.\",\n"
            "      \"reasoning\": \"Clear reasoning tied directly to extracted metric(s).\"\n"
            "    }\n"
            "  ]\n"
            "}\n\n"
            "Guidance for recommendations:\n"
            "- Provide 3-5 prioritized recommendations (priority: 1, 2, 3, ...).\n"
            "- Each recommendation must be specific and actionable (e.g., \"Add alt text to informational images\" not \"improve accessibility\").\n"
            "- Each recommendation must have clear reasoning that cites the actual metrics (e.g., \"7 of 12 images lack alt text\").\n"
            "- Avoid generic or vague advice.\n"
            "- Recommendations should prioritize high-impact issues that tie directly to the metrics provided.\n"
            "- Keep recommendation text concise (1-2 sentences).\n\n"
            "Guidance for better analysis:\n"
            "- For SEO structure, comment on heading counts, word count, and whether duplicate H1s may be due to rendering.\n"
            "- For CTAs, comment on whether the page appears action-oriented and whether CTA density may create focus or noise.\n"
            "- For images, comment on alt coverage and explicitly note that decorative images may not need descriptive alt text.\n"
            "- For internal linking, comment on whether the page appears well-connected internally.\n"
            "- For meta tags, assess title length, description length, and clarity.\n"
            "- Recommendations must be actionable and directly tied to metrics.\n"
        )
        return prompt

    def _format_metrics_for_prompt(self, audit: AuditResponse) -> Dict[str, Any]:
        """
        Format audit metrics into a structured dictionary for the prompt.

        Args:
            audit: AuditResponse with extracted metrics.

        Returns:
            Structured dictionary of metrics.
        """
        title = audit.meta.title or ""
        description = audit.meta.description or ""
        total_links = audit.links.internal + audit.links.external

        metrics = {
            "url": audit.url,
            "word_count": audit.word_count,
            "headings": {
                "h1_count": audit.headings.h1,
                "h2_count": audit.headings.h2,
                "h3_count": audit.headings.h3,
                "note": (
                    "Heading counts are raw DOM counts and may include duplicated "
                    "rendered or hidden elements on some modern websites."
                ),
            },
            "cta_like_elements": {
                "count": audit.cta_count,
                "note": (
                    "CTA count is heuristic and may include repeated or UI-adjacent action elements."
                ),
            },
            "links": {
                "internal": audit.links.internal,
                "external": audit.links.external,
                "total": total_links,
            },
            "images": {
                "total": audit.images.total,
                "missing_alt": audit.images.missing_alt,
                "missing_alt_percent": round(audit.images.missing_alt_percent, 2),
                "with_alt_percent": round(100 - audit.images.missing_alt_percent, 2),
                "note": (
                    "Some images may be decorative, so missing alt text should be reviewed "
                    "for meaning-bearing images first."
                ),
            },
            "meta_tags": {
                "title": title,
                "title_length": len(title),
                "description": description,
                "description_length": len(description),
            },
        }

        return metrics

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse JSON response from Groq.

        Args:
            response_text: Raw text response from Groq.

        Returns:
            Parsed JSON dictionary.

        Raises:
            json.JSONDecodeError: If response doesn't contain valid JSON.
        """
        cleaned = self._extract_json_text(response_text)
        parsed = json.loads(cleaned)

        required_fields = [
            "seo_analysis",
            "cta_analysis",
            "image_accessibility",
            "internal_linking",
            "meta_tag_quality",
            "overall_score",
            "summary",
            "top_recommendations",
        ]

        for field in required_fields:
            if field not in parsed:
                if field == "top_recommendations":
                    parsed[field] = []
                elif field == "overall_score":
                    parsed[field] = 0
                else:
                    parsed[field] = ""

        if not isinstance(parsed["top_recommendations"], list):
            parsed["top_recommendations"] = []

        # Normalize recommendations to structured format
        normalized_recommendations = []
        for idx, item in enumerate(parsed["top_recommendations"][:5], 1):
            normalized_item = self._normalize_recommendation(item, idx)
            if normalized_item:
                normalized_recommendations.append(normalized_item)

        parsed["top_recommendations"] = normalized_recommendations

        # Normalize score
        if isinstance(parsed.get("overall_score"), (int, float)):
            parsed["overall_score"] = min(100, max(0, int(parsed["overall_score"])))
        else:
            parsed["overall_score"] = 0

        # Normalize text fields
        for key in [
            "seo_analysis",
            "cta_analysis",
            "image_accessibility",
            "internal_linking",
            "meta_tag_quality",
            "summary",
        ]:
            parsed[key] = str(parsed.get(key, "")).strip()

        return parsed

    def _normalize_recommendation(self, item: Any, priority: int) -> Optional[dict]:
        """
        Normalize a single recommendation item to structured format.

        Handles both dict (already structured) and string (fallback) formats.

        Args:
            item: Recommendation item from model output (dict or string).
            priority: Priority level (1-5).

        Returns:
            Normalized recommendation dict or None if invalid.
        """
        if isinstance(item, dict):
            # Already structured - validate and normalize
            rec = str(item.get("recommendation", "")).strip()
            reasoning = str(item.get("reasoning", "")).strip()
            if rec and reasoning:
                return {
                    "priority": int(item.get("priority", priority)),
                    "recommendation": rec,
                    "reasoning": reasoning,
                }
        elif isinstance(item, str):
            # Fallback: string recommendation without reasoning
            rec = item.strip()
            if rec:
                return {
                    "priority": priority,
                    "recommendation": rec,
                    "reasoning": "(Reasoning not provided.)",
                }
        
        return None

    def _extract_json_text(self, response_text: str) -> str:
        """
        Extract JSON text from raw model output.

        Supports:
        - plain JSON
        - ```json fenced blocks
        - extra leading/trailing text

        Args:
            response_text: Raw model output.

        Returns:
            JSON substring.

        Raises:
            json.JSONDecodeError: If no valid JSON object can be isolated.
        """
        text = response_text.strip()

        # Remove fenced code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]

        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        # If the full text is already JSON, return it
        if text.startswith("{") and text.endswith("}"):
            return text

        # Fallback: extract first JSON object
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if match:
            return match.group(0).strip()

        raise json.JSONDecodeError("No valid JSON object found in AI response", text, 0)

    def _error_response(self, error: str, details: str, summary: str) -> Dict[str, Any]:
        """
        Build a consistent error response.

        Args:
            error: Error type.
            details: Error details.
            summary: Summary message.

        Returns:
            Standardized error response.
        """
        return {
            "error": error,
            "details": details,
            "seo_analysis": "",
            "cta_analysis": "",
            "image_accessibility": "",
            "internal_linking": "",
            "meta_tag_quality": "",
            "overall_score": 0,
            "summary": summary,
            "top_recommendations": [],
        }

    def _ensure_log_directory(self) -> None:
        """
        Ensure the logs directory exists.
        
        Creates the directory if it doesn't already exist.
        Silently handles any errors to prevent breaking the API.
        """
        try:
            log_dir = Path(AUDIT_LOG_FILE).parent
            log_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning("Could not create log directory: %s", str(e))

    def _log_ai_interaction(self, url: str, metrics: Dict[str, Any], 
                           system_prompt: str, user_prompt: str,
                           raw_response: Optional[str] = None,
                           parsed_response: Optional[Dict[str, Any]] = None,
                           error: Optional[str] = None) -> None:
        """
        Log AI interaction to JSONL file for auditing and debugging.
        
        Args:
            url: Audited URL
            metrics: Factual metrics sent to AI
            system_prompt: System prompt used
            user_prompt: User prompt used
            raw_response: Raw response from AI model
            parsed_response: Parsed analysis after normalization
            error: Error message if the interaction failed
        """
        try:
            self._ensure_log_directory()
            
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "url": url,
                "metrics": metrics,
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "raw_response": raw_response,
                "parsed_response": parsed_response,
                "error": error,
            }
            
            # Append as JSONL (one JSON object per line)
            with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
                
        except Exception as e:
            logger.warning("Failed to log AI interaction: %s", str(e))


def create_ai_service(api_key: Optional[str] = None) -> AIAnalysisService:
    """
    Factory function to create AIAnalysisService instance.

    Args:
        api_key: Optional Groq API key.

    Returns:
        Configured AIAnalysisService instance.

    Raises:
        ValueError: If no API key is available.
    """
    return AIAnalysisService(api_key=api_key)
