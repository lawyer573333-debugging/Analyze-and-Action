import asyncio
import json
import os
from dotenv import load_dotenv

# Set up environment
load_dotenv()

# Import the orchestrator and agents
# Note: We need to set the python path or run from correct dir
# For this test, let's mock the settings or ensure they are loaded
from app.services.urban_orchestrator import urban_orchestrator

async def run_test_cases():
    test_cases = [
        {
            "name": "REAL: Faisal Chowk Accident",
            "text": "Major accident near Faisal Chowk signal. Two cars collided and traffic is blocked for almost 1 km."
        },
        {
            "name": "FAKE: Alien Invasion",
            "text": "Aliens have landed near the metro station and are controlling traffic lights."
        },
        {
            "name": "REAL: G-10 Flooding",
            "text": "Heavy rain has flooded the underpass near G-10. Several vehicles are stuck and traffic movement is very slow."
        }
    ]

    for case in test_cases:
        print(f"\n{'='*50}")
        print(f"TEST CASE: {case['name']}")
        print(f"INPUT: {case['text']}")
        print(f"{'='*50}")

        results = await urban_orchestrator.run_pipeline(case['text'])

        print(f"FINAL STATUS: {results['final_status']}")

        for stage in results['stages']:
            agent = stage['agent']
            data = stage['data']
            print(f"\n--- {agent} Output ---")
            if agent == "TrustSentinel":
                print(f"Score: {data.get('trust_score')}% | Verified: {data.get('is_verified')} | Class: {data.get('classification')}")
                print(f"Reason: {data.get('reasoning')}")
            elif agent == "DataProcessor":
                print(f"Type: {data.get('incident_type')} | Severity: {data.get('severity')}")
                print(f"Location: {data.get('location')}")
            elif agent == "ImpactAnalyst":
                print(f"Headline: {data.get('impact_headline')}")
                print(f"Urgency: {data.get('urgency_index')}/10")
            elif agent == "ActionController":
                print(f"Primary Action: {data.get('primary_action', {}).get('title')}")
                print(f"SMS: {data.get('notification_message')}")

if __name__ == "__main__":
    asyncio.run(run_test_cases())
