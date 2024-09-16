from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from graph import FriendlyResponder
import uvicorn

app = FastAPI()
responder = FriendlyResponder()

class MessageRequest(BaseModel):
    user_input: str
    session_id: str

@app.post("/chat/v1")
async def respond_to_message(request: MessageRequest):
    try:
        user_input = request.user_input
        session_id = request.session_id
        message = {"question":user_input,"session_id":session_id}
        responses = responder.run(message)
        return {"responses": responses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    
    uvicorn.run(app, host="127.0.0.1", port=8001)
