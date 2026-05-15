import asyncio
import json
import uuid
from typing import Dict, Any
from app.models.schemas import ActionItem, SimulationResult
import google.generativeai as genai

async def simulate_execution(action_dict: dict, context_insight: str) -> dict:
    """
    Simulates the execution of an action, generating before/after states and logs.
    """
    try:
        # Pydantic validation
        action = ActionItem(**action_dict)
    except Exception as e:
        raise ValueError(f"Invalid ActionItem format: {e}")

    # 1. Staged Execution Delays (Mocking API Latency)
    delay_ms = action.parameters.get("delay_ms", 500)
    await asyncio.sleep(delay_ms / 1000.0)
    
    # 2. Use Gemini to dynamically generate plausible states
    prompt = f"""
    You are a Simulation Engine. Given the following action to execute:
    Title: {action.title}
    Description: {action.description}
    Context: {context_insight}
    
    Generate a JSON response containing:
    1. "before_state": A small JSON object representing the system before execution.
    2. "after_state": A small JSON object representing the system after execution.
    3. "execution_logs": An array of 3-4 strings detailing the simulated execution steps (e.g., "Connecting to webhook...", "Patching database...", "Sending email...").
    If the action involves an email or message, include the drafted text in the logs.
    """
    
    model = genai.GenerativeModel('gemini-1.5-pro')
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
            execution_logs=["Executed fallback simulation (JSON generation failed)."]
        ).model_dump()
