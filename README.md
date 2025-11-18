# ICICI Prudential AMC FAQ Assistant - Data Extraction

This project implements a data extraction system for ICICI Prudential AMC fund information from Groww website, following a **precompute architecture** where data is scraped, validated, and stored with source URLs.

## Architecture

The system follows a modular architecture:

```
┌─────────────────┐
│  Web Scraper    │ → Groww Website
│  (scraper.py)   │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Data Validator │ → Validate extracted data
│  (validator.py) │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Data Storage   │ → JSON storage with source URLs
│  (storage.py)   │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Main Script    │ → Orchestrates the pipeline
│  (main.py)      │
└─────────────────┘
```

## Features

- **Data Extraction**: Scrapes fund data from Groww website
- **Data Points Extracted**:
  - Expense Ratio
  - Exit Load
  - Minimum SIP
  - Lock-in Period (ELSS)
  - Riskometer
  - Benchmark
  - Statement Download Information
- **Validation**: Validates all extracted data for correctness
- **Source URL Tracking**: Every data point includes its source URL
- **Structured Storage**: Data stored in JSON format for easy retrieval

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Gemini API key:
```bash
python setup_api_key.py
```
Or manually create `.env` file with:
```
GEMINI_API_KEY=your_api_key_here
```

## Usage

### Basic Usage

Run the main script to scrape both funds:

```bash
python main.py
```

### Custom URLs

You can also provide custom URLs as command line arguments:

```bash
python main.py https://groww.in/mutual-funds/icici-prudential-large-cap-fund-direct-growth
```

### Individual Components

#### Test Scraper Only

```bash
python scraper.py
```

#### Test Validator Only

```bash
python data_validator.py
```

#### Test Storage Only

```bash
python data_storage.py
```

## Data Structure

### Fund Data Format

```json
{
  "fund_id": "abc123def456",
  "fund_name": "ICICI Prudential Large Cap Fund Direct Growth",
  "source_url": "https://groww.in/mutual-funds/icici-prudential-large-cap-fund-direct-growth",
  "scraped_at": "2024-01-15 10:30:00",
  "last_updated": "2024-01-15T10:30:00",
  "expense_ratio": {
    "value": 0.85,
    "unit": "%",
    "display": "0.85%"
  },
  "exit_load": {
    "value": 1.0,
    "unit": "%",
    "period": "1",
    "display": "1% if redeemed within 1 year"
  },
  "minimum_sip": {
    "value": 100,
    "unit": "INR",
    "display": "₹100"
  },
  "lock_in": {
    "value": 3,
    "unit": "years",
    "display": "3 years (ELSS)",
    "is_elss": true
  },
  "riskometer": {
    "value": "very high",
    "display": "Very High"
  },
  "benchmark": {
    "value": "NIFTY 100 Total Return Index",
    "display": "NIFTY 100 Total Return Index"
  },
  "statement_download": {
    "available": true,
    "instructions": ["Statements can be downloaded from..."],
    "display": "Available - Check fund house website or registrar portal"
  }
}
```

## Storage

Data is stored in the `data/` directory:

- `data/funds_data.json` - All fund data
- `data/metadata.json` - Storage metadata
- `data/rag_data.json` - Data formatted for RAG pipeline
- `data/scraping_results.json` - Scraping session results

## Validation

The validator checks:

- ✅ URL format and domain (must be groww.in)
- ✅ Expense ratio (0-10% range)
- ✅ Exit load (0-5% range)
- ✅ Minimum SIP (₹100-₹100,000 range)
- ✅ Lock-in period (0-10 years)
- ✅ Riskometer (valid risk levels)
- ✅ Benchmark (contains index keywords)
- ✅ Statement download info

## Source URL Validation

All URLs are validated to ensure:
- They are from `groww.in` domain
- They use proper HTTP/HTTPS protocol
- They are well-formed

## Notes

- The scraper uses BeautifulSoup for HTML parsing
- Data is stored with timestamps for tracking updates
- Each fund gets a unique ID based on its URL
- The system can handle updates to existing funds

## Backend API (FAQ Assistant)

The backend implements a complete RAG (Retrieval-Augmented Generation) pipeline using Gemini 2.0 Flash.

### Backend Components

- **Gemini Client** (`gemini_client.py`) - Integration with Gemini 2.0 Flash model
- **Vector Store** (`vector_store.py`) - FAISS-based semantic search
- **RAG Pipeline** (`rag_pipeline.py`) - Combines retrieval and generation
- **FastAPI Backend** (`api.py`) - REST API endpoints

### Backend Setup

1. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

2. **Extract fund data (if not done):**
   ```bash
   python main.py
   ```

3. **Setup backend:**
   ```bash
   python setup_backend.py
   ```

4. **(Optional) Warm up embedding model** – run this once (locally or during build) so Render doesn’t re-download 70 MB of weights on each boot:
   ```bash
   python warm_embedding_model.py
   ```
   This caches `sentence-transformers/paraphrase-MiniLM-L3-v2` under `~/.cache/huggingface`.

5. **Start API server:**
   ```bash
   python api.py
   # Or (dev): uvicorn api:app --reload
   # Or (deploy on Render/Heroku): uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}
   ```

### Render Deployment Tips

Add the warm-up script to your Render build command so the model downloads during build rather than first request:

```
pip install -r requirements.txt && python warm_embedding_model.py
```

Keep `data/` checked into git so the service boots with a ready-made FAISS index. After deployment you can verify everything with:

```
curl https://<your-service>.onrender.com/health
curl "https://<your-service>.onrender.com/query?q=What%20is%20the%20rating"
```

### API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /query` - Answer FAQ query (JSON body)
- `GET /query?q=...` - Answer FAQ query (GET method)
- `GET /funds` - List available funds
- `POST /rebuild-index` - Rebuild vector store index

### Example API Usage

```bash
# POST request
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the expense ratio?", "fund_name": "ICICI Prudential Large Cap Fund"}'

# GET request
curl "http://localhost:8000/query?q=What%20is%20the%20minimum%20SIP?"
```

### API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Future Enhancements

- Scheduled updates (cron job / task scheduler)
- Web interface for querying data
- Advanced filtering and search

## License

This project is for educational purposes.

