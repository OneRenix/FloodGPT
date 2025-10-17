import pandas as pd
import numpy as np
import json
import logging
import asyncio
import os
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException

load_dotenv()
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from fastapi.staticfiles import StaticFiles

# Import the compiled LangGraph app from your main agent script
from main_agent import app

# --- Environment Variables ---
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")

# --- Rate Limiting ---
limiter = Limiter(key_func=get_remote_address)

# --- 1. Custom JSON Encoder ---
# This class teaches Python's JSON library how to handle special types
# that it doesn't know about, like NumPy numbers and Pandas DataFrames.
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        if isinstance(obj, pd.DataFrame):
            # Convert DataFrame to a JSON-friendly dict with 'split' orientation
            return obj.to_dict(orient='split')
        # Let the base class default method raise the TypeError
        return super(CustomJSONEncoder, self).default(obj)

# --- API Setup ---
api = FastAPI()
api.mount("/static", StaticFiles(directory="static"), name="static")

@api.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "frame-ancestors 'none'"
    return response
api.state.limiter = limiter
api.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- Pydantic Models ---
class AgentRequest(BaseModel):
    question: str
    recaptcha_token: str
    honeypot: str | None = None

# --- Helper Functions ---
async def verify_recaptcha(token: str) -> bool:
    if not RECAPTCHA_SECRET_KEY:
        logging.error("RECAPTCHA_SECRET_KEY is not set.")
        return False
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": RECAPTCHA_SECRET_KEY,
                "response": token,
            },
        )
        result = response.json()
        if result.get("success") and result.get("score", 0.0) > 0.3:
            return True
    return False

# --- API Endpoints ---

@api.post("/stream-agent")
@limiter.limit("5/minute")
async def stream_agent_endpoint(request: Request, data: AgentRequest):
    """
    Receives a question via a POST request and streams the agent's progress.
    Includes reCAPTCHA, honeypot, and rate limiting checks.
    """
    # Honeypot check
    if data.honeypot:
        # Silently fail or log, but don't give the bot any indication of why.
        logging.warning(f"Honeypot field filled by {request.client.host}. Value: {data.honeypot}")
        raise HTTPException(status_code=400, detail="Invalid request")

    # reCAPTCHA verification
    if not await verify_recaptcha(data.recaptcha_token):
        logging.warning(f"reCAPTCHA verification failed for {request.client.host}.")
        raise HTTPException(status_code=403, detail="reCAPTCHA verification failed.")

    inputs = {"question": data.question}

    async def event_stream():
        """The generator function that yields events as the agent runs."""
        try:
            # Use 'astream' to get real-time updates from the LangGraph
            async for chunk in app.astream(inputs):
                # Each chunk is a dictionary where the key is the node that just ran
                for node_name, node_output in chunk.items():
                    event_data = {"event": node_name, "data": node_output}
                    # Yield the event in Server-Sent Event format, using our custom encoder
                    yield f"data: {json.dumps(event_data, cls=CustomJSONEncoder)}\n\n"
                    await asyncio.sleep(0.1)
            
            # Send a final 'end' event
            yield f"data: {json.dumps({'event': 'end'})}\n\n"

        except Exception as e:
            logging.error(f"Error during stream: {e}")
            yield f"data: {json.dumps({'event': 'error', 'data': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@api.get("/")
async def read_index():
    """Serves the main index.html file at the root URL."""
    return FileResponse('index.html')
