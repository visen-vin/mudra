# backend/api/auth.py
from fastapi import APIRouter, HTTPException
from backend.feeds.zerodha import ZerodhaAdapter

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/zerodha/callback")
async def zerodha_oauth_callback(request_token: str):
    """
    Handle Zerodha OAuth callback (Phase 5)
    Converts request_token to access_token
    """
    # TODO: Exchange request_token for access_token
    # POST to https://api.kite.trade/session/token
    return {"status": "placeholder", "note": "Implement in Phase 5"}
