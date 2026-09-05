import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import socketio
import os
os.environ['WEB_CONCURRENCY'] = '1'
os.environ['MALLOC_ARENA_MAX'] = '2'

# Import our custom Socket.IO server
from core.socket_manager import sio
# Import our custom modules
from core.socket_manager import sio
from speech.tts import generate_audio_base64

# Create the FastAPI app
app = FastAPI(title="SignMitra AI Microservices", version="1.0.0")

# Setup CORS (Important for letting the frontend communicate)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "online", "message": "SignMitra Neural Engine is active."}

class TTSRequest(BaseModel):
    text: str

@app.post("/api/tts")
async def get_audio(request: TTSRequest):
    audio_data = generate_audio_base64(request.text)
    if audio_data:
        return {"status": "success", "audio": audio_data}
    return {"status": "error", "message": "Failed to generate speech"}


# This is the most bulletproof way to handle FastAPI + SocketIO
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

if __name__ == "__main__":
    print("🚀 Starting SignMitra Neural Engine...")
    print("👉 Ensure you run this from the ai_server directory.")
    # Run the wrapped socket_app instead of the plain app
    #uvicorn.run(socket_app, host="127.0.0.1", port=5000)
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(socket_app, host="0.0.0.0", port=port)