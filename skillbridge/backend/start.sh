#!/bin/bash
# Run from inside the backend/ directory

# Load .env if present
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Check API key
if [ -z "$GEMINI_API_KEY" ]; then
  echo "ERROR: GEMINI_API_KEY is not set."
  echo "Create a .env file with: GEMINI_API_KEY=your_key"
  exit 1
fi

echo "Starting SkillBridge Pro AI backend on http://localhost:8000"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
