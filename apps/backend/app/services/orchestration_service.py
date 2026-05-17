import httpx
import asyncio
import json
import logging
from app.config import settings
from app.agents.ingestion import extract_text_from_document
from app.agents.gemini_agents import extract_insights, analyze_impact, generate_actions
from app.agents.simulation import simulate_execution
from app.services.websocket_manager import manager

logger = logging.getLogger(__name__)

class VertexAIOrchestratorService:
    def __init__(self):
        self.base_url = f"https://{settings.VERTEX_LOCATION}-aiplatform.googleapis.com/v1"
        self.project_id = settings.GCP_PROJECT_ID
        self.agent_id = settings.VERTEX_AGENT_ID
    
    async def run_pipeline(self, document) -> dict:
        """Orchestrates the 5-agent pipeline: Ingestion -> Insights -> Impact -> Action -> Simulation"""
        pipeline_results = {
            "document_id": document.id,
            "filename": document.filename,
            "stages": [],
            "simulation": None,
            "status": "Success",
            "error": None
        }
        
        # Track and limit Gemini API calls for safety and cost control
        import google.generativeai as genai
        original_generate = genai.GenerativeModel.generate_content
        api_calls = 0
        max_api_calls = 4
        
        def limited_generate(self, *args, **kwargs):
            nonlocal api_calls
            if api_calls >= max_api_calls:
                raise RuntimeError(f"Gemini API call limit reached (maximum {max_api_calls} calls allowed). Execution terminated.")
            api_calls += 1
            logger.info(f"Gemini API Call #{api_calls} initiated for model: {self.model_name}")
            return original_generate(self, *args, **kwargs)
            
        try:
            logger.info(f"Starting pipeline for document {document.id}")
            genai.configure(api_key=settings.GEMINI_API_KEY_PRIMARY)
            
            # Apply cost-control shield monkeypatch
            genai.GenerativeModel.generate_content = limited_generate
            
            await manager.broadcast({"stage": "started", "message": "Initializing multi-agent pipeline..."}, document.id)
            await asyncio.sleep(0.5)

            # Stage 1: Ingestion
            logger.info("Pipeline Stage: Ingestion")
            await manager.broadcast({"stage": "ingestion", "message": "Ingesting and normalising document..."}, document.id)
            source_val = document.storage_path or document.source_url or document.filename
            text = await extract_text_from_document(document.id, source_val, document.source_type)
            pipeline_results["stages"].append({"stage": "Ingestion", "status": "Success"})
            await asyncio.sleep(0.5)

            # Stage 2: Insights Extraction
            logger.info("Pipeline Stage: Insights")
            await manager.broadcast({"stage": "insights", "message": "Extracting operational insights..."}, document.id)
            insights = await extract_insights(text)
            pipeline_results["stages"].append({"stage": "Insights", "data": insights})
            await asyncio.sleep(0.5)

            # Stage 3: Impact Analysis & Actions Generation
            logger.info("Pipeline Stage: Impact & Action Analysis")
            await manager.broadcast({"stage": "analysis", "message": "Analysing strategic impact & ranking actions..."}, document.id)
            
            # Extract a dictionary representing primary insight
            primary_insight = {}
            if isinstance(insights, dict):
                primary_insight = insights.get("primary_insight", insights)
            elif isinstance(insights, list) and insights:
                primary_insight = insights[0]

            impact = await analyze_impact(primary_insight)
            pipeline_results["stages"].append({"stage": "Impact", "data": impact})
            
            actions = await generate_actions(impact, primary_insight)
            pipeline_results["stages"].append({"stage": "Actions", "data": actions})
            await asyncio.sleep(0.5)

            # Stage 4: Simulation Execution
            recommended_actions = []
            if isinstance(actions, dict):
                recommended_actions = actions.get("recommended_actions", [])
            elif isinstance(actions, list):
                recommended_actions = actions

            if recommended_actions:
                primary_action = recommended_actions[0]
                
                # Normalize action_dict for ActionItem Pydantic model
                normalized_action = dict(primary_action)
                if "title" not in normalized_action and "action_title" in normalized_action:
                    normalized_action["title"] = normalized_action["action_title"]
                if "description" not in normalized_action:
                    normalized_action["description"] = normalized_action.get("expected_outcome", "") or normalized_action.get("action_type", "No description provided.")
                if "parameters" not in normalized_action or not isinstance(normalized_action["parameters"], dict):
                    normalized_action["parameters"] = {}
                
                logger.info(f"Pipeline Stage: Simulation for {normalized_action.get('title')}")
                sim_res = await simulate_execution(normalized_action, primary_insight.get("insight", "General Business"))
                pipeline_results["simulation"] = sim_res
            
            # Broadcast Completed
            await manager.broadcast({
                "stage": "completed", 
                "message": "Analysis successfully completed!",
                "results_count": len(insights.get("secondary_insights", [])) + 1 if isinstance(insights, dict) else 1
            }, document.id)

        except Exception as e:
            logger.error(f"Pipeline failed for document {document.id}: {e}")
            pipeline_results["status"] = "Failed"
            pipeline_results["error"] = str(e)
            await manager.broadcast({"stage": "completed", "message": f"Pipeline Error: {e}"}, document.id)
            
        finally:
            # Restore original generate_content function
            genai.GenerativeModel.generate_content = original_generate

        return pipeline_results

    async def call_orchestrator(self, input_data: dict, pipeline_stage: str) -> dict:
        """Call Vertex AI orchestrator with specific tool"""
        headers = {
            "Authorization": f"Bearer {await self._get_access_token()}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "displayName": f"pipeline-{pipeline_stage}",
            "userInput": {
                "text": json.dumps(input_data)
            }
        }
        
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/projects/{self.project_id}/agents/{self.agent_id}:run",
                json=payload,
                headers=headers
            )
        
        return response.json()
    
    async def _get_access_token(self) -> str:
        """Get GCP access token for authentication"""
        from google.auth.transport.requests import Request
        from google.oauth2.service_account import Credentials
        
        credentials = Credentials.from_service_account_file(
            settings.GCP_KEY_PATH,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        credentials.refresh(Request())
        return credentials.token

orchestrator = VertexAIOrchestratorService()
