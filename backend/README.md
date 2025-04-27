# Backend Server

This is a FastAPI server for Animind with an `/agent` endpoint.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the server

Start the server with:
```bash
uvicorn main:app --reload
```

The server will be available at http://localhost:8000

## Endpoints

- `GET /`: Welcome message
- `POST /agent`: Takes a text input and returns "hi"

## API Documentation

FastAPI provides automatic interactive documentation:
- http://localhost:8000/docs
- http://localhost:8000/redoc 