import json
import google.generativeai as genai
from typing import List, Dict, Any
import logging
import asyncio
from app.config import settings

logger = logging.getLogger(__name__)

# Configure Gemini API
if settings.GEMINI_API_KEY_PRIMARY:
    genai.configure(api_key=settings.GEMINI_API_KEY_PRIMARY)


async def extract_insights(document_text: str) -> Dict[str, Any]:
    """
    Agent 1: Extracts operational insights from document text with citations.
    """
    # Input validation
    if not document_text or len(document_text.strip()) < 10:
        raise ValueError("Document text must be at least 10 characters")
    
    if len(document_text) > 1_000_000:  # 1MB limit
        raise ValueError("Document text exceeds maximum length (1MB)")
    
    if not settings.GEMINI_API_KEY_PRIMARY:
        raise ValueError("GEMINI_API_KEY_PRIMARY not configured")
    
    prompt = f"""
    You are an expert business analyst. Extract non-trivial insights.
    Content: {document_text}   Domain: General Business

    Return JSON:
    {{
      "primary_insight": {{ "headline": "", "evidence": [], "confidence": 0.0, "insight_type": "" }},
      "secondary_insights": [
        {{ "headline": "", "evidence": [], "confidence": 0.0, "insight_type": "" }}
      ],
      "key_metrics": [ {{ "metric": "", "value": "", "direction": "", "period": "" }} ],
      "signals": [ ]
    }}

    Rules: NO generic statements. MUST cite specific numbers/facts.
    Minimum 2, maximum 5 secondary insights.
    """
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                ),
                request_options={"timeout": 30}
            )
            
            result = json.loads(response.text)
            
            # Validate response schema
            if "primary_insight" not in result:
                raise ValueError("Response missing 'primary_insight' field")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Attempt {attempt + 1}: Failed to parse insights JSON: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                raise ValueError(f"Failed to parse agent response after {max_retries} attempts: {e}")
        except genai.types.GenAIError as e:
            logger.error(f"Attempt {attempt + 1}: Gemini API error: {e}")
            if hasattr(e, 'status_code'):
                if e.status_code == 429:  # Rate limit
                    await asyncio.sleep(10)
                elif e.status_code in [500, 502, 503]:  # Transient errors
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise
            else:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise


async def analyze_impact(insight_dict: dict) -> Dict[str, Any]:
    """
    Agent 2: Quantifies real-world impact and urgency.
    """
    if not isinstance(insight_dict, dict):
        raise ValueError("insight_dict must be a dictionary")
    
    if not settings.GEMINI_API_KEY_PRIMARY:
        raise ValueError("GEMINI_API_KEY_PRIMARY not configured")
    
    prompt = f"""
    You are a strategic impact analyst.
    Insights: {json.dumps(insight_dict)}   Domain: General Business

    Return JSON:
    {{
      "impact_summary": "string",
      "immediate_impacts": [{{"area": "string", "impact": "string", "severity": "string", "timeframe": "string", "quantified_estimate": "string"}}],
      "cascading_effects": [],
      "urgency_score": 0,
      "probability_score": 0,
      "magnitude_score": 0,
      "affected_areas": [],
      "risk_if_ignored": "string"
    }}
    Be specific. Use metrics from insights. No vague language.
    """
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                ),
                request_options={"timeout": 30}
            )
            
            result = json.loads(response.text)
            result["insight_id"] = insight_dict.get("id", "unknown")
            
            # Validate required fields
            if "impact_summary" not in result:
                raise ValueError("Response missing 'impact_summary' field")
            if "urgency_score" not in result:
                result["urgency_score"] = 5  # Default score
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Attempt {attempt + 1}: Failed to parse impact JSON: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                raise ValueError(f"Failed to parse agent response after {max_retries} attempts: {e}")
        except genai.types.GenAIError as e:
            logger.error(f"Attempt {attempt + 1}: Gemini API error: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                raise


async def generate_actions(impact_dict: dict, insight_dict: dict) -> List[Dict[str, Any]]:
    """
    Agent 3: Generates executable actions based on the impact.
    """
    if not isinstance(impact_dict, dict) or not isinstance(insight_dict, dict):
        raise ValueError("impact_dict and insight_dict must be dictionaries")
    
    if not settings.GEMINI_API_KEY_PRIMARY:
        raise ValueError("GEMINI_API_KEY_PRIMARY not configured")
    
    prompt = f"""
    You are a strategic decision agent. Generate 3 ranked executable actions.
    Impact: {json.dumps(impact_dict)}
    Available systems: [CRM, Email, Pricing Engine, Dashboard, Notifications]

    Return JSON with recommended_actions[]:
    {{
      "recommended_actions": [
        {{
          "rank": 1,
          "title": "string",
          "description": "string",
          "action_type": "string",
          "category": "string",
          "target_system": "string",
          "effort": "string",
          "parameters": {{}},
          "expected_outcome": "string",
          "time_to_impact": "string"
        }}
      ]
    }}

    Action #1 MUST be realistic and implementable.
    """
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.5
                ),
                request_options={"timeout": 30}
            )
            
            result = json.loads(response.text)
            
            # Validate response
            if "recommended_actions" not in result:
                raise ValueError("Response missing 'recommended_actions' field")
            
            if not isinstance(result["recommended_actions"], list) or len(result["recommended_actions"]) == 0:
                raise ValueError("recommended_actions must be a non-empty list")
            
            return result.get("recommended_actions", [])
            
        except json.JSONDecodeError as e:
            logger.error(f"Attempt {attempt + 1}: Failed to parse actions JSON: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                raise ValueError(f"Failed to parse agent response after {max_retries} attempts: {e}")
        except genai.types.GenAIError as e:
            logger.error(f"Attempt {attempt + 1}: Gemini API error: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                raise
