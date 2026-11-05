from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import CodeExecutionRequest, CodeExecutionResponse
from app.models import ExecutionHistory, User, Submission
from app.auth import get_current_user
from app.services.compiler_service import compiler_service

router = APIRouter(prefix="/compiler", tags=["Online Compiler"])

@router.post("/execute", response_model=CodeExecutionResponse)
def execute_code(
    req: CodeExecutionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Executes student code in an isolated container/Judge0 sandbox.
    Stores record in execution history.
    """
    test_case_dicts = [tc.dict() for tc in req.test_cases] if req.test_cases else []
    exec_result = compiler_service.execute_code(
        language=req.language,
        code=req.code,
        stdin=req.stdin or "",
        test_cases=test_case_dicts
    )

    # Save execution record
    if req.experiment_id:
        history_record = ExecutionHistory(
            submission_id=req.submission_id,
            student_id=current_user.id,
            experiment_id=req.experiment_id,
            language=req.language,
            code=req.code,
            stdin=req.stdin,
            stdout=exec_result.get("stdout"),
            stderr=exec_result.get("stderr"),
            exit_code=exec_result.get("exit_code", 0),
            execution_time=exec_result.get("execution_time", 0.0),
            memory_used=exec_result.get("memory_used", 0.0),
            status=exec_result.get("status", "success")
        )
        db.add(history_record)
        db.commit()

    return exec_result

@router.get("/history/{experiment_id}")
def get_experiment_execution_history(
    experiment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ExecutionHistory).filter(ExecutionHistory.experiment_id == experiment_id)
    if current_user.role == "student":
        query = query.filter(ExecutionHistory.student_id == current_user.id)
        
    records = query.order_by(ExecutionHistory.created_at.desc()).limit(20).all()
    return records

