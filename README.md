# Microlearning Content Generator

A professional web application for generating high-quality educational content using AI. Features a modern **Next.js/React frontend** with a FastAPI backend for converting curated notes into Multiple Choice Questions (MCQ) and Clinical Vignettes (Non-MCQ).

## Features

- **Next.js/React Frontend**: Modern, responsive single-page application
- **Dual Content Types**: Generate MCQ and Non-MCQ educational materials
- **AI Model Selection**: Choose between Claude 4.5 (Anthropic) or Gemini Pro (Google)
- **Smart Pipeline**: Automated generation → formatting → validation with retry logic
- **Quality Assurance**: Deterministic validators ensure output meets strict format requirements
- **Production Ready**: Secure authentication, rate limiting, and containerization

## Tech Stack

- **Frontend**: Next.js 14, React 18, TypeScript
- **Backend**: FastAPI, Python 3.11+
- **AI Models**: Anthropic Claude, Google Gemini
- **Deployment**: Docker, Google Cloud Run

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- API Keys from:
  - [Google AI Studio](https://makersuite.google.com/app/apikey)
  - [Anthropic Console](https://console.anthropic.com/)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository>
   cd microlearning-generator
   ```

2. **Set up backend**
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Configure environment
   cp env.example .env
   # Edit .env with your API keys
   ```

3. **Set up frontend**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Run the application**

   **Option 1: Run both frontend and backend together**
   ```bash
   # Windows
   run-frontend.bat
   
   # Mac/Linux
   chmod +x run-frontend.sh
   ./run-frontend.sh
   ```

   **Option 2: Run separately**
   ```bash
   # Terminal 1: Backend
   python run.py
   
   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:4000

## Project Structure

```
microlearning-generator/
├── frontend/              # Next.js React application
│   ├── pages/            # Next.js pages
│   ├── components/       # React components
│   ├── services/         # API services
│   ├── styles/           # CSS styles
│   └── package.json      # Node dependencies
├── app.py                # FastAPI backend
├── pipeline.py           # Content generation pipeline
├── validators.py         # Format validators
├── config.py            # Application configuration
├── prompts/             # AI prompt templates
├── static/              # Legacy static files
├── Dockerfile           # Container configuration
├── requirements.txt     # Python dependencies
└── README.md           # Documentation
```

## Frontend Development

The frontend is built with Next.js and React, providing:

### Components
- **LoginModal**: Secure authentication interface
- **GeneratorForm**: Configuration and input controls
- **OutputPanel**: Display generated content with actions
- **Toast**: User notifications

### Services
- **authService**: Handle authentication
- **generationService**: API calls for content generation

### Running Frontend Only
```bash
cd frontend
npm run dev        # Development mode with hot reload
npm run build      # Production build
npm run start      # Production server
```

## Backend API

### Endpoints

- `GET /` - API documentation
- `POST /run` - Generate content
- `GET /healthz` - Health check
- `GET /version` - Version info
- `POST /api/auth/login` - Authentication
- `GET /api/auth/check` - Check auth status
- `POST /api/auth/logout` - Logout

### API Request Example

```json
POST /run
{
  "content_type": "MCQ",
  "generator_model": "claude",
  "input_text": "Your educational content here...",
  "num_questions": 3,
  "focus_areas": "Optional focus areas"
}
```

## Configuration

Key environment variables in `.env`:

```env
# API Keys (Required)
GOOGLE_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Authentication
EDITOR_PASSWORD=secure_password

# Server Configuration
PORT=4000  # Backend port

# Models (Optional)
CLAUDE_MODEL=claude-3-5-sonnet-20241022
GEMINI_PRO=gemini-2.0-flash-exp
```

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t microlearning .

# Run container
docker run -p 4000:4000 --env-file .env microlearning
```

### Production Build

```bash
# Build frontend for production
cd frontend
npm run build
npm run export  # Creates static export

# The backend can serve the static frontend
# Place the 'out' folder contents in 'static' directory
```

### Google Cloud Run

```bash
# Deploy to Cloud Run
./deploy.sh
```

## Development

### Frontend Development
```bash
cd frontend
npm run dev  # Runs on http://localhost:3000
```

### Backend Development
```bash
# Run with auto-reload
RELOAD=True python run.py
```

### Running Tests
```bash
# Backend tests
pytest

# Frontend linting
cd frontend
npm run lint
```

## Content Formats

### MCQ Format
- Clinical vignette/question stem
- 4-5 answer options (A-E)
- Correct answer with detailed explanation
- Analysis of incorrect options
- Key learning insights

### Non-MCQ Format
- Clinical vignette scenario
- Mixed question types:
  - True/False questions
  - Yes/No questions
  - Multiple choice dropdowns
- Detailed explanations for each answer

## Troubleshooting

### Common Issues

1. **Port conflicts**: Change ports in `.env` and `frontend/package.json`
2. **API connection errors**: Ensure backend is running on port 4000
3. **Build errors**: Check Node.js and Python versions
4. **CORS issues**: Backend CORS is configured for localhost:3000 and 4000

## Security

- Session-based authentication with HttpOnly cookies
- Rate limiting (10 requests/minute)
- Environment-based secrets management
- Ready for Google IAP integration

## License

Proprietary and confidential. Internal use only.

## Support

For issues or questions, contact the development team.