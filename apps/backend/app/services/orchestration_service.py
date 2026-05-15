from app.models.document import Document
from typing import Dict, Any
import logging
import asyncio

# Import the actual Agent tools
from app.agents.ingestion import extract_text_from_document
from app.agents.gemini_agents import extract_insights, analyze_impact, generate_actions
from app.agents.simulation import simulate_execution
from app.services.websocket_manager import manager

logger = logging.getLogger(__name__)

class AntigravityOrchestrator:
    async def run_pipeline(self, document: Document) -> Dict[str, Any]:
        """
        The Antigravity Orchestrator Loop.
        Executes the tools in sequence using the contracts defined in schemas.py.
        """
        logger.info(f"Starting Antigravity orchestration for document {document.id}")
        await manager.broadcast({"stage": "started", "message": "Antigravity Orchestrator initialized"}, document.id)
        
        # 1. Ingestion Agent
        await manager.broadcast({"stage": "ingestion", "message": "Agent 1: Extracting text from document..."}, document.id)
        # Using placeholder file path for now; in a real scenario we'd use the uploaded file path from Google Cloud Storage or local disk
        file_path = f"data/{document.id}.pdf" if document.source_type == "pdf" else "raw text placeholder"
        
        try:
            # For hackathon/testing, if file doesn't exist we'll use a mock text
            input_text = await extract_text_from_document(str(document.id), file_path, document.source_type)
        except Exception as e:
            logger.warning(f"Ingestion failed or file not found, falling back to mock text. Error: {e}")
            input_text = "Operational efficiency in the logistics department has dropped by 15% due to legacy routing software. Furthermore, server costs have spiked by $10k this month."
        
        # 2. Insight Extraction Agent
        await manager.broadcast({"stage": "insights", "message": "Agent 2: Extracting non-trivial insights with Gemini Pro..."}, document.id)
        insights = await extract_insights(input_text)
        await manager.broadcast({"stage": "insights", "message": f"Agent 2 Found {len(insights)} insights."}, document.id)
        
        # 3 & 4. Parallel fan-out for Impact and Action Generation
        await manager.broadcast({"stage": "analysis", "message": "Agents 3 & 4: Analyzing impact and generating actions..."}, document.id)
        
        final_results = []
        for insight in insights:
            # Agent 3: Impact
            impact = await analyze_impact(insight)
            
            # Agent 4: Action
            actions = []
            # Check urgency score guardrail
            urgency = impact.get("urgency_score", 0)
            if urgency >= 30:
                actions = await generate_actions(impact, insight)
            else:
                logger.info(f"Insight {insight.get('id')} urgency {urgency} < 30. Skipping Action Generation.")
            
            # Agent 5: Simulation (execute the top ranked action)
            simulations = []
            if actions:
                top_action = sorted(actions, key=lambda x: x.get("rank", 99))[0]
                await manager.broadcast({"stage": "analysis", "message": f"Agent 5: Simulating execution for action: {top_action.get('title')}"}, document.id)
                sim_result = await simulate_execution(top_action, insight.get('insight', ''))
                simulations.append(sim_result)
                
            final_results.append({
                "insight": insight,
                "impact": impact,
                "actions": actions,
                "simulations": simulations
            })
            
        logger.info(f"Antigravity Pipeline completed for document {document.id}")
        await manager.broadcast({"stage": "completed", "message": "Orchestration finished successfully", "results_count": len(final_results)}, document.id)
        return {"document_id": str(document.id), "results": final_results}

orchestrator = AntigravityOrchestrator()
