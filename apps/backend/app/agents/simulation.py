import asyncio
import json
import uuid
from typing import Dict, Any
from app.models.schemas import ActionItem, SimulationResult
import google.generativeai as genai

async def simulate_execution(action_dict: dict, context_insight: str) -> dict:
    """
    Simulates the execution of an action, generating before/after states and highly realistic logs.
    """
    try:
        # Pydantic validation
        action = ActionItem(**action_dict)
    except Exception as e:
        raise ValueError(f"Invalid ActionItem format: {e}")

    # 1. Staged Execution Delays (Mocking API Latency)
    delay_ms = action.parameters.get("delay_ms", 500)
    await asyncio.sleep(delay_ms / 1000.0)
    
    # 2. Use Gemini to dynamically generate plausible states and mock integrations
    prompt = f"""
    You are an Enterprise Simulation Engine. Given the following action to execute:
    Title: {action.title}
    Description: {action.description}
    Context: {context_insight}
    
    You must output ONLY a valid JSON object. Do not include markdown formatting.
    
    Generate a JSON response containing:
    1. "before_state": A realistic JSON object representing the system before execution (e.g., ticket_status: "open", server_load: 99%).
    2. "after_state": A realistic JSON object representing the system after execution (e.g., ticket_status: "resolved", server_load: 45%).
    3. "execution_logs": An array of strings detailing the simulated execution steps. 
       CRITICAL: Make these logs look highly realistic. Include things like:
       - "POST https://hooks.slack.com/services/... (200 OK)"
       - "Jira Ticket AUTO-102 created and assigned."
       - If the action involves communication, generate a full, professionally drafted email HTML string inside the logs.
    """
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.7
        )
    )
    
    try:
        sim_data = json.loads(response.text)
        result = SimulationResult(
            action_id=action.id,
            status="success",
            before_state=sim_data.get("before_state", {}),
            after_state=sim_data.get("after_state", {}),
            execution_logs=sim_data.get("execution_logs", ["Simulated execution completed."])
        )
        return result.model_dump()
    except Exception as e:
        # Fallback simulation
        return SimulationResult(
            action_id=action.id,
            status="success_fallback",
            before_state={"status": "pending"},
            after_state={"status": "resolved"},
            execution_logs=[
                "Connecting to internal API...",
                "Executing fallback integration protocol.",
                "Simulated execution completed."
            ]
        ).model_dump()
