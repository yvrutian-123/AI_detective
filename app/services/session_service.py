from sqlalchemy.orm import Session
from app.models.session import GameSession, SessionClueUnlock, GameActionLog
from app.models.case import CaseInfo, CaseSuspect, CaseClue
from app.services.case_service import case_service
from app.agents.dm_agent import dm_agent
from app.utils.exception import SessionNotFoundError, CaseNotFoundError
from app.utils.common import format_datetime
import time

class SessionService:
    def create_session(self, db: Session, case_id: int, user_id: int = None):
        case_info = db.query(CaseInfo).filter(