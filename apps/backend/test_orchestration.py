import asyncio
import os
from app.models import Document
from app.services.orchestration_service import orchestrator
import uuid

# Load env vars manually for the test
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY_PRIMARY")
genai.configure(api_key=api_key)

async def test_pipeline():
    print("Starting Antigravity Orchestration Test...")
    
    # Create a mock document
    mock_doc = Document(
        id=str(uuid.uuid4()),
        user_id=str(uuid.uuid4()),
        filename="Operational Analysis Report: Sales conversions have dropped by 18% in the EMEA region due to severe CRM page loading latencies. Customers are abandoning their checkout flows, costing approximately $25k in lost revenue daily. We recommend upgrading the server capacity immediately.",
        content_type="text/plain",
        source_type="text"
    )
    
    # The orchestrator will use the content_path as raw text because source_type="text"
    try:
        result = await orchestrator.run_pipeline(mock_doc)
        print("\nPipeline Completed Successfully!\n")
        
        import json
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"\nPipeline Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_pipeline())
