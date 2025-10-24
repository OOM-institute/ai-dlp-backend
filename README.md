# AI Landing Page Builder

An AI-powered landing page builder that uses OpenAI to generate dynamic, customizable landing pages based on user context and competitor analysis.

## 🚀 Features

- **AI-Powered Content Generation**: Leverages OpenAI to create tailored landing page content
- **Website Crawling**: Automatically analyzes competitor websites for inspiration
- **Dynamic Page Sections**: Supports hero, features, testimonials, FAQ, contact, and footer sections
- **MongoDB Integration**: Persistent storage for generated pages
- **RESTful API**: FastAPI backend with comprehensive endpoints

## 📁 Project Structure
```
ai-landing-page-builder/
├── backend/
│   ├── main.py                     # FastAPI app entry point
│   ├── requirements.txt            # Python dependencies
│   ├── .env                        # Environment variables (create this, not in git)
│   ├── app/
│   │   ├── __init__.py            # Load environment variables
│   │   ├── models.py              # Pydantic request/response models
│   │   ├── db.py                  # MongoDB CRUD operations
│   │   ├── crawler.py             # Website crawling logic
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── prompts.py         # LLM prompt templates
│   │   │   └── generator.py       # OpenAI API calls
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── pages.py           # API endpoints
│   ├── docs/
│   │   ├── ADR.md                 # Architecture decisions
│   │   └── ARCH.html              # System architecture diagram
│   └── pageSpec.json              # Sample page specification
```

## 🛠️ Setup

### Prerequisites

- Docker and Docker Compose
- OpenAI API access
- MongoDB Atlas account (or local MongoDB)

### Installation with Docker (Recommended)

1. **Clone the repository**
```bash
   git clone
   cd ai-dlp-backend
```

2. **Configure environment variables**
   
   Create a `.env` file in the project root:
```env
   OPENAI_API_KEY=your_api_key
   MONGODB_URI=mongodb+srv://your_connection_string
   ENVIRONMENT=development
```

3. **Build and run with Docker Compose**
```bash
   docker-compose up --build
```

   The API will be available at `http://localhost:8000`

4. **Access API documentation**
```bash
   http://localhost:8000/docs
```

5. **Stop the containers**
```bash
   docker-compose down
```

6. **View logs**
```bash
   docker-compose logs -f
```

### Local Development (without Docker)

**Note:** For local development, we recommend using Docker. If you prefer to run without Docker:

1. **Install Python 3.13+**

2. **Install dependencies**
```bash
   pip install -r requirements.txt
```

3. **Create a `.env` file** with your environment variables

4. **Run the backend**
```bash
   uvicorn main:app --reload
```

## 📡 API Endpoints

- `POST /api/pages/generate` - Generate new landing page
- `GET /api/pages/{id}` - Retrieve page
- `POST /api/pages/{id}/edit-section` - Manual section edit
- `POST /api/pages/{id}/regenerate-section` - AI regeneration
- `POST /api/pages/{id}/reorder-sections` - Drag & drop
- `POST /api/pages/{id}/publish` - Publish page
- `DELETE /api/pages/{id}` - Delete section

## 🧪 Usage Example
```python
import requests

# Generate a landing page
response = requests.post("http://localhost:8000/api/pages/generate", json={
    "industry": "E-commerce",
    "offer": "eco friendly shoes",
    "target_audience": "teenagers",
    "brand_tone": "playful",
    "competitor_url": "https://www.nike.com"
})

page_data = response.json()
print(f"Generated page ID: {page_data['page_id']}")
```

## 📚 Documentation

- [Architecture Decision Records](https://github.com/Angely0122/ai-landing-page-backend/blob/main/docs/ADR.md)
- [System Architecture Diagram](https://htmlpreview.github.io/?https://github.com/Angely0122/ai-landing-page-backend/blob/main/docs/ARCH.html)
