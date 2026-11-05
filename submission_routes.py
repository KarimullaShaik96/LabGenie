import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Submission, Experiment, User, Course, VivaAssessment
from app.schemas import (
    SubmissionCreate, SubmissionUpdate, SubmissionOut, FacultyVerifyRequest,
    VivaSubmitRequest, VivaAssessmentOut
)
from app.auth import get_current_user, require_roles
from app.services.watsonx_service import watsonx_service

router = APIRouter(prefix="/submissions", tags=["Submissions & Verification"])

@router.get("", response_model=List[SubmissionOut])
def get_submissions(
    course_id: Optional[int] = None,
    experiment_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    student_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Submission)

    if current_user.role == "student":
        query = query.filter(Submission.student_id == current_user.id)
    elif student_id:
        query = query.filter(Submission.student_id == student_id)

    if experiment_id:
        query = query.filter(Submission.experiment_id == experiment_id)
    
    if course_id:
        query = query.join(Experiment).filter(Experiment.course_id == course_id)

    if status_filter:
        query = query.filter(Submission.status == status_filter)

    submissions = query.order_by(Submission.updated_at.desc()).all()
    results = []
    now = datetime.datetime.utcnow()

    for s in submissions:
        exp = s.experiment
        deadline = exp.deadline if exp else None
        is_overdue = bool(deadline and (s.submitted_at or now) > deadline and s.status != "verified")

        results.append({
            "id": s.id,
            "experiment_id": s.experiment_id,
            "student_id": s.student_id,
            "status": s.status,
            "submitted_code": s.submitted_code,
            "submitted_circuit_data": s.submitted_circuit_data,
            "input_data": s.input_data,
            "output_data": s.output_data,
            "observations": s.observations,
            "result": s.result,
            "faculty_comments": s.faculty_comments,
            "faculty_marks": s.faculty_marks,
            "rubric_scores": s.rubric_scores or {},
            "ai_evaluation": s.ai_evaluation,
            "submitted_at": s.submitted_at,
            "verified_at": s.verified_at,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
            "deadline": deadline,
            "is_overdue": is_overdue,
            "student_name": s.student.name if s.student else None,
            "student_roll": s.student.roll_or_emp_id if s.student else None,
            "experiment_title": exp.title if exp else None,
            "experiment_number": exp.experiment_number if exp else None,
            "course_name": exp.course.name if exp and exp.course else None,
            "course_code": exp.course.code if exp and exp.course else None,
            "verified_by_name": s.verified_by.name if s.verified_by else None
        })
    return results

