# User Prompt Template for Website Audit Analysis

Analyze the following website audit metrics.

## Important Guidelines

- Use ONLY the provided metrics and content preview.
- Do NOT fabricate facts.
- Be specific, grounded, and cautious.
- If a metric may be inflated by raw DOM structure, mention that possibility briefly.
- Treat CTA count as "CTA-like elements detected" rather than perfect human-classified CTAs.
- Treat missing alt text carefully: some images may be decorative, so do not insist every image needs descriptive alt text.
- Keep each section concise but useful.

## Scoring Rubric (0-100 total)

- SEO structure and headings: 25 points
- CTA clarity and conversion focus: 20 points
- Image accessibility: 20 points
- Internal linking: 15 points
- Meta tag quality: 20 points

## Factual Metrics

{METRICS_JSON}

## Content Preview

{CONTENT_PREVIEW}

## Expected Response Structure

Return ONLY a valid JSON object in this exact structure:

```json
{
  "seo_analysis": "2-4 sentences grounded in the metrics.",
  "cta_analysis": "2-4 sentences grounded in the metrics.",
  "image_accessibility": "2-4 sentences grounded in the metrics.",
  "internal_linking": "2-4 sentences grounded in the metrics.",
  "meta_tag_quality": "2-4 sentences grounded in the metrics.",
  "overall_score": 0,
  "summary": "A concise executive summary with the most important findings.",
  "top_recommendations": [
    {
      "priority": 1,
      "recommendation": "Specific, actionable recommendation text.",
      "reasoning": "Clear reasoning tied directly to extracted metric(s)."
    },
    {
      "priority": 2,
      "recommendation": "Specific, actionable recommendation text.",
      "reasoning": "Clear reasoning tied directly to extracted metric(s)."
    },
    {
      "priority": 3,
      "recommendation": "Specific, actionable recommendation text.",
      "reasoning": "Clear reasoning tied directly to extracted metric(s)."
    }
  ]
}
```

## Guidance for Recommendations

- Provide 3-5 prioritized recommendations (priority: 1, 2, 3, ...).
- Each recommendation must be specific and actionable (e.g., "Add alt text to informational images" not "improve accessibility").
- Each recommendation must have clear reasoning that cites the actual metrics (e.g., "7 of 12 images lack alt text").
- Avoid generic or vague advice.
- Recommendations should prioritize high-impact issues that tie directly to the metrics provided.
- Keep recommendation text concise (1-2 sentences).

## Analysis Guidance

- **For SEO structure**: Comment on heading counts, word count, and whether duplicate H1s may be due to rendering.
- **For CTAs**: Comment on whether the page appears action-oriented and whether CTA density may create focus or noise.
- **For images**: Comment on alt coverage and explicitly note that decorative images may not need descriptive alt text.
- **For internal linking**: Comment on whether the page appears well-connected internally.
- **For meta tags**: Assess title length, description length, and clarity.
- **Recommendations must be actionable and directly tied to metrics.**
