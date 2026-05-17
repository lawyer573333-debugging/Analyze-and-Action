import json
import google.generativeai as genai
from typing import List, Dict, Any, Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Load balancing helper
def get_model(agent_level: int):
    """
    Returns a configured Gemini model based on the agent's level.
    Level 0 & 1 use Secondary Key.
    Level 2 & 3 use Primary Key.
    """
    key = settings.GEMINI_API_KEY_SECONDARY if agent_level <= 1 else settings.GEMINI_API_KEY_PRIMARY
    genai.configure(api_key=key)
    return genai.GenerativeModel('gemini-1.5-pro')

async def verify_trust(report_text: str) -> Dict[str, Any]:
    """
    Agent 0: Trust & Verification (Vulnerability Shield).
    Analyzes reports for spam, fake events (Aliens, Dinosaurs), or unrealistic claims.
    """
    prompt = f"""
    You are the "Urban Trust Sentinel" for a Smart City Management System.
    Your task is to verify if a citizen report is REAL or SPAM/FAKE.

    Report: "{report_text}"

    CRITICAL RULES:
    1. Language Credibility: Does it sound like a real person reporting a city issue?
    2. Realism: UFOs, Aliens, Dinosaurs, Magic, or Curses are 100% FAKE.
    3. Logical Consistency: Can this happen in a modern city?

    Return JSON ONLY:
    {{
      "trust_score": float (0.0 to 100.0),
      "is_verified": boolean,
      "classification": "Real" | "Spam" | "Fake" | "Joke",
      "reasoning": "Brief explanation of why this score was given",
      "flagged_keywords": []
    }}

    Examples:
    - "Major accident near Faisal Chowk" -> Trust: 95%, Real
    - "Aliens landed at metro station" -> Trust: 2%, Fake
    - "Dinosaur blocking highway" -> Trust: 5%, Joke
    """

    model = get_model(0)
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.0
        )
    )

    try:
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Agent 0 parsing error: {e}")
        return {"trust_score": 0.0, "is_verified": False, "classification": "Error"}

async def process_urban_data(report_text: str) -> Dict[str, Any]:
    """
    Agent 1: Urban Data Processor (Content Understanding).
    Extracts key facts and signals from verified reports.
    """
    prompt = f"""
    You are an "Urban Data Analyst". Extract key facts from this verified city report.
    Report: "{report_text}"

    Return JSON ONLY:
    {{
      "incident_type": "string",
      "location": "string",
      "severity": "Low" | "Medium" | "High" | "Critical",
      "timestamp_estimate": "string",
      "key_signals": ["list", "of", "facts"],
      "entities_involved": ["cars", "people", "utility", "etc"]
    }}
    """

    model = get_model(1)
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
        logger.error(f"Agent 1 parsing error: {e}")
        return {}

async def analyze_urban_impact(facts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent 2: Insight & Impact Analyst.
    Explains why the insight matters and connects to real-world consequences.
    """
    prompt = f"""
    You are a "City Impact Strategist". Analyze the consequences of this urban incident.
    Facts: {json.dumps(facts)}

    Think about: Cascading traffic failures, emergency response delays, economic loss, and public safety.

    Return JSON ONLY:
    {{
      "impact_headline": "string",
      "consequences": [
        {{ "area": "Traffic", "description": "string", "severity": "string" }},
        {{ "area": "Safety", "description": "string", "severity": "string" }}
      ],
      "cascading_risk": "What happens if NOT addressed in 30 minutes?",
      "urgency_index": 0-10,
      "stakeholders_to_notify": ["Police", "Ambulance", "Public", "etc"]
    }}
    """

    model = get_model(2)
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.2
        )
    )

    try:
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Agent 2 parsing error: {e}")
        return {}

async def orchestrate_urban_action(impact: Dict[str, Any], facts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent 3: Action Orchestrator.
    Generates actionable recommendations and prepares for simulation/routing.
    """
    prompt = f"""
    You are the "City Action Controller". Generate 3 realistic, actionable recommendations.
    Facts: {json.dumps(facts)}
    Impact: {json.dumps(impact)}

    IMPORTANT: One action MUST be a "Rerouting Plan" compatible with a navigation engine.

    Return JSON ONLY:
    {{
      "primary_action": {{
        "title": "string",
        "type": "Reroute" | "Dispatch" | "Alert",
        "description": "string",
        "target_system": "rescue-road-engine",
        "parameters": {{
            "affected_road": "string",
            "suggested_alternate": "string",
            "closure_level": "Partial" | "Full"
        }}
      }},
      "secondary_actions": [],
      "notification_message": "Draft SMS for citizens",
      "simulation_trigger": "string (e.g. Trigger Dispatch Mock)"
    }}
    """

    model = get_model(3)
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
        logger.error(f"Agent 3 parsing error: {e}")
        return {}
