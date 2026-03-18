# AI-Powered Website Audit Tool

A clean, well-structured FastAPI application that extracts factual metrics from websites deterministically.

## Features

- **Website Scraping**: Fetch and parse HTML content safely
- **Deterministic Metrics**: Extract factual data without AI bias:
  - Word count
  - Heading counts (H1, H2, H3)
  - CTA detection
  - Link analysis (internal/external)
  - Image metrics (alt text coverage)
  - Meta tags extraction
- **Clean Architecture**: Properly separated concerns (API, Services, Schemas, Utils)
- **Type Safety**: Full type hints with Pydantic validation
- **Error Handling**: Comprehensive error handling with clear messages
- **Professional Code**: Docstrings, modular design, beginner-friendly

## Project Structure

```
app/
├── main.py                  # FastAPI entry point
├── api/
│   └── routes.py           # API endpoints
├── core/
│   └── config.py           # Configuration constants
├── services/
│   └── scraper_service.py  # Scraping and metrics logic
├── schemas/
│   └── audit_schema.py     # Pydantic models
└── utils/
    └── html_utils.py       # Helper functions
```

## Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST /audit

Audit a website and extract metrics.

**Request**:
```json
{
  "url": "https://example.com"
}
```

**Response**:
```json
{
  "url": "https://example.com",
  "word_count": 1500,
  "headings": {
    "h1": 1,
    "h2": 3,
    "h3": 5
  },
  "cta_count": 4,
  "links": {
    "internal": 12,
    "external": 5
  },
  "images": {
    "total": 8,
    "missing_alt": 1,
    "missing_alt_percent": 12.5
  },
  "meta": {
    "title": "Example Page Title",
    "description": "Example page description"
  },
  "content": "First 500 characters of visible text..."
}
```

### GET /health

Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

## Metrics Explained

### Word Count
- Visible text only (removes scripts, styles, etc.)
- Whitespace normalized
- Words split safely

### Headings
- Separate counts for H1, H2, H3
- Case-insensitive

### CTA Detection
- Includes all `<button>` elements
- Detects `<a>` tags with keywords:
  - contact, buy, book, call, start, get started
  - sign up, signup, register, learn more
  - request demo, try now

### Link Analysis
- **Internal**: Same domain, relative URLs
- **External**: Different domains
- Ignores: empty href, "#", javascript:, mailto:, tel:

### Image Metrics
- **Total**: All `<img>` tags
- **Missing Alt**: No alt attribute or empty alt
- **Percentage**: Missing / Total * 100

### Meta Tags
- **Title**: `<title>` tag
- **Description**: `<meta name="description">`

## Architecture Rules

✅ **API Layer** → Handles HTTP requests/responses only  
✅ **Services Layer** → Contains business logic  
✅ **Schemas** → Pydantic models for validation  
✅ **Utils** → Reusable helper functions  
✅ **Core** → Configuration constants  

✅ **No mixing** of concerns  
✅ **Type hints** throughout  
✅ **Error handling** at each layer  

## Error Handling

- **Invalid URLs**: 400 Bad Request
- **Timeouts**: Clear timeout error message
- **Network errors**: Clear connection error message
- **Parse errors**: Clear parsing error message
- **Server errors**: 500 Internal Server Error with details

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Stack

- **FastAPI**: Modern web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **BeautifulSoup**: HTML parsing
- **Requests**: HTTP client

## Future Enhancements

- AI layer for semantic analysis
- Prompt logging and tracing
- Batch processing
- Caching layer
- Database integration
- Authentication
- Rate limiting

**GET** `/api/health` - Health check
**GET** `/api/prompt-logs` - Retrieve prompt history
**POST** `/api/clear-logs` - Clear logs
**GET** `/api/logs-summary` - Log statistics
**GET** `/` - API info

## 🎨 User Interface

The web interface provides:
- **Metrics Tab**: Visual display of all factual data
- **Insights Tab**: AI-generated analysis with scores
- **Recommendations Tab**: Priority-sorted actionable items
- **Logs Tab**: Complete prompt and response history

## 📝 Configuration

Create a `.env` file with:
```
OPENAI_API_KEY=sk-...              # Your OpenAI API key
API_HOST=0.0.0.0                   # API host
API_PORT=8000                      # API port
DEBUG=False                        # Debug mode
ENV=development                    # Environment
```

## 🤖 AI Design Decisions

### Model Choice: GPT-4 Turbo
- Strong reasoning and domain knowledge
- Better at grounding insights in data
- Reliable JSON output parsing
- Good cost-performance balance

### Two-Stage Analysis
1. **Stage 1**: Comprehensive analysis (metrics, content)
2. **Stage 2**: Focused recommendations generation
- Separates analysis concerns
- Allows for independent prompt optimization

### Grounding Strategy
- Always reference specific metrics
- Reject vague observations
- Link every recommendation to data
- Maintain separation between facts and insights

## ⚖️ Trade-offs & Design Choices

### Single-Page Analysis Only
- **Choice**: Analyze one page only
- **Reasoning**: Keeps solution focused and fast
- **Trade-off**: Limited understanding of full site structure

### Lightweight Over Feature-Complete
- **Choice**: Core features only
- **Reasoning**: Fast delivery, evaluates core competencies
- **Trade-off**: Not production-ready as-is

### Structured Prompts
- **Choice**: Pre-designed prompts in code
- **Reasoning**: Shows design thinking, quality control
- **Trade-off**: Less flexibility for different use cases

## 🚀 Future Improvements

With more time, I would:

1. **Enhanced Analysis**
   - Multi-page crawling and site structure analysis
   - Competitive benchmarking
   - Historical audit tracking
   - Custom industry benchmarks

2. **Smarter AI**
   - Fine-tuned prompts per page type
   - Multi-model approach
   - Chain-of-thought reasoning
   - Fact verification

3. **Better UX**
   - Real-time analysis progress
   - Interactive metric explorer
   - Custom report generation (PDF/DOCX)
   - Team collaboration features

4. **Production Features**
   - Rate limiting and throttling
   - User authentication
   - Result caching
   - Email report delivery
   - Webhook notifications

5. **Performance**
   - Async batch processing
   - Redis caching
   - CDN deployment
   - Parallel AI processing

## 📦 Dependencies

- **FastAPI** 0.104.1 - Fast, modern web framework
- **Uvicorn** 0.24.0 - ASGI server
- **requests** 2.31.0 - HTTP client
- **BeautifulSoup4** 4.12.2 - HTML parsing
- **OpenAI** 1.3.0 - AI model API
- **pydantic** 2.5.0 - Data validation
- **python-dotenv** 1.0.0 - Environment management
- **pytest** 7.4.3 - Testing framework

## 🧪 Testing

Run tests with:
```bash
pytest backend/tests/
```

Sample URLs for testing:
- https://www.example.com
- https://www.github.com
- https://www.nonprofit.org

## 📄 License

See LICENSE file for details.

## 👨‍💻 Author

Built for EIGHT25MEDIA AI-Native Software Engineer Assignment (March 2026)
