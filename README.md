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

- Python 3.8+
- MongoDB
- OpenAI API access

### Installation

1. **Clone the repository**
```bash
   git clone
   cd ai-landing-page-builder
```

2. **Set up the backend**
```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
```

3. **Configure environment variables**
   
   Create a `.env` file in the `backend/` directory:
```env
   OPENAI_API_KEY=your_api_key
   MONGODB_URI=mongodb+srv://your_connection_string
```

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
