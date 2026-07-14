import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.utils.database import init_database
from backend.services.session_manager import create_new_game, get_game_session, save_game
from backend.services.dm_agent import generate_intro, generate_investigation_response

app = FastAPI(title="悬疑探案游戏", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
def root():
    return FileResponse(os.path.join(frontend_dir, "index.html"))

init_database()

@app.post("/api/new-game")
def new_game(topic: str = "悬疑", difficulty: str = "medium", scene: str = "现代都市"):
    result, errors = create_new_game(topic, difficulty, scene)
    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    intro = generate_intro(result['case_data'])
    
    return {
        "session_id": result['session_id'],
        "case_id": result['case_id'],
        "intro": intro,
        "case_data": result['case_data']
    }

@app.get("/api/session/{session_id}")
def get_session(session_id: str):
    session_data = get_game_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="会话不存在")
    return session_data

from pydantic import BaseModel

class ActionRequest(BaseModel):
    action: str

class SaveRequest(BaseModel):
    user_id: str = "default_user"
    save_name: str = "存档"

@app.post("/api/action/{session_id}")
def game_action(session_id: str, request: ActionRequest):
    session_data = get_game_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    response = generate_investigation_response(session_id, request.action)
    
    if 'error' in response:
        raise HTTPException(status_code=400, detail=response['error'])
    
    return {
        "session_id": session_id,
        "response": response,
        "game_state": get_game_session(session_id)['game_state']
    }

@app.post("/api/save/{session_id}")
def save_game_api(session_id: str, request: SaveRequest):
    result = save_game(session_id, request.user_id, request.save_name)
    if not result:
        raise HTTPException(status_code=400, detail="保存失败")
    return result

@app.get("/api/case/{case_id}")
def get_case(case_id: str):
    from backend.utils.database import get_case
    case_data = get_case(case_id)
    if not case_data:
        raise HTTPException(status_code=404, detail="案件不存在")
    return case_data

@app.get("/api/saves/{user_id}")
def get_saves(user_id: str):
    from backend.utils.database import get_game_saves
    saves = get_game_saves(user_id)
    return saves

@app.get("/api/load/{save_id}")
def load_game_api(save_id: str):
    from backend.services.session_manager import load_game
    result = load_game(save_id)
    if not result:
        raise HTTPException(status_code=404, detail="存档不存在")
    return result

@app.delete("/api/save/{save_id}")
def delete_save_api(save_id: str):
    from backend.utils.database import delete_game_save
    delete_game_save(save_id)
    return {"message": "删除成功"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)