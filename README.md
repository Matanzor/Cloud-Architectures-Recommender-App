# Cloud Architecture Parsing and Recommendation

A system that scrapes AWS cloud architectures, parses them into structured data, stores in MongoDB, and recommends matches based on user requirements.

## Prerequisites

- Docker and Docker Compose
- (Optional) Git

## Quick Start

```bash
git clone <https://github.com/Matanzor/Cloud-Architectures-Recommender-App.git>
cd sol
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

1. Scraper fetches AWS Architecture Blog pages (or uses seed data if scraping fails).
2. Parser extracts AWS resources (EC2, Lambda, S3, etc.) and infers metadata from text.
3. Data is stored in MongoDB.
4. Recommendation API scores architectures by matching user requirements (use case, scale, traffic_pattern, etc.) and returns the best matches.

## Design Choices

- **MongoDB:** Document model fits nested architecture data (resources + metadata) without joins. Aligns with assignment spec.
- **Seed data:** Ensures the demo works even if AWS scraping is slow or blocked. Scraper always loads seed first, then optionally scrapes live pages.
- **Rule-based parsing:** Keyword mapping for metadata inference. No external AI dependency, keeps control and explainability.
- **Weighted scoring:** use_case and availability_requirement weighted higher in recommendations.

## Trade-offs

- Scraping: AWS pages can be dynamic; seed data is the fallback.
- Parsing: Rule-based may miss nuance; could extend with ML later.
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
