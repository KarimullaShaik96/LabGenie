from typing import Optional
import datetime
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Submission, User, Course, Experiment
from app.auth import get_current_user
from app.services.pdf_service import pdf_service
from app.routers.analytics_routes import get_hod_analytics

router = APIRouter(prefix="/pdf", tags=["PDF Generation"])

@router.get("/lab-record/{submission_id}")
def download_student_lab_record(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generates and downloads a complete, publication-ready Student Lab Record PDF
    containing Aim, Theory, Procedure, Code, Output, Observations, Result, and Faculty Verification.
    """
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    student = submission.student
    exp = submission.experiment

    student_info = {
        "name": student.name if student else current_user.name,
        "roll_or_emp_id": student.roll_or_emp_id if student else current_user.roll_or_emp_id,
        "department": student.department if student else current_user.department
    }

    experiment_data = {
        "course_code": exp.course.code if exp and exp.course else "CS301",
        "course_name": exp.course.name if exp and exp.course else "Laboratory",
        "experiment_number": exp.experiment_number if exp else 1,
        "title": exp.title if exp else "Experiment",
        "aim": exp.aim,
        "theory": exp.theory,
        "procedure": exp.procedure,
        "source_code": exp.source_code,
        "expected_output": exp.expected_output,
        "observations": exp.observations,
        "result": exp.result
    }

    submission_data = {
        "submitted_code": submission.submitted_code,
        "output_data": submission.output_data,
        "observations": submission.observations,
        "result": submission.result,
        "status": submission.status,
        "faculty_marks": submission.faculty_marks,
        "faculty_comments": submission.faculty_comments
    }

    pdf_bytes = pdf_service.generate_student_lab_record_pdf(
        student_info=student_info,
        experiment_data=experiment_data,
        submission_data=submission_data
    )

    clean_filename = f"LabRecord_Exp{experiment_data['experiment_number']}_{student_info['roll_or_emp_id'] or 'student'}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={clean_filename}"}
    )

@router.get("/hod-academic-report")
def download_hod_academic_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generates and exports department-wide laboratory audit report PDF for HOD and accreditation boards.
    """
    analytics_data = get_hod_analytics(db=db, current_user=current_user)
    pdf_bytes = pdf_service.generate_hod_academic_report_pdf(analytics_data.dict())

    clean_filename = f"HOD_Lab_Audit_Report_{datetime.datetime.now().strftime('%Y%m%d')}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={clean_filename}"}
    )

@router.get("/course-record/{course_id}")
def download_course_lab_record(
    course_id: int,
    student_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generates and downloads a complete Course Laboratory Record Book containing:
    Cover Page, Index Sheet with marks and verification dates, followed by all experiment chapters.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    target_student_id = current_user.id
    if current_user.role in ["faculty", "hod"] and student_id:
        target_student_id = student_id

    student = db.query(User).filter(User.id == target_student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Target student record not found")

    experiments = db.query(Experiment).filter(Experiment.course_id == course_id).order_by(Experiment.experiment_number.asc()).all()
    if not experiments:
        raise HTTPException(status_code=400, detail="No experiments found for this course to generate a record book")

    # Fetch submissions for each experiment
    experiments_data = []
    for exp in experiments:
        sub = db.query(Submission).filter(
            Submission.experiment_id == exp.id,
            Submission.student_id == target_student_id
        ).first()

        exp_dict = {
            "experiment_number": exp.experiment_number,
            "title": exp.title,
            "aim": exp.aim,
            "theory": exp.theory,
            "procedure": exp.procedure,
            "source_code": exp.source_code,
            "expected_output": exp.expected_output,
            "observations": exp.observations,
            "result": exp.result,
            "date": sub.submitted_at.strftime("%d/%m/%Y") if (sub and sub.submitted_at) else datetime.date.today().strftime("%d/%m/%Y"),
            "faculty_marks": sub.faculty_marks if sub else None,
            "status": sub.status if sub else "Not Started",
            "submitted_code": sub.submitted_code if sub else exp.source_code,
            "output_data": sub.output_data if sub else exp.expected_output,
            "student_observations": sub.observations if sub else exp.observations,
            "student_result": sub.result if sub else exp.result,
            "faculty_comments": sub.faculty_comments if sub else "Awaiting submission and verification."
        }
        experiments_data.append(exp_dict)

    student_info = {
        "name": student.name,
        "roll_or_emp_id": student.roll_or_emp_id or "21CS042",
        "department": student.department or "Computer Science & Engineering",
        "batch_name": student.batch.name if student.batch else "CSE-Batch-A-2025"
    }

    course_info = {
        "code": course.code,
        "name": course.name,
        "academic_year": "2025-2026",
        "semester": course.semester or "Semester 5",
        "faculty_name": course.faculty.name if course.faculty else "Dr. Rajesh Sharma"
    }

    pdf_bytes = pdf_service.generate_full_course_lab_record_pdf(
        student_info=student_info,
        course_info=course_info,
        experiments_data=experiments_data
    )

    clean_filename = f"Complete_Lab_Record_{course.code}_{student_info['roll_or_emp_id']}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={clean_filename}"}
    )

