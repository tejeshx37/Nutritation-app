# Personal AI Nutritionist 🥗

An intelligent web application that helps users track nutrition, get AI-powered meal recommendations, and achieve their health goals through natural language food logging.

## 🚀 Features

- **Natural Language Food Logging**: Input food in plain English ("2 rotis and dal for lunch")
- **AI-Powered Parsing**: Intelligent extraction of food items, quantities, and units
- **Nutrition Tracking**: Comprehensive calorie and macro tracking with FatSecret API
- **Smart Recommendations**: AI-generated meal suggestions based on goals and preferences
- **Beautiful Dashboard**: Visual progress tracking with interactive charts
- **Indian Food Support**: Specialized recognition for Indian cuisine and portions

## 🏗️ Architecture

```
React Frontend ↔️ FastAPI Backend ↔️ FatSecret API
                       ↕️
                 PostgreSQL Database
                       ↕️
                 NLP Processing (spaCy/GPT)
```

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React with TypeScript
- **Database**: PostgreSQL
- **APIs**: FatSecret API, OpenAI GPT-4
- **NLP**: spaCy + GPT-4 for food parsing
- **Charts**: Chart.js
- **Authentication**: JWT tokens
- **Styling**: Tailwind CSS

## 📁 Project Structure

```
personal-ai-nutritionist/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Configuration & utilities
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── main.py         # FastAPI app entry point
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── utils/          # Utility functions
│   ├── package.json
│   └── Dockerfile
├── database/                # Database migrations & seeds
├── docs/                    # API documentation
└── docker-compose.yml       # Development environment
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Docker & Docker Compose

### 1. Clone & Setup
```bash
git clone <repository-url>
cd personal-ai-nutritionist
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Environment Variables
Create `.env` files in both backend and frontend directories with:
```env
# Backend
DATABASE_URL=postgresql://user:password@localhost/nutrition_db
FATSECRET_CLIENT_ID=your_client_id
FATSECRET_CLIENT_SECRET=your_client_secret
OPENAI_API_KEY=your_openai_key
SECRET_KEY=your_secret_key

# Frontend
REACT_APP_API_URL=http://localhost:8000
```

### 5. Run with Docker
```bash
docker-compose up -d
```

## 🔧 Development

### Backend Development
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm start
```

### Database Migrations
```bash
cd backend
alembic upgrade head
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For support and questions, please open an issue in the repository.
