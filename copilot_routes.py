from fastapi import APIRouter, Depends
from app.schemas import CopilotRequest, CopilotResponse
from app.models import User
from app.auth import get_current_user
from app.services.watsonx_service import watsonx_service

router = APIRouter(prefix="/copilot", tags=["AI Lab Copilot"])

@router.post("/chat", response_model=CopilotResponse)
def copilot_chat(
    req: CopilotRequest,
    current_user: User = Depends(get_current_user)
):
    """
    AI Lab Copilot powered by IBM Granite.
    Explains errors, suggests debugging hints, reviews output discrepancies,
    and generates personalized viva voce practice questions.
    """
    res = watsonx_service.generate_copilot_assistance(
        prompt=req.prompt,
        mode=req.mode,
        language=req.language or "python",
        code=req.code,
        experiment_title=req.experiment_title,
        error_message=req.error_message,
        actual_output=req.actual_output,
        expected_output=req.expected_output
    )
    return res

