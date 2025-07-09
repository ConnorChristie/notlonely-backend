from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, AsyncIterator
import importlib.metadata

from providers.base import BaseProvider

class ChatRequest(BaseModel):
    provider: str
    messages: List[Dict[str, str]]
    model: str = None

app = FastAPI()
PROVIDERS: Dict[str, BaseProvider] = {}

def load_providers():
    """Load providers from entry points."""
    for entry_point in importlib.metadata.entry_points(group="notlonely_providers"):
        PROVIDERS[entry_point.name] = entry_point.load()

@app.on_event("startup")
async def startup_event():
    """Load providers on startup."""
    load_providers()

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Handle a chat request, streaming the response.
    """
    if request.provider not in PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Provider '{request.provider}' not found.")

    provider_class = PROVIDERS[request.provider]
    provider = provider_class()

    async def stream_response() -> AsyncIterator[str]:
        kwargs = {}
        if request.model:
            kwargs["model"] = request.model
            
        async for token in provider.chat(request.messages, **kwargs):
            yield token

    return StreamingResponse(stream_response(), media_type="text/plain")

@app.get("/health")
async def health_check():
    return {"status": "ok", "providers": list(PROVIDERS.keys())} 