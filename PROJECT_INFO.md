# Project Information

## Overview
Microlearning Content Generator - A professional web application with **Next.js/React frontend** and FastAPI backend for generating educational content using AI.

## Tech Stack
- **Frontend**: Next.js 14, React 18, TypeScript
- **Backend**: FastAPI, Python 3.11+
- **AI Models**: Anthropic Claude 4.5, Google Gemini Pro
- **Deployment**: Docker, Google Cloud Run

## Quick Start
```bash
# 1. Setup
python setup.py           # Backend setup
cd frontend && npm install && cd ..  # Frontend setup

# 2. Run both
# Windows
run-frontend.bat

# Mac/Linux
./run-frontend.sh

# 3. Access
Frontend: http://localhost:3000
Backend: http://localhost:4000
Password: admin123 (or from .env)
```

## File Structure
```
.
├── frontend/              # Next.js React Application
│   ├── pages/            
│   │   ├── _app.tsx      # App wrapper
│   │   └── index.tsx     # Main page
│   ├── components/       
│   │   ├── LoginModal.tsx
│   │   ├── GeneratorForm.tsx
│   │   ├── OutputPanel.tsx
│   │   └── Toast.tsx
│   ├── services/         
│   │   ├── auth.ts       # Authentication
│   │   └── generation.ts # API calls
│   ├── styles/           
│   │   └── globals.css   # Global styles
│   ├── package.json      # Dependencies
│   └── next.config.js    # Next.js config
│
├── Backend Files
│   ├── app.py            # FastAPI server
│   ├── pipeline.py       # AI generation
│   ├── validators.py     # Format validation
│   ├── config.py        # Settings
│   └── run.py           # Entry point
│
├── Prompts (prompts/)    # AI templates
├── Configuration Files
│   ├── requirements.txt  # Python deps
│   ├── Dockerfile       # Container
│   └── .env            # API keys
│
└── Scripts
    ├── run-frontend.bat # Windows starter
    └── run-frontend.sh  # Unix starter
```

## Key Features
- ✅ **Next.js/React UI** (as per Milestone 2 requirements)
- ✅ MCQ and Non-MCQ generation
- ✅ Claude 4.5 & Gemini Pro support
- ✅ Session-based authentication
- ✅ Automatic formatting & validation
- ✅ Rate limiting (10/min)
- ✅ Docker ready
- ✅ Cloud Run deployable

## Development Commands

### Frontend Development
```bash
cd frontend
npm run dev      # Development server (port 3000)
npm run build    # Production build
npm run start    # Production server
npm run lint     # Check code quality
```

### Backend Development
```bash
python run.py           # Run backend (port 4000)
RELOAD=True python run.py  # With auto-reload
```

### Build for Production
```bash
# Frontend
cd frontend
npm run build
npm run export  # Creates 'out' folder

# Backend
docker build -t microlearning .
```

## API Endpoints
- Frontend serves from: `http://localhost:3000`
- Backend API: `http://localhost:4000`
  - `POST /run` - Generate content
  - `POST /api/auth/login` - Login
  - `GET /api/auth/check` - Auth status
  - `GET /healthz` - Health check

## Environment Variables
```env
# Required
GOOGLE_API_KEY=xxx
ANTHROPIC_API_KEY=xxx
EDITOR_PASSWORD=xxx

# Optional
PORT=4000  # Backend port
MAX_FORMATTER_RETRIES=1
```

## Deployment Options

### Local Development
```bash
# Both servers
./run-frontend.sh  # or .bat on Windows
```

### Docker
```bash
docker build -t microlearning .
docker run -p 4000:4000 --env-file .env microlearning
```

### Google Cloud Run
```bash
./deploy.sh
```

## Troubleshooting

1. **npm not found**: Install Node.js 18+
2. **Port in use**: Change PORT in .env
3. **API connection failed**: Check backend is running on port 4000
4. **CORS errors**: Backend configured for localhost:3000 and 4000

## Milestone Compliance

### Milestone 1 ✅
- LangGraph pipeline (simplified)
- Validators for MCQ/NMCQ
- FastAPI with /run endpoint
- Containerization

### Milestone 2 ✅
- **Next.js/React frontend** (as required)
- Single-page UI with toggles
- Secure session authentication
- Static file serving
- Cloud Run ready

## Version
1.0.0 - Production Ready with Next.js Frontend