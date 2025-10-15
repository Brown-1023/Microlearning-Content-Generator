# Frontend - Microlearning Content Generator

Next.js/React single-page application for the Microlearning Content Generator.

## Structure

- `pages/` - Next.js pages
- `components/` - React components
- `services/` - API service layer
- `styles/` - Global styles

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run production server
npm start
```

## Features

- Content type toggle (MCQ/Non-MCQ)
- Model selection (Claude/Gemini)
- Input fields for notes, questions, focus areas
- Real-time generation with validation
- Download results as .txt

## Deployment

This frontend is designed to be deployed as part of a single container with the backend for Google Cloud Run. See the main [README.md](../README.md) for deployment instructions.