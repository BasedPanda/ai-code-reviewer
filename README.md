# AI-Powered Code Review Assistant

An intelligent code review system that leverages AI to provide automated code analysis, suggestions, and real-time collaboration features.

## Features

- 🤖 AI-powered code analysis
- 🔍 Automated code review suggestions
- 📊 Pull request analytics and insights
- ⚡ Real-time updates via WebSocket
- 🔒 Secure GitHub integration
- 📈 Performance and security analysis
- 💬 Interactive comment threads
- 📱 Responsive web interface

## Tech Stack

### Frontend
- React with TypeScript
- Tailwind CSS for styling
- Socket.IO for real-time communication
- React Router for navigation
- Recharts for data visualization
- shadcn/ui components

### Backend
- FastAPI (Python)
- PostgreSQL database
- SQLAlchemy ORM
- OpenAI GPT integration
- WebSocket support
- Redis for caching
- GitHub API integration

## Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Redis (optional, for caching)
- GitHub account
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-code-review.git
cd ai-code-review
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
cp .env.example .env  # Edit with your configurations
```

3. Set up the frontend:
```bash
cd frontend
npm install
cp .env.example .env  # Edit with your configurations
```

4. Set up the database:
```bash
# Using psql
createdb code_review
```

## Running the Application

1. Start the backend server:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

2. Start the frontend development server:
```bash
cd frontend
npm run dev
```

3. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Project Structure

```
ai-code-review/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── types/
│   │   └── utils/
│   ├── package.json
│   └── vite.config.ts
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   └── services/
│   ├── requirements.txt
│   └── .env.example
│
├── .gitignore
└── README.md
```

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Acknowledgments

- OpenAI for GPT API
- FastAPI team
- React and Vite teams
- All contributors