# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import Config

app = FastAPI(title="Mudra Trading", version="0.1.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
