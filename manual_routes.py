from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ManualGenerateRequest, ManualGenerateResponse
from app.models import Course, User
from app.auth import get_current_user
from app.services.watsonx_service import watsonx_service
from app.services.rag_service import rag_service

router = APIRouter(prefix="/manuals", tags=["AI Manual Generator"])

@router.post("/generate", response_model=ManualGenerateResponse)
def generate_lab_manual(
    req: ManualGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generates a full engineering lab manual powered by IBM Granite (watsonx.ai)
    with RAG augmentation from uploaded course syllabus PDFs.
    """
    rag_context = ""
    source_refs = []

    # Retrieve syllabus context via RAG
    if req.use_rag:
        rag_query = f"{req.syllabus_topic} {req.experiment_title} {req.course_name}"
        rag_res = rag_service.retrieve_relevant_context(
            course_id=req.course_id,
            query=rag_query,
            n_results=3
        )
        rag_context = rag_res.get("context", "")
        source_refs = rag_res.get("sources", [])

    generated = watsonx_service.generate_lab_manual(
        course_code=req.course_code,
        course_name=req.course_name,
        experiment_title=req.experiment_title,
        experiment_number=req.experiment_number,
        syllabus_topic=req.syllabus_topic,
        available_equipment=req.available_equipment,
        lab_type=req.lab_type,
        rag_context=rag_context,
        source_references=source_refs
    )

    return generated

