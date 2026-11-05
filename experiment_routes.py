from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Experiment, Course, User
from app.schemas import ExperimentCreate, ExperimentUpdate, ExperimentOut
from app.auth import get_current_user, require_roles

router = APIRouter(prefix="/experiments", tags=["Experiments"])

@router.get("", response_model=List[ExperimentOut])
def get_experiments(
    course_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Experiment)
    
    # Scoped authorization
    if current_user.role == "student":
        query = query.filter(Experiment.is_verified_by_faculty == True)
        if current_user.enrolled_courses:
            enrolled_ids = [c.id for c in current_user.enrolled_courses]
            query = query.filter(Experiment.course_id.in_(enrolled_ids))
    elif current_user.role == "faculty":
        # Can see experiments for courses in their department
        pass

    if course_id:
        query = query.filter(Experiment.course_id == course_id)

    experiments = query.order_by(Experiment.experiment_number.asc()).all()
    results = []
    for exp in experiments:
        results.append({
            "id": exp.id,
            "course_id": exp.course_id,
            "experiment_number": exp.experiment_number,
            "title": exp.title,
            "syllabus_topic": exp.syllabus_topic,
            "equipment_needed": exp.equipment_needed,
            "lab_type": exp.lab_type,
            "programming_language": exp.programming_language,
            "deadline": exp.deadline,
            "max_marks": exp.max_marks,
            "aim": exp.aim,
            "learning_objectives": exp.learning_objectives,
            "theory": exp.theory,
            "algorithm": exp.algorithm,
            "procedure": exp.procedure,
            "source_code": exp.source_code,
            "circuit_instructions": exp.circuit_instructions,
            "expected_output": exp.expected_output,
            "observations": exp.observations,
            "result": exp.result,
            "safety_instructions": exp.safety_instructions,
            "viva_questions": exp.viva_questions or [],
            "rubric": exp.rubric or [],
            "source_references": exp.source_references or [],
            "is_ai_generated": exp.is_ai_generated,
            "is_verified_by_faculty": exp.is_verified_by_faculty,
            "created_at": exp.created_at,
            "updated_at": exp.updated_at,
            "course_name": exp.course.name if exp.course else None,
            "course_code": exp.course.code if exp.course else None
        })
    return results

@router.get("/{experiment_id}", response_model=ExperimentOut)
def get_experiment_detail(
    experiment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    return {
        "id": exp.id,
        "course_id": exp.course_id,
        "experiment_number": exp.experiment_number,
        "title": exp.title,
        "syllabus_topic": exp.syllabus_topic,
        "equipment_needed": exp.equipment_needed,
        "lab_type": exp.lab_type,
        "programming_language": exp.programming_language,
        "deadline": exp.deadline,
        "max_marks": exp.max_marks,
        "aim": exp.aim,
        "learning_objectives": exp.learning_objectives,
        "theory": exp.theory,
        "algorithm": exp.algorithm,
        "procedure": exp.procedure,
        "source_code": exp.source_code,
        "circuit_instructions": exp.circuit_instructions,
        "expected_output": exp.expected_output,
        "observations": exp.observations,
        "result": exp.result,
        "safety_instructions": exp.safety_instructions,
        "viva_questions": exp.viva_questions or [],
        "rubric": exp.rubric or [],
        "source_references": exp.source_references or [],
        "is_ai_generated": exp.is_ai_generated,
        "is_verified_by_faculty": exp.is_verified_by_faculty,
        "created_at": exp.created_at,
        "updated_at": exp.updated_at,
        "course_name": exp.course.name if exp.course else None,
        "course_code": exp.course.code if exp.course else None
    }

@router.post("", response_model=ExperimentOut)
def create_experiment(
    exp_data: ExperimentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["faculty", "hod"]))
):
    course = db.query(Course).filter(Course.id == exp_data.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Target course not found")

    # Scoped authorization
    if current_user.role == "faculty" and course.faculty_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to add experiments to another faculty's course")

    exp = Experiment(
        course_id=exp_data.course_id,
        experiment_number=exp_data.experiment_number,
        title=exp_data.title,
        syllabus_topic=exp_data.syllabus_topic,
        equipment_needed=exp_data.equipment_needed,
        lab_type=exp_data.lab_type or course.lab_type,
        programming_language=exp_data.programming_language,
        deadline=exp_data.deadline,
        max_marks=exp_data.max_marks or 25.0,
        aim=exp_data.aim,
        learning_objectives=exp_data.learning_objectives,
        theory=exp_data.theory,
        algorithm=exp_data.algorithm,
        procedure=exp_data.procedure,
        source_code=exp_data.source_code,
        circuit_instructions=exp_data.circuit_instructions,
        expected_output=exp_data.expected_output,
        observations=exp_data.observations,
        result=exp_data.result,
        safety_instructions=exp_data.safety_instructions,
        viva_questions=exp_data.viva_questions or [],
        rubric=exp_data.rubric or [],
        source_references=exp_data.source_references or [],
        is_ai_generated=exp_data.is_ai_generated,
        is_verified_by_faculty=exp_data.is_verified_by_faculty,
        created_by_id=current_user.id
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return get_experiment_detail(exp.id, db, current_user)

@router.put("/{experiment_id}", response_model=ExperimentOut)
def update_experiment(
    experiment_id: int,
    exp_data: ExperimentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["faculty", "hod"]))
):
    exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    for field, val in exp_data.dict(exclude_unset=True).items():
        setattr(exp, field, val)

    db.commit()
    db.refresh(exp)
    return get_experiment_detail(exp.id, db, current_user)

@router.put("/{experiment_id}/review-publish")
def review_and_publish_manual(
    experiment_id: int,
    is_approved: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["faculty", "hod"]))
):
    """Faculty reviews and approves an AI-generated manual for student visibility"""
    exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    exp.is_verified_by_faculty = is_approved
    db.commit()
    return {
        "message": f"Experiment manual {'published to students' if is_approved else 'kept in draft'}",
        "is_verified_by_faculty": exp.is_verified_by_faculty
    }
