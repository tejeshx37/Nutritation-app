#!/bin/bash

echo "🚀 Setting up Personal AI Nutritionist..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create environment files
echo "📝 Creating environment files..."

# Backend environment
if [ ! -f "backend/.env" ]; then
    cp backend/env.example backend/.env
    echo "✅ Created backend/.env (please update with your API keys)"
else
    echo "⚠️  backend/.env already exists"
fi

# Frontend environment
if [ ! -f "frontend/.env" ]; then
    cat > frontend/.env << EOF
REACT_APP_API_URL=http://localhost:8000
EOF
    echo "✅ Created frontend/.env"
else
    echo "⚠️  frontend/.env already exists"
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install spaCy model
echo "📚 Installing spaCy model..."
python -m spacy download en_core_web_sm

cd ..

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

echo ""
echo "🎉 Setup complete! Next steps:"
echo ""
echo "1. Update backend/.env with your API keys:"
echo "   - FATSECRET_CLIENT_ID and FATSECRET_CLIENT_SECRET"
echo "   - OPENAI_API_KEY"
echo "   - SECRET_KEY (generate a secure random string)"
echo ""
echo "2. Start the application:"
echo "   docker-compose up -d"
echo ""
echo "3. Access the application:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "4. For development without Docker:"
echo "   - Backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "   - Frontend: cd frontend && npm start"
echo ""
echo "Happy coding! 🥗"
