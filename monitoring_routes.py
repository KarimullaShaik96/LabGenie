import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import User, LiveLabActivity, Experiment, Course
from app.schemas import LiveHeartbeatRequest, LiveStudentActivityOut
from app.auth import get_current_user, require_roles

router = APIRouter(prefix="/monitoring", tags=["Real-Time Lab Monitoring"])

@router.post("/heartbeat")
def record_heartbeat(
    req: LiveHeartbeatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Records student activity heartbeat inside LabGenie AI workspace.
    Maintains privacy: only monitors in-application actions.
    """
    now = datetime.datetime.utcnow()
    current_user.is_online = True
    current_user.last_active_at = now
    if req.experiment_id:
        current_user.current_experiment_id = req.experiment_id
    if req.needs_assistance is not None:
        current_user.help_requested = req.needs_assistance
        current_user.help_note = req.assistance_note

    # Update or insert LiveLabActivity record
    activity = db.query(LiveLabActivity).filter(LiveLabActivity.student_id == current_user.id).first()
    if not activity:
        activity = LiveLabActivity(
            student_id=current_user.id,
            experiment_id=req.experiment_id,
            active_tab=req.active_tab or "compiler",
            last_heartbeat=now,
            compilation_attempts=1 if req.compilation_attempt else 0,
            successful_runs=1 if req.run_success else 0,
            failed_runs=1 if (req.compilation_attempt and not req.run_success) else 0,
            needs_assistance=req.needs_assistance or False,
            assistance_note=req.assistance_note
        )
        db.add(activity)
    else:
        activity.last_heartbeat = now
        if req.experiment_id:
            activity.experiment_id = req.experiment_id
        if req.active_tab:
            activity.active_tab = req.active_tab
        if req.compilation_attempt:
            activity.compilation_attempts += 1
            if req.run_success:
                activity.successful_runs += 1
            else:
                activity.failed_runs += 1
        if req.needs_assistance is not None:
            activity.needs_assistance = req.needs_assistance
            activity.assistance_note = req.assistance_note

    db.commit()
    return {"status": "heartbeat_acknowledged", "timestamp": now.isoformat()}

@router.get("/live", response_model=List[LiveStudentActivityOut])
def get_live_lab_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["faculty", "hod"]))
):
    """
    Retrieves real-time active students in laboratory sessions (Module 8).
    Shows compilation attempts, successes/failures, active experiment, and students requesting assistance.
    """
    cutoff_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
    
    # Query students who have active records
    activities = db.query(LiveLabActivity).all()
    results = []

    for act in activities:
        student = act.student
        if not student:
            continue

        # Check if student is active within recent window
        is_active = bool(act.last_heartbeat and act.last_heartbeat >= cutoff_time)
        exp = db.query(Experiment).filter(Experiment.id == act.experiment_id).first() if act.experiment_id else None

        results.append({
            "student_id": student.id,
            "student_name": student.name,
            "student_roll": student.roll_or_emp_id,
            "experiment_id": act.experiment_id,
            "experiment_title": exp.title if exp else "Online Coding Workspace",
            "course_code": exp.course.code if exp and exp.course else "CS301",
            "active_tab": act.active_tab,
            "last_heartbeat": act.last_heartbeat,
            "is_active": is_active,
            "compilation_attempts": act.compilation_attempts,
            "successful_runs": act.successful_runs,
            "failed_runs": act.failed_runs,
            "submission_status": "In Progress" if is_active else "Idle",
            "needs_assistance": act.needs_assistance,
            "assistance_note": act.assistance_note
        })

    # Sort assistance requests to the top
    results.sort(key=lambda x: (not x["needs_assistance"], not x["is_active"], x["last_heartbeat"]), reverse=False)
    return results

@router.post("/resolve-help/{student_id}")
def resolve_assistance_request(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["faculty", "hod"]))
):
    """Faculty marks student assistance request as resolved"""
    student = db.query(User).filter(User.id == student_id).first()
    if student:
        student.help_requested = False
        student.help_note = None

    act = db.query(LiveLabActivity).filter(LiveLabActivity.student_id == student_id).first()
    if act:
        act.needs_assistance = False
        act.assistance_note = None

    db.commit()
    return {"message": "Assistance request marked as resolved"}