@router.get("/experiment/{experiment_id}", response_model=SubmissionOut)
def get_or_create_submission(
    experiment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetches student's current submission or initializes an in_progress draft"""
    exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    submission = db.query(Submission).filter(
        Submission.experiment_id == experiment_id,
        Submission.student_id == current_user.id
    ).first()

    if not submission:
        submission = Submission(
            experiment_id=experiment_id,
            student_id=current_user.id,
            status="in_progress",
            submitted_code=exp.source_code,
            output_data=exp.expected_output,
            observations=exp.observations,
            result=exp.result
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)

    now = datetime.datetime.utcnow()
    deadline = exp.deadline
    is_overdue = bool(deadline and (submission.submitted_at or now) > deadline and submission.status != "verified")

    return {
        "id": submission.id,
        "experiment_id": submission.experiment_id,
        "student_id": submission.student_id,
        "status": submission.status,
        "submitted_code": submission.submitted_code,
        "submitted_circuit_data": submission.submitted_circuit_data,
        "input_data": submission.input_data,
        "output_data": submission.output_data,
        "observations": submission.observations,
        "result": submission.result,
        "faculty_comments": submission.faculty_comments,
        "faculty_marks": submission.faculty_marks,
        "rubric_scores": submission.rubric_scores or {},
        "ai_evaluation": submission.ai_evaluation,
        "submitted_at": submission.submitted_at,
        "verified_at": submission.verified_at,
        "created_at": submission.created_at,
        "updated_at": submission.updated_at,
        "deadline": deadline,
        "is_overdue": is_overdue,
        "student_name": current_user.name,
        "student_roll": current_user.roll_or_emp_id,
        "experiment_title": exp.title,
        "experiment_number": exp.experiment_number,
        "course_name": exp.course.name if exp.course else None,
        "course_code": exp.course.code if exp.course else None,
        "verified_by_name": submission.verified_by.name if submission.verified_by else None
    }

@router.put("/{submission_id}/save")
def save_submission_draft(
    submission_id: int,
    data: SubmissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if submission.student_id != current_user.id and current_user.role not in ["faculty", "hod"]:
        raise HTTPException(status_code=403, detail="Not authorized to edit this submission")

    for field, val in data.dict(exclude_unset=True).items():
        setattr(submission, field, val)

    submission.updated_at = datetime.datetime.utcnow()
    db.commit()
    return {"message": "Draft saved successfully", "status": submission.status, "updated_at": submission.updated_at}

@router.post("/{submission_id}/submit")
def submit_for_verification(
    submission_id: int,
    data: Optional[SubmissionUpdate] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if data:
        for field, val in data.dict(exclude_unset=True).items():
            setattr(submission, field, val)

    submission.status = "under_verification"
    submission.submitted_at = datetime.datetime.utcnow()
    
    # Module 10: AI-Assisted Experiment Evaluation (IBM Granite)
    exp = submission.experiment
    preliminary_eval = watsonx_service.evaluate_submission_preliminary(
        experiment=exp,
        code=submission.submitted_code or "",
        output_log=submission.output_data or "",
        observations=submission.observations or ""
    )
    submission.ai_evaluation = preliminary_eval

    db.commit()
    return {
        "message": "Experiment submitted for faculty verification successfully.",
        "status": submission.status,
        "ai_preliminary_evaluation": submission.ai_evaluation
    }

@router.post("/{submission_id}/verify")
def verify_submission(
    submission_id: int,
    req: FacultyVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["faculty", "hod"]))
):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    submission.status = req.status  # 'verified' or 'correction_required'
    submission.faculty_comments = req.faculty_comments
    submission.faculty_marks = req.faculty_marks
    submission.rubric_scores = req.rubric_scores or {}
    submission.verified_by_id = current_user.id
    submission.verified_at = datetime.datetime.utcnow()

    db.commit()
    return {
        "message": f"Experiment status updated to '{submission.status}'",
        "status": submission.status,
        "faculty_marks": submission.faculty_marks
    }

# ==================== Practical Skill Verification: Viva Voce (Module 11) ====================
@router.post("/{submission_id}/viva/submit", response_model=VivaAssessmentOut)
def submit_viva_answers(
    submission_id: int,
    req: VivaSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submits student text answers to personalized viva questions.
    Evaluates conceptual understanding with IBM Granite and stores report.
    """
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    exp_title = submission.experiment.title if submission.experiment else "Experiment"
    answers_dicts = [a.dict() for a in req.answers]

    evaluation = watsonx_service.evaluate_viva_answers(
        experiment_title=exp_title,
        qa_list=answers_dicts
    )

    assessment = db.query(VivaAssessment).filter(VivaAssessment.submission_id == submission_id).first()
    if not assessment:
        assessment = VivaAssessment(
            submission_id=submission_id,
            student_id=submission.student_id,
            experiment_id=submission.experiment_id,
            qa_records=evaluation["qa_records"],
            total_score=evaluation["total_score"],
            max_score=10.0,
            overall_understanding=evaluation["overall_understanding"],
            ai_summary=evaluation["ai_summary"]
        )
        db.add(assessment)
    else:
        assessment.qa_records = evaluation["qa_records"]
        assessment.total_score = evaluation["total_score"]
        assessment.overall_understanding = evaluation["overall_understanding"]
        assessment.ai_summary = evaluation["ai_summary"]

    db.commit()
    db.refresh(assessment)
    return assessment

@router.get("/{submission_id}/viva", response_model=Optional[VivaAssessmentOut])
def get_viva_assessment(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves practical skill viva assessment results for student and faculty"""
    assessment = db.query(VivaAssessment).filter(VivaAssessment.submission_id == submission_id).first()
    return assessment
