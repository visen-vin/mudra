# Setup Guide

## Local Development

### Backend
1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```
2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up environment variables:**
   Copy `.env.example` to `.env` and fill in your API keys.
5. **Run the server:**
   ```bash
   python3 main.py
   ```

### Frontend
1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```
2. **Install dependencies:**
   ```bash
   npm install
   ```
3. **Run the development server:**
   ```bash
   npm run dev
   ```

## Docker Setup

To run the entire application using Docker:

1. **Build and run with docker-compose:**
   ```bash
   docker-compose up --build
   ```
2. **Access the application:**
   - Frontend: `http://localhost:5173` (or `http://localhost:8000` if serving from backend)
   - Backend API: `http://localhost:8000/api`

## Running Tests

### Backend Tests
Run all tests from the project root:
```bash
export PYTHONPATH=$PYTHONPATH:.
python3 -m pytest tests/ -v
```
