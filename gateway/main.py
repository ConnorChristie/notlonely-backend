import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import httpx
import json
import grpc
import uvicorn

# Import generated gRPC files
from generated import chat_pb2
from generated import chat_pb2_grpc

app = FastAPI()
gRPC_server = None

LLM_MANAGER_URL = "http://llm-manager:8001/chat"

# gRPC Service Implementation
class ChatService(chat_pb2_grpc.ChatServiceServicer):
    async def Chat(self, request: chat_pb2.ChatRequest, context: grpc.aio.ServicerContext):
        request_data = {
            "provider": request.provider,
            "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
        }
        if request.HasField("model"):
            request_data["model"] = request.model

        try:
            async with httpx.AsyncClient() as client:
                async with client.stream("POST", LLM_MANAGER_URL, json=request_data, timeout=None) as response:
                    response.raise_for_status()
                    async for chunk in response.aiter_text():
                        yield chat_pb2.ChatResponse(partial=True, content=chunk)
            
            yield chat_pb2.ChatResponse(partial=False, content="")

        except httpx.HTTPStatusError as e:
            await context.abort(grpc.StatusCode.INTERNAL, f"LLM Manager request failed: {e.response.text}")
        except Exception as e:
            await context.abort(grpc.StatusCode.INTERNAL, f"An unexpected error occurred: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Start the gRPC server in the background."""
    global gRPC_server
    gRPC_server = grpc.aio.server()
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatService(), gRPC_server)
    gRPC_server.add_insecure_port('[::]:50051')
    asyncio.create_task(gRPC_server.start())
    print("gRPC server started on port 50051")

@app.on_event("shutdown")
async def shutdown_event():
    """Gracefully stop the gRPC server."""
    if gRPC_server:
        await gRPC_server.stop(grace=5)
        print("gRPC server shut down.")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            request_data = json.loads(data)

            async with httpx.AsyncClient() as client:
                async with client.stream("POST", LLM_MANAGER_URL, json=request_data, timeout=None) as response:
                    async for chunk in response.aiter_text():
                        await websocket.send_json({"partial": True, "content": chunk})
            
            await websocket.send_json({"partial": False, "content": ""})

    except WebSocketDisconnect:
        print("Client disconnected")

@app.get("/health")
async def health_check():
    return {"status": "ok"} 