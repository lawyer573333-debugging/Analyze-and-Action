# Insight-to-Action Engine

An enterprise-grade AI platform that transforms raw user inputs (PDFs, URLs, text) into actionable business recommendations through a sophisticated multi-agent pipeline.

## Project Structure

This is a monorepo containing:
- `apps/backend`: FastAPI application orchestrating the Vertex AI agents.
- `apps/frontend-web`: Next.js web application.
- `apps/frontend-mobile`: Flutter mobile application.
- `packages/`: Shared schemas, utilities, and API clients.
- `infra/`: Terraform, Kubernetes, and Docker configuration.

## Setup

1. Copy `.env.example` to `.env` in the relevant directories.
2. Run `docker-compose up -d` to start local services (Postgres, Redis).
3. Start the backend: `npm run dev:backend`.
4. Start the frontend: `npm run dev:frontend`.
