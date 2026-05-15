import json
import google.generativeai as genai
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

async def extract_insights(document_text: str) -> List[Dict[str, Any]]:
    """
    Agent 1: Extracts operational insights from document text with citations.
    """
    prompt = f"""
    You are an elite Enterprise Operations Extraction Engine. Your goal is to extract non-trivial, highly specific operational insights from the following text.
    You must output ONLY a valid JSON array of 'InsightResult' objects.
    
    CRITICAL INSTRUCTIONS:
    1. Focus aggressively on bottlenecks, critical compliance risks, or financial/resource leaks. Ignore trivial details.
    2. Extract exactly 2-3 key insights.
    3. For EVERY insight, you MUST quote the exact text in the 'evidence' array. If you cannot find exact evidence, do not extract it.
    4. Category must be strictly one of: "Risk", "Opportunity", "Inefficiency", "Compliance".
    
    Output Schema (List of Objects):
    [{{
      "id": "uuid-string",
      "insight": "string",
      "category": "enum",
      "confidence": 0.9,
      "evidence": [{{"citation": "exact string", "page_number": null}}]
    }}]
    
    Document Text:
    {document_text}
    """
    
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.1
        )
    )
    
    try:
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Failed to parse insights JSON: {e}")
        return []

async def analyze_impact(insight_dict: dict) -> Dict[str, Any]:
    """
    Agent 2: Quantifies real-world impact and urgency.
    """
    prompt = f"""
    You are an Impact Analysis Agent. Quantify the real-world impact of the following insight.
    You must output ONLY a valid JSON object of 'ImpactResult'.
    
    Requirements:
    1. Score impact and urgency from 0-100.
    2. If the text does not contain enough data to quantify, return urgency_score: 0 and do not invent metrics.
    
    Output Schema:
    {{
      "insight_id": "string",
      "impact_score": int,
      "urgency_score": int,
      "quantified_impact": {{"metric": "string", "projected_value": float}} // Optional
    }}
    
    Insight:
    {json.dumps(insight_dict)}
    """
    
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.1
        )
    )
    
    try:
        res = json.loads(response.text)
        res["insight_id"] = insight_dict.get("id", "unknown")
        return res
    except Exception as e:
        logger.error(f"Failed to parse impact JSON: {e}")
        return {}

async def generate_actions(impact_dict: dict, insight_dict: dict) -> List[Dict[str, Any]]:
    """
    Agent 3: Generates executable actions based on the impact.
    """
    prompt = f"""
    You are an Enterprise Action Generation Agent. Based on the insight and its quantified impact, generate exactly 3 ranked executable actions.
    You must output ONLY a valid JSON array of 'ActionItem' objects.
    
    CRITICAL INSTRUCTIONS:
    1. Rank from 1 (highest priority) to 3.
    2. Actions MUST be highly specific, operational, and immediately executable by an automated system.
    3. Generate the precise parameters required for our Simulation Engine to execute this (e.g., webhook_url, delay_ms, Jira_project_key, Slack_channel, email_recipient).
    
    Output Schema:
    [{{
      "id": "uuid-string",
      "rank": int,
      "title": "string",
      "description": "string",
      "parameters": {{"key": "value"}}
    }}]
    
    Insight:
    {json.dumps(insight_dict)}
    
    Impact:
    {json.dumps(impact_dict)}
    """
    
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.5
        )
    )
    
    try:
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Failed to parse actions JSON: {e}")
        return []
