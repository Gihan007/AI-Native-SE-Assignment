# 🔍 AI-Powered Website Audit Tool

A production-ready **FastAPI microservice** that combines deterministic website metrics extraction with **AI-driven analysis** using Groq's `openai/gpt-oss-120b` model to generate actionable, metric-grounded website audit recommendations.

**Key Capabilities:**
- 📊 Extract 10+ deterministic metrics from any website
- 🤖 Generate AI-powered audit insights with prioritized recommendations
- 📝 Comprehensive JSONL logging of all AI interactions for compliance and debugging
- 🔒 Type-safe request/response validation with Pydantic
- ⚡ Fast, async-ready architecture
- 🧩 Clean, modular codebase with full documentation

---

## 📋 Table of Contents

1. [Features](#features)
2. [Requirements](#requirements)
3. [Quick Start](#quick-start)
4. [Detailed Setup](#detailed-setup)
5. [Configuration](#configuration)
6. [API Endpoints](#api-endpoints)
7. [Audit Metrics Guide](#audit-metrics-guide)
8. [AI Analysis & Logging](#ai-analysis--logging)
9. [Project Structure](#project-structure)
10. [Testing](#testing)
11. [Troubleshooting](#troubleshooting)
12. [Development](#development)
13. [License](#license)

---

## ✨ Features

### Core Capabilities

#### 1. **Deterministic Metrics Extraction**
- **Word Count** - Total visible text content
- **Heading Analysis** - H1, H2, H3 counts (raw DOM)
- **CTA Detection** - Heuristic detection of call-to-action elements
- **Link Analysis** - Internal vs external link breakdown
- **Image Metrics** - Total images, missing alt text percentage, accessibility score
- **Meta Tags** - Title, description, and metadata lengths
- **Content Preview** - First 500 characters of visible text for AI context

#### 2. **AI-Powered Analysis** (via Groq LLM)
- **Multi-Section Analysis**
  - SEO structure and heading hierarchy
  - CTA clarity and conversion focus
  - Image accessibility coverage
  - Internal linking strategy
  - Meta tag quality

- **Metric-Grounded Scoring**
  - Overall audit score (0-100)
  - Executive summary with key findings
  - 3-5 prioritized recommendations with specific reasoning

- **Flexible Prompts**
  - System and user prompts stored in `app/prompts/` as markdown files
  - Easy to customize without modifying code
  - Template-based with dynamic metric insertion

#### 3. **Structured Logging**
- **JSONL Format** - One audit interaction per line
- **Complete Record** - URL, metrics, prompts, AI response, errors (if any)
- **Timestamps** - ISO 8601 UTC for all entries
- **Audit Trail** - Full compliance-ready history of all AI interactions

### Non-Functional Features
- ✅ Full type hints with Pydantic v2.5.0
- ✅ Comprehensive error handling with fallback strategies
- ✅ Async-ready for high concurrency
- ✅ Modular architecture (services, schemas, utils)
- ✅ Production-ready logging
- ✅ Graceful timeout handling

---

## 📦 Requirements

### System Requirements
- **Python**: 3.9+
- **OS**: Windows, macOS, Linux
- **RAM**: 512MB+ (recommended: 1GB+)
- **Internet**: Required for website scraping and Groq API calls

### External Dependencies
- **Groq API Key** - [Get free key here](https://console.groq.com)
- (Optional) **Beautiful Soup 4** - Included in requirements

### Python Dependencies
```
groq>=0.5.0              # Groq LLM client
pydantic==2.5.0          # Request/response validation
fastapi>=0.104.0         # Web framework
uvicorn>=0.24.0          # ASGI server
beautifulsoup4>=4.12.0   # HTML parsing
requests>=2.31.0         # HTTP client
python-dotenv>=1.0.0     # Environment variable management
```

---

## 🚀 Quick Start

### 1. Clone & Setup Virtual Environment

```bash
# Navigate to project directory
cd AI-Native-SE-Assignment

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get your free Groq API key from [console.groq.com](https://console.groq.com)

### 4. Run the Application

```bash
python -m uvicorn app.main:app --reload
```

**Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### 5. Test the API

**Via cURL**:
```bash
curl -X POST http://localhost:8000/audit \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.apple.com/mac/"}'
```

**Via Python Requests**:
```python
import requests

response = requests.post(
    "http://localhost:8000/audit",
    json={"url": "https://www.apple.com/mac/"}
)
print(response.json())
```

---

## 🔧 Detailed Setup

### Step 1: Verify Python Installation

```bash
python --version
# Output: Python 3.9.* or higher
```

### Step 2: Clone Repository

```bash
git clone https://github.com/yourusername/AI-Native-SE-Assignment.git
cd AI-Native-SE-Assignment
```

### Step 3: Create & Activate Virtual Environment

**Windows**:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Upgrade pip

```bash
python -m pip install --upgrade pip
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

**Verify installation**:
```bash
pip list
# Should show: groq, pydantic, fastapi, uvicorn, beautifulsoup4, requests, python-dotenv
```

### Step 6: Set Up Environment Variables

Create `.env` file:

```env
# Groq API Configuration
GROQ_API_KEY=gsk_your_key_here

# Optional: Server Configuration
API_HOST=127.0.0.1
API_PORT=8000
```

**Get Groq API Key**:
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Create a new API key
4. Copy the key to `.env`

### Step 7: Create Logs Directory

```bash
mkdir logs
```

*(This is created automatically on first audit, but creating it manually ensures proper permissions)*

### Step 8: Run the Server

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Optional parameters**:
- `--reload` - Auto-restart on code changes (dev only)
- `--host 0.0.0.0` - Listen on all network interfaces
- `--port 8000` - Custom port
- `--workers 4` - Multiple worker processes (production)

### Step 9: Verify Server is Running

Visit `http://localhost:8000/health` in your browser or:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | ✅ Yes | - | Your Groq API key from [console.groq.com](https://console.groq.com) |
| `API_HOST` | ❌ No | `127.0.0.1` | Server bind address |
| `API_PORT` | ❌ No | `8000` | Server port |

### Application Settings (in `app/core/config.py`)

```python
# AI Model Configuration
MODEL = "openai/gpt-oss-120b"    # Groq model name
TEMPERATURE = 0.2               # Response creativity (0=deterministic, 1=creative)
MAX_TOKENS = 1400              # Maximum response length

# HTTP Configuration
REQUEST_TIMEOUT = 10            # Seconds to wait for website response
DEFAULT_USER_AGENT = "Mozilla/5.0..."   # Browser user agent for scraping

# Logging Configuration
AUDIT_LOG_FILE = "logs/audit_logs.jsonl"  # Path to audit log

# CTA Detection
CTA_KEYWORDS = {"contact", "buy", "book", "call", "start", "get started", "sign up", ...}

# HTML noise removal
NOISY_ELEMENTS = {"script", "style", "noscript", "svg", "canvas", "video", ...}
```

### Modifying Prompts

Edit prompt templates without restarting the server:

- **System Prompt**: `app/prompts/system_prompt.md`
- **User Prompt**: `app/prompts/user_prompt.md`

Changes take effect on the next audit request.

---

## 📡 API Endpoints

### 1. POST `/audit`

**Perform a website audit with AI analysis.**

#### Request

```json
{
  "url": "https://example.com"
}
```

#### Response (Success - 200)

```json
{
  "metrics": {
    "url": "https://www.apple.com/mac/",
    "word_count": 1744,
    "headings": {
      "h1": 1,
      "h2": 9,
      "h3": 54
    },
    "cta_count": 42,
    "links": {
      "internal": 196,
      "external": 9
    },
    "images": {
      "total": 68,
      "missing_alt": 31,
      "missing_alt_percent": 45.59
    },
    "meta": {
      "title": "Mac - Apple",
      "description": "The most powerful Mac laptops and desktops ever. Supercharged by Apple silicon. MacBook Neo, MacBook Air, MacBook Pro, iMac, Mac mini, Mac Studio, and Mac Pro."
    },
    "content": "Mac - Apple Apple Store Mac iPad iPhone Watch Vision AirPods TV & Home Entertainment Accessories Support 0 + Buy Mac with education savings. * Shop Mac MacBook Neo New MacBook Air New MacBook Pro New iMac Mac mini Mac Studio Mac Pro Compare Help Me Choose Displays New Accessories Shop Mac Tahoe Explore the lineup. All products Laptops Desktops Displays New MacBook Neo silver blush citrus indigo The magic of Mac at a surprising price. Learn more Buy New MacBook Air 13\" and 15\" sky blue silver sta..."
  },
  "ai_insights": {
    "seo_analysis": "The page has a single H1, which aligns with best practices, and a healthy word count of 1,744 words. The presence of 9 H2s provides good sectional division, but the raw count of 54 H3s may indicate an overly deep or fragmented hierarchy, especially given the note about possible duplicated DOM elements.",
    "cta_analysis": "42 CTA-like elements were detected, showing a strong emphasis on prompting user actions. However, such a high density can dilute focus and potentially overwhelm visitors, making it harder to identify the primary conversion paths.",
    "image_accessibility": "31 of the 68 images (45.6%) lack alt attributes, suggesting many informational images are not described for screen readers. While some images may be decorative, the proportion of missing alt text warrants a focused review.",
    "internal_linking": "196 internal links provide extensive connectivity within the Apple site, supporting SEO and user navigation. The volume is high, so ensuring each link adds clear value will maintain relevance and avoid link fatigue.",
    "meta_tag_quality": "The title \"Mac - Apple\" is concise (11 characters) and brand-focused, though it could be more descriptive. The meta description is 159 characters, fitting the optimal length and effectively summarizing the page content.",
    "overall_score": 69,
    "summary": "The page demonstrates solid SEO fundamentals with good word count and internal linking, but it suffers from excessive CTA density, a high percentage of images missing alt text, and a potentially over-segmented heading structure.",
    "top_recommendations": [
      {
        "priority": 1,
        "recommendation": "Audit all images and add descriptive alt text to any informational images lacking it.",
        "reasoning": "31 images (45.6% of total) are missing alt attributes, which hampers accessibility for screen-reader users."
      },
      {
        "priority": 2,
        "recommendation": "Consolidate and prioritize CTA elements to highlight the most important actions and reduce visual noise.",
        "reasoning": "42 CTA-like elements were detected, which may overwhelm users and dilute the impact of primary conversion calls."
      },
      {
        "priority": 3,
        "recommendation": "Review the heading hierarchy and consider reducing the number of H3s to create clearer content sections.",
        "reasoning": "The raw count of 54 H3 headings suggests possible over-segmentation, which can affect both SEO hierarchy and user readability."
      }
    ]
  }
}
```

#### Response (Error - 4xx/5xx)

```json
{
  "detail": "Failed to fetch website. Connection error: [SSL: CERTIFICATE_VERIFY_FAILED]"
}
```

**Common HTTP Codes**:
- `200` - Success
- `400` - Invalid URL format
- `502` - Website unreachable
- `503` - API rate limited or service unavailable
- `504` - Request timeout

#### Error Handling

The API gracefully handles:
- **Invalid URLs** → Returns 400 with error message
- **Unreachable websites** → Logs and returns 502 with details
- **Groq API failures** → Falls back to structured error response
- **Timeouts** → 10-second default, returns 504 if exceeded

---

### 2. GET `/health`

**Check if the API is running and healthy.**

#### Response

```json
{
  "status": "healthy",
  "message": "API is running"
}
```

### 3. GET `/docs`

**Interactive API documentation** (auto-generated by FastAPI)

Visit `http://localhost:8000/docs` to explore all endpoints with Swagger UI.

### 4. GET `/redoc`

**Alternative API documentation** (ReDoc format)

Visit `http://localhost:8000/redoc`

---

## 📊 Audit Metrics Guide

### Metrics Extracted

#### **Word Count**
- Total visible text content (excluding HTML tags)
- **Use Case**: Assess content depth for SEO

#### **Headings**
- `h1_count` - Top-level headings (should be 1 per page)
- `h2_count` - Section headings
- `h3_count` - Subsection headings
- **Note**: Raw DOM counts may include hidden/duplicated elements
- **Use Case**: Evaluate page structure hierarchy

#### **CTA Detection**
- `cta_count` - Heuristically detected call-to-action elements
- **Note**: Approximation; may include UI elements that aren't true CTAs
- **Use Case**: Assess conversion focus

#### **Links Analysis**
- `internal` - Links to same domain
- `external` - Links to different domains
- **Use Case**: Monitor link distribution and crawlability

#### **Image Metrics**
- `total` - Total images on page
- `missing_alt` - Images without alt attributes
- `missing_alt_percent` - Percentage without alt text
- **Note**: Some images may be decorative
- **Use Case**: Assess accessibility compliance

#### **Meta Tags**
- `title` - Page title
- `description` - Meta description
- Both include length measurements
- **Use Case**: Evaluate SEO metadata

#### **Content Preview**
- First 500 characters of visible text
- **Use Case**: Provides context for AI analysis

---

## 🤖 AI Analysis & Logging

### How AI Analysis Works

1. **Metrics Collected** → Deterministic extraction from website (word count, headings, links, images, etc.)
2. **System Prompt Loaded** → `app/prompts/system_prompt.md` (defines AI auditor role)
3. **User Prompt Built** → Metrics injected into `app/prompts/user_prompt.md` template
4. **Groq API Called** → `openai/gpt-oss-120b` model processes prompts with 0.2 temperature
5. **Response Parsed** → JSON extracted and validated against schema
6. **Logged to JSONL** → Complete interaction recorded to `logs/audit_logs.jsonl`
7. **Returned to Client** → Metrics + AI insights (only 2 fields in response)

### JSONL Logging Format

Each line in `logs/audit_logs.jsonl` is a complete JSON object:

```json
{
  "timestamp": "2026-03-18T21:18:44.715228Z",
  "url": "https://www.apple.com/mac/",
  "metrics": {...},
  "system_prompt": "You are a senior website auditor...",
  "user_prompt": "Analyze the following website audit metrics...",
  "raw_response": "{\"seo_analysis\": \"...\", ...}",
  "parsed_response": {...},
  "error": null
}
```

**Log Entry Fields**:
- `timestamp` - ISO 8601 UTC when audit was performed
- `url` - Website URL audited
- `metrics` - Complete metrics payload sent to AI
- `system_prompt` - Full system prompt used
- `user_prompt` - Full user prompt used
- `raw_response` - Unmodified model output
- `parsed_response` - Validated JSON response
- `error` - Error message (null if successful)

**Viewing Logs**:

```bash
# View recent entries (last 5)
tail -n 5 logs/audit_logs.jsonl

# Pretty print last entry
python -c "import json; print(json.dumps(json.loads(open('logs/audit_logs.jsonl').readlines()[-1]), indent=2))"

# Count total audits
wc -l logs/audit_logs.jsonl
```

---

## 📁 Project Structure

```
AI-Native-SE-Assignment/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── setup.bat                          # Windows setup script
├── .env                               # Environment variables (create this)
├── .gitignore                         # Git ignore rules
│
├── app/
│   ├── __init__.py
│   ├── main.py                        # FastAPI app entry point
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py                  # API endpoint handlers
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py                  # Configuration constants
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── scraper_service.py         # Website metrics extraction
│   │   └── ai_analysis_service.py     # AI-powered analysis & logging
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── audit_schema.py            # Pydantic models (request/response)
│   │
│   ├── prompts/
│   │   ├── system_prompt.md           # AI system prompt
│   │   └── user_prompt.md             # AI user prompt template
│   │
│   └── utils/
│       ├── __init__.py
│       └── html_utils.py              # HTML parsing helpers
│
├── logs/
│   └── audit_logs.jsonl               # Audit trail (auto-created)
│
├── venv/                              # Virtual environment (auto-created)
│
└── QUICK_START_AI.md                  # Quick start guide

```

### Key Files Explained

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app initialization and middleware setup |
| `app/api/routes.py` | `/audit` and `/health` endpoint implementations |
| `app/services/scraper_service.py` | Extracts deterministic metrics from HTML |
| `app/services/ai_analysis_service.py` | Calls Groq API, parses response, logs interactions |
| `app/schemas/audit_schema.py` | Pydantic models for type safety and validation |
| `app/core/config.py` | Configuration constants (model, timeouts, etc.) |
| `app/prompts/*.md` | Configurable AI prompts (no Python restart needed) |

---

## 🧪 Testing

### Unit Tests

#### Test 1: Verify Installation

```bash
python -c "import groq, pydantic, fastapi; print('✓ All dependencies installed')"
```

#### Test 2: Check Environment Configuration

```bash
python -c "import os; print(f'GROQ_API_KEY set: {bool(os.getenv(\"GROQ_API_KEY\"))}')"
```

#### Test 3: Syntax Validation

```bash
python -m py_compile app/services/ai_analysis_service.py
python -m py_compile app/services/scraper_service.py
python -m py_compile app/api/routes.py
```

#### Test 4: Import All Modules

```bash
python -c "from app.main import app; from app.services.scraper_service import ScraperService; from app.services.ai_analysis_service import AIAnalysisService; print('✓ All imports successful')"
```

### Integration Tests

#### Test 5: Health Check Endpoint

```bash
# Start server in one terminal
python -m uvicorn app.main:app --reload

# In another terminal, test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","message":"API is running"}
```

#### Test 6: Full Audit Flow

**Python Script** (`test_audit.py`):

```python
import requests
import json

# Test with a real website
url = "https://www.apple.com/mac/"

response = requests.post(
    "http://localhost:8000/audit",
    json={"url": url},
    timeout=60
)

print(f"Status Code: {response.status_code}")
print(f"Response:\n{json.dumps(response.json(), indent=2)}")

# Verify response structure
data = response.json()
assert "metrics" in data, "Missing 'metrics' in response"
assert "ai_insights" in data, "Missing 'ai_insights' in response"
assert "overall_score" in data["ai_insights"], "Missing 'overall_score'"
assert "top_recommendations" in data["ai_insights"], "Missing recommendations"

print("\n✓ All checks passed!")
```

Run:
```bash
python test_audit.py
```

#### Test 7: Verify Logging

```bash
python -c "
import json

# Read the last log entry
with open('logs/audit_logs.jsonl', 'r') as f:
    lines = f.readlines()
    last_entry = json.loads(lines[-1])
    
print('Last audit logged:')
print(f'  URL: {last_entry[\"url\"]}')
print(f'  Timestamp: {last_entry[\"timestamp\"]}')
print(f'  Status: {\"Success\" if last_entry[\"error\"] is None else \"Error\"}')
print(f'  Score: {last_entry[\"parsed_response\"].get(\"overall_score\", \"N/A\")}')
"
```

#### Test 8: Error Handling

```bash
# Test with invalid URL
curl -X POST http://localhost:8000/audit \
  -H "Content-Type: application/json" \
  -d '{"url": "not-a-valid-url"}'
# Expected: 400 error

# Test with unreachable domain
curl -X POST http://localhost:8000/audit \
  -H "Content-Type: application/json" \
  -d '{"url": "https://this-domain-does-not-exist-12345.com"}'
# Expected: 502 or 504 error
```

---

## 🔧 Troubleshooting

### Problem: `GROQ_API_KEY not found`

**Solution**:
1. Create `.env` file in project root
2. Add: `GROQ_API_KEY=gsk_your_key_here`
3. Restart the server
4. Verify: `python -c "import os; print(os.getenv('GROQ_API_KEY'))"`

### Problem: `ModuleNotFoundError: No module named 'groq'`

**Solution**:
```bash
# Ensure virtual environment is activated
which python  # Should show venv path

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify
pip list | grep groq
```

### Problem: `Connection refused on port 8000`

**Solution**:
```bash
# Check if port is already in use
netstat -an | grep 8000  # Windows: netstat -ano | findstr :8000

# Use different port:
python -m uvicorn app.main:app --port 8001
```

### Problem: `SSL: CERTIFICATE_VERIFY_FAILED` when scraping

**Solution**:
This is normal for some websites. The code includes error handling.
If you need to bypass SSL:
```python
# In scraper_service.py, modify requests call:
response = requests.get(url, timeout=30, verify=False)  # ⚠️ Not recommended for production
```

### Problem: Timeout errors (> 10 seconds)

**Solution**:
- Website is slow or unresponsive
- Increase timeout in `app/core/config.py`:
  ```python
  REQUEST_TIMEOUT = 20  # Increase from 10
  ```

### Problem: `Logs directory doesn't exist`

**Solution**:
```bash
mkdir logs
chmod 755 logs  # macOS/Linux
```

### Problem: High Memory Usage

**Solution**:
- Audit large websites (5MB+ HTML) consume more memory
- Consider running on machine with 2GB+ RAM
- Implement batch processing if handling many audits

---

## 👨‍💻 Development

### Code Style

All code follows:
- **PEP 8** - Python style guide
- **Type Hints** - Full type annotations
- **Docstrings** - Google-style for all functions
- **Error Handling** - Comprehensive try-catch blocks

### Adding New Metrics

To add a new metric:

1. **Update Schema** (`app/schemas/audit_schema.py`):
   ```python
   class AuditResponse(BaseModel):
       # ... existing fields ...
       new_metric: Type = Field(...)
   ```

2. **Extract Metric** (`app/services/scraper_service.py`):
   ```python
   def extract_metrics(self) -> AuditResponse:
       # ... existing extraction ...
       new_metric = self._calculate_new_metric()
       return AuditResponse(..., new_metric=new_metric)
   ```

3. **Update Prompts** (`app/prompts/user_prompt.md`):
   - Add metric to FACTUAL METRICS section
   - Update analysis guidance

### Modifying AI Behavior

**To change how AI analyzes websites**:

1. Edit `app/prompts/system_prompt.md` - Change AI role/rules
2. Edit `app/prompts/user_prompt.md` - Adjust guidance and structure
3. No server restart needed - changes take effect immediately

**To change model or temperature**:

Edit `app/core/config.py`:
```python
MODEL = "llama-3.1-70b-versatile"  # Try different Groq model
TEMPERATURE = 0.5                  # More creative responses (0.2 = deterministic)
```

### Debugging

**Enable detailed logging**:

```python
# In app/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Print response from Groq**:

```python
# In ai_analysis_service.py, modify generate_insights():
print(f"Raw Response: {raw_response}")  # See unmodified AI output
```

---

## 📝 License

This project is provided as-is for educational purposes.

---

## 🤝 Contributing

To improve this project:

1. **Report bugs** - Create an issue with reproduction steps
2. **Suggest features** - Propose improvements via discussion
3. **Submit PRs** - Ensure code follows style guide and includes tests
4. **Improve docs** - Update README with clarifications

---

## 📚 Related Files

- **QUICK_START_AI.md** - Quick reference guide (30 seconds)
- **.env.example** - Example environment file
- **requirements.txt** - Complete dependency list with versions

---

## ✅ Verification Checklist

Before deploying to production:

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file created with valid `GROQ_API_KEY`
- [ ] Syntax check passed: `python -m py_compile app/**/*.py`
- [ ] Health endpoint responds: `curl http://localhost:8000/health`
- [ ] At least one audit successfully logged in `logs/audit_logs.jsonl`
- [ ] AI prompts present: `app/prompts/{system_prompt,user_prompt}.md`
- [ ] No warnings or errors in startup logs

---

## 📞 Support

**If you encounter issues**:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review error messages in console output
3. Check `logs/audit_logs.jsonl` for detailed error context
4. Verify environment variables are set correctly
5. Try running on a different website URL

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Create venv | `python -m venv venv` |
| Activate venv | `venv\Scripts\activate` (Windows) / `source venv/bin/activate` (Mac/Linux) |
| Install deps | `pip install -r requirements.txt` |
| Start server | `python -m uvicorn app.main:app --reload` |
| Test health | `curl http://localhost:8000/health` |
| Check syntax | `python -m py_compile app/services/*.py` |
| View logs | `tail -n 10 logs/audit_logs.jsonl` |
| Test audit | `python test_audit.py` |
| View API docs | Open `http://localhost:8000/docs` in browser |

---

**Last Updated**: March 18, 2026  
**Status**: ✅ Production Ready

See LICENSE file for details.

## 👨‍💻 Author

Built for EIGHT25MEDIA AI-Native Software Engineer Assignment (March 2026)
