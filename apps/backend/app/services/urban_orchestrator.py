import logging
import asyncio
from typing import Dict, Any, List
from app.services.simulation_service import simulation_service
from app.agents.urban_agents import (
    verify_trust,
    process_urban_data,
    analyze_urban_impact,
    orchestrate_urban_action
)

logger = logging.getLogger(__name__)

class UrbanOrchestratorService:
    """
    Orchestrates the 4-agent Smart City pipeline:
    Trust -> Process -> Impact -> Action -> Simulation
    """

    async def run_pipeline(self, report_text: str) -> Dict[str, Any]:
        pipeline_results = {
            "input": report_text,
            "stages": [],
            "simulation": None,
            "final_status": "Success",
            "error": None
        }

        try:
            # Stage 0: Trust & Verification
            logger.info("Starting Stage 0: Trust Verification")
            trust_data = await verify_trust(report_text)
            pipeline_results["stages"].append({"agent": "TrustSentinel", "data": trust_data})

            if not trust_data.get("is_verified", False):
                pipeline_results["final_status"] = "Terminated (Low Trust)"
                return pipeline_results

            # Stage 1: Urban Data Processing
            logger.info("Starting Stage 1: Data Processing")
            facts = await process_urban_data(report_text)
            pipeline_results["stages"].append({"agent": "DataProcessor", "data": facts})

            # Stage 2: Impact Analysis
            logger.info("Starting Stage 2: Impact Analysis")
            impact = await analyze_urban_impact(facts)
            pipeline_results["stages"].append({"agent": "ImpactAnalyst", "data": impact})

            # Stage 3: Action Orchestration
            logger.info("Starting Stage 3: Action Generation")
            actions = await orchestrate_urban_action(impact, facts)
            pipeline_results["stages"].append({"agent": "ActionController", "data": actions})

            # NEW: Trigger Simulation
            primary_action = actions.get("primary_action", {})
            if primary_action:
                logger.info(f"Triggering Simulation for action: {primary_action.get('title')}")
                sim_result = await simulation_service.simulate_action(primary_action)
                pipeline_results["simulation"] = sim_result

        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            pipeline_results["final_status"] = "Error"
            pipeline_results["error"] = str(e)

        return pipeline_results

urban_orchestrator = UrbanOrchestratorService()
