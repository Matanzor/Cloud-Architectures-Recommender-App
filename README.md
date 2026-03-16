# Cloud Architecture Parsing and Recommendation

A system that scrapes AWS cloud architectures, parses them into structured data, stores in MongoDB, and recommends matches based on user requirements.

## Prerequisites

- Docker and Docker Compose
- (Optional) Git

## Quick Start

```bash
git clone https://github.com/Matanzor/Cloud-Architectures-Recommender-App.git
cd Cloud-Architectures-Recommender-App
docker-compose up --build
```

Wait for all services to start. Then:

- **Frontend:** http://localhost
- **Backend API:** http://localhost:8000

## Setup

1. Build and run:

   ```bash
   docker-compose up --build
   ```

2. MongoDB starts on port 27017. Backend connects to it automatically.
3. Frontend runs on port 80, backend on 8000.
4. On first run, the database is empty. Click "Trigger Scrape" in the UI to load seed data (and optionally scrape AWS pages).

## Architecture

- **Backend (FastAPI):** Python API with endpoints for listing architectures, triggering scrape, and getting recommendations.
- **Database (MongoDB):** Stores architecture documents with resources and metadata.
- **Frontend (React):** Dashboard to list architectures, view details, trigger scrape, and submit requirements for recommendations.

## Flow

1. Scraper loads seed data (10 curated architectures) into MongoDB.
2. Scraper fetches AWS blog pages from five sources (architecture, aws, compute, database).
3. For each live-scraped page: extract resources (EC2, Lambda, S3, etc.) and infer metadata.
4. Data is stored in MongoDB with a `parsed_with` field (seed/AI/rule_based).
5. Recommendation API scores architectures by matching user requirements and returns the best matches.

## Parsing Flow

- **Seed data:** Pre-structured, always loaded first. No parsing. `parsed_with: "seed"`.
- **Live-scraped pages:** Try AI first (if `OPENAI_API_KEY` is set and the call succeeds) → `parsed_with: "ai"`. Otherwise fall back to rule-based keyword mapping → `parsed_with: "rule_based"`.

The UI shows `parsed_with` for each architecture so you can verify which path was used.

## Scraping

- **Sources:** Five AWS blog categories — architecture (main + category), aws, compute, database. Up to 20 posts per list page.
- **Retries:** Each fetch retried up to 3 times with exponential backoff (2s, 4s, 6s).
- **Politeness:** 1.5s delay between requests.

## Design Choices

- **MongoDB:** Document model fits nested architecture data (resources + metadata) without joins. Aligns with assignment spec.
- **Seed data:** Ensures the demo works even if AWS scraping is slow or blocked. Scraper always loads seed first, then optionally scrapes live pages.
- **Parsing:** AI (OpenAI gpt-4o-mini) when `OPENAI_API_KEY` is set, rule-based keyword mapping as fallback. Best of both: AI for nuance, rules for reliability.
- **Weighted scoring:** use_case and availability_requirement weighted higher in recommendations.

## Trade-offs

- Scraping: AWS pages can be dynamic; seed data is the fallback.
- Parsing: AI improves nuance, rule-based fallback when no API key.
- Recommendation: Simple scoring; interpretable for interviews.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /architectures | List architectures |
| GET | /architectures/{id} | Get architecture detail |
| POST | /architectures/scrape | Trigger scrape (background) |
| POST | /recommend | Get recommendations (JSON body with 9 required fields) |

## Run Without Docker

```bash
# Terminal 1: MongoDB (or use Docker for MongoDB only)
mongod

# Terminal 2: Backend
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload

# Terminal 3: Frontend
cd frontend && npm install && npm run dev
```

Set `MONGODB_URI=mongodb://localhost:27017` for backend. Frontend dev server proxies /api to backend.

## Testing with AI Parsing

When `OPENAI_API_KEY` is set, the parser uses OpenAI (gpt-4o-mini) to infer metadata from scraped text. Otherwise it falls back to rule-based parsing.

**With Docker:**

1. Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=sk-your-openai-api-key
   ```
2. Run `docker-compose up --build`
3. Click "Trigger Scrape" — live-scraped pages will use AI for metadata extraction

**Without Docker:**

```bash
export OPENAI_API_KEY=sk-your-openai-api-key
cd backend && uvicorn app.main:app --reload
```

Then trigger a scrape. Seed data is pre-structured and does not use AI, only newly scraped pages from AWS are parsed with AI.
