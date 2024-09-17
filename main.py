from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from graph import FriendlyResponder

app = FastAPI()
responder = FriendlyResponder()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes especificar dominios específicos en lugar de "*"
    allow_credentials=True,
    allow_methods=["*"],  # Puedes restringir a métodos específicos como ["GET", "POST"]
    allow_headers=["*"],  # Puedes especificar los headers permitidos como ["Authorization", "Content-Type"]
)

class MessageRequest(BaseModel):
    user_input: str
    session_id: str

@app.post("/chat/v1")
async def respond_to_message(request: MessageRequest):
    try:
        user_input = request.user_input
        session_id = request.session_id
        message = {"question": user_input, "session_id": session_id}
        responses = responder.run(message)
        return {"responses": responses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/")
async def alive():
    return {"message":"alive"}
    
# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8001)
