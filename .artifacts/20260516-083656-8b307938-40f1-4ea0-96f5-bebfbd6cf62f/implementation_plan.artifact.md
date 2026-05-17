# Implementation Plan - Smart City Urban Management Engine

This plan transforms the current project into a futuristic **Smart City Urban Management System**. It will process unstructured urban data (traffic, weather, complaints) and simulate real-time emergency and infrastructure responses.

## User Review Required
- **Map Integration:** For the "Outcome Visualization," do you have a preferred Map provider (Google Maps, Leaflet, or a simple custom vector map)?
- **Simulation Type:** I've planned for a "Traffic Rerouting" and "Emergency Dispatch" simulation. Does this cover your needs for the "Action Simulation" requirement?

## Proposed Changes

### 1. Backend: Smart City Agentic Pipeline (`apps/backend`)
We will implement a multi-agent workflow using structured reasoning.

- **Agent 1: Urban Sentinel (Content Understanding):** Extracts signals from traffic reports, news, and sensors.
- **Agent 2: Insight Engine (Impact Analysis):** Analyzes how weather + accidents + complaints create "Cascading Failures."
- **Agent 3: City Controller (Action & Simulation):** Generates rerouting plans and triggers mock API calls to emergency services.

#### [NEW] `apps/backend/app/agents/urban_agents.py`
- Definition of the three agents and their handoff logic.

#### [NEW] `apps/backend/app/services/simulation_service.py`
- Handles the mock execution:
    - `trigger_rerouting()`: Updates a mock traffic database.
    - `dispatch_emergency()`: Simulates an API call to a 911/Dispatch system.
    - `notify_citizens()`: Generates SMS/App notification logs.

### 2. Frontend: Futuristic Urban Dashboard (`apps/frontend-mobile`)
The UI will be updated from a generic dashboard to a "City Control Center."

#### `lib/screens/dashboard_screen.dart`
- Update UI to show "City Pulse" (Real-time signal feed).
- Implement the **Outcome Visualization** component (Before vs After state of a city sector).
- Add a "Pipeline Trace" view to show Agent reasoning.

#### `lib/widgets/map_visualization.dart`
- A custom widget to show "Active Incidents" and "Simulated Reroutes."

## Verification Plan

### Automated Tests
- `pytest apps/backend/tests/test_urban_pipeline.py`: Verifies that a "Heavy Rain + Accident" input results in a "Rerouting Action."
- `pytest apps/backend/tests/test_simulation.py`: Verifies the mock API calls are triggered.

### Manual Verification
- **Step 1:** Upload a text file containing: *"Accident on 5th Ave, heavy congestion, ambulance delayed by flooding."*
- **Step 2:** Observe the "Pipeline Pipeline" in the app showing Agent 1 -> Agent 2 -> Agent 3.
- **Step 3:** Verify the "Action Simulation" log shows: `[SIMULATION] Rerouting 5th Ave traffic to Broadway... SUCCESS.`
- **Step 4:** Check the "Outcome Visualization" to see the "Before" (Red congestion) vs "After" (Green flow) state.
