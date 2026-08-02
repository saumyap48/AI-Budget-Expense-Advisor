from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.common import ApiResponse
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.rag_service import RAGService
from backend.app.dependencies.auth import get_current_user
from backend.app.models.user import User

router = APIRouter(prefix="/chat", tags=["AI Assistant"])


@router.post("", response_model=ApiResponse[ChatResponse])
def ask_ai_assistant(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = RAGService(db)
    response = service.process_chat_query(user_id=current_user.id, request=payload)
    return ApiResponse(
        success=True,
        data=response,
        message="AI response generated successfully"
    )
