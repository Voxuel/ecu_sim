from pydantic import BaseModel, Field
from typing import Optional
class DiagnosticSession(BaseModel):
    session_type: int = Field(...)
    is_active: bool = Field(False)
    
class SessionManager:
    def __init__(self):
        self.active_session = Optional[DiagnosticSession] = None
        
    def start_session(self, session_type: int):
        self.active_session = DiagnosticSession(session_type=session_type, is_active=True)
    
    def end_session(self):
        self.active_session = None
        
    def get_active_session(self) -> Optional[DiagnosticSession]:
        return self.active_session