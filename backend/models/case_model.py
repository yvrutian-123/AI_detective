from pydantic import BaseModel, Field
from typing import List, Optional

class Victim(BaseModel):
    name: str
    identity: str
    death_cause: str

class Suspect(BaseModel):
    id: str
    name: str
    motive: str
    alibi: str
    secret: str

class TrueKiller(BaseModel):
    suspect_id: str
    modus_operandi: str
    key_flaw: str

class Clue(BaseModel):
    id: str
    content: str
    type: str
    location: str
    related_suspect: Optional[str] = None

class CaseInfo(BaseModel):
    case_name: str
    background: str
    victim: Victim

class CaseData(BaseModel):
    case_id: str
    case_info: CaseInfo
    suspects: List[Suspect]
    true_killer: TrueKiller
    clue_library: List[Clue]

class GameState(BaseModel):
    current_stage: str = "intro"
    unlocked_clue_ids: List[str] = Field(default_factory=list)
    interrogated_suspect_ids: List[str] = Field(default_factory=list)
    dialog_history: List[dict] = Field(default_factory=list)
    player_choices: List[dict] = Field(default_factory=list)

class SessionData(BaseModel):
    session_id: str
    case_id: str
    game_state: GameState

class SaveData(BaseModel):
    save_id: str
    user_id: str
    create_time: str
    update_time: str
    save_name: str
    case_data: CaseData
    game_state: GameState