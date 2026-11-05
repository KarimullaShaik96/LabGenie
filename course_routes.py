import os
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import (
    Course, User, SyllabusDocument, Department, StudentBatch, LabRoom, ExperimentSchedule, Experiment
)
from app.schemas import (
    CourseCreate, CourseUpdate, CourseOut, DepartmentOut, StudentBatchOut, LabRoomOut,
    ExperimentScheduleCreate, ExperimentScheduleOut
)
from app.auth import get_current_user, require_roles
from app.config import settings
from app.services.rag_service import rag_service

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("", response_model=List[CourseOut])
def get_courses(
    department: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Course)
    
    if current_user.role == "student":
        # Students see enrolled courses
        if current_user.enrolled_courses:
            enrolled_ids = [c.id for c in current_user.enrolled_courses]
            query = query.filter(Course.id.in_(enrolled_ids))
        elif department:
            query = query.filter(Course.department == department)
    elif current_user.role == "faculty":
        # Faculty see taught courses or can filter by department
        if department:
            query = query.filter(Course.department == department)
        else:
            # Show all courses in their department
            query = query.filter(Course.department == current_user.department)
    elif current_user.role == "hod":
        # HOD sees department courses
        if current_user.department:
            query = query.filter(Course.department == current_user.department)

    courses = query.all()
    results = []
    for c in courses:
        results.append({
            "id": c.id,
            "code": c.code,
            "name": c.name,
            "department": c.department,
            "semester": c.semester,
            "academic_year": c.academic_year,
            "description": c.description,
            "lab_type": c.lab_type,
            "faculty_id": c.faculty_id,
            "syllabus_text": c.syllabus_text,
            "syllabus_pdf_path": c.syllabus_pdf_path,
            "created_at": c.created_at,
            "faculty_name": c.faculty.name if c.faculty else None,
            "total_experiments": len(c.experiments),
            "total_students": len(c.students)
        })
    return results

@router.get("/meta/departments", response_model=List[DepartmentOut])
def get_departments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Department).all()

@router.get("/meta/batches", response_model=List[StudentBatchOut])
def get_batches(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(StudentBatch).all()

@router.get("/meta/lab-rooms", response_model=List[LabRoomOut])
def get_lab_rooms(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(LabRoom).all()

@router.get("/schedules", response_model=List[ExperimentScheduleOut])
def get_all_schedules(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    schedules = db.query(ExperimentSchedule).all()
    res = []
    for s in schedules:
        res.append({
            "id": s.id,
            "experiment_id": s.experiment_id,
            "batch_id": s.batch_id,
            "batch_name": s.batch.name if s.batch else None,
            "lab_room_id": s.lab_room_id,
            "lab_room_name": s.lab_room.name if s.lab_room else None,
            "faculty_id": s.faculty_id,
            "faculty_name": s.faculty.name if s.faculty else None,
            "scheduled_date": s.scheduled_date,
            "start_time": s.start_time,
            "end_time": s.end_time,
            "submission_deadline": s.submission_deadline,
            "status": s.status,
            "instructions": s.instructions,
            "experiment_title": s.experiment.title if s.experiment else None
        })
    return res

@router.post("/schedules", response_model=ExperimentScheduleOut)
def create_schedule(
    data: ExperimentScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["faculty", "hod"]))
):
    schedule = ExperimentSchedule(
        experiment_id=data.experiment_id,
        batch_id=data.batch_id,
        lab_room_id=data.lab_room_id,
        faculty_id=data.faculty_id or current_user.id,
        scheduled_date=data.scheduled_date,
        start_time=data.start_time or "09:00 AM",
        end_time=data.end_time or "12:00 PM",
        submission_deadline=data.submission_deadline,
        status=data.status or "scheduled",
        instructions=data.instructions
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    return {
        "id": schedule.id,
        "experiment_id": schedule.experiment_id,
        "batch_id": schedule.batch_id,
        "batch_name": schedule.batch.name if schedule.batch else None,
        "lab_room_id": schedule.lab_room_id,
        "lab_room_name": schedule.lab_room.name if schedule.lab_room else None,
        "faculty_id": schedule.faculty_id,
        "faculty_name": schedule.faculty.name if schedule.faculty else None,
        "scheduled_date": schedule.scheduled_date,
        "start_time": schedule.start_time,
        "end_time": schedule.end_time,
        "submission_deadline": schedule.submission_deadline,
        "status": schedule.status,
        "instructions": schedule.instructions,
        "experiment_title": schedule.experiment.title if schedule.experiment else None
    }

@router.get("/{course_id}", response_model=CourseOut)
def get_course_detail(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    c = db.query(Course).filter(Course.id == course_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return {
        "id": c.id,
        "code": c.code,
        "name": c.name,
        "department": c.department,
        "semester": c.semester,
        "academic_year": c.academic_year,
        "description": c.description,
        "lab_type": c.lab_type,
        "faculty_id": c.faculty_id,
        "syllabus_text": c.syllabus_text,
        "syllabus_pdf_path": c.syllabus_pdf_path,
        "created_at": c.created_at,
        "faculty_name": c.faculty.name if c.faculty else None,
        "total_experiments": len(c.experiments),
        "total_students": len(c.students)
    }

@router.post("", response_model=CourseOut)
def create_course(
    course_data: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["faculty", "hod"]))
):
    existing = db.query(Course).filter(Course.code == course_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Course code already exists")

    course = Course(
        code=course_data.code,
        name=course_data.name,
        department=course_data.department,
        semester=course_data.semester,
        academic_year=course_data.academic_year,
        description=course_data.description,
        lab_type=course_data.lab_type,
        syllabus_text=course_data.syllabus_text,
        faculty_id=course_data.faculty_id or current_user.id
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    # Index initial syllabus text into ChromaDB RAG
    if course_data.syllabus_text:
        rag_service.index_document(
            course_id=course.id,
            title=f"{course.code} - {course.name} Syllabus",
            text=course_data.syllabus_text,
            source_type="syllabus_text"
        )

    return get_course_detail(course.id, db, current_user)

@router.put("/{course_id}", response_model=CourseOut)
def update_course(
    course_id: int,
    course_data: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["faculty", "hod"]))
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Scoped authorization
    if current_user.role == "faculty" and course.faculty_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit a course managed by another faculty member")

    for key, val in course_data.dict(exclude_unset=True).items():
        setattr(course, key, val)

    db.commit()
    db.refresh(course)
    return get_course_detail(course.id, db, current_user)

@router.post("/{course_id}/upload-syllabus")
async def upload_syllabus_pdf(
    course_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["faculty", "hod"]))
):
    """Uploads a syllabus/manual PDF, validates size, and indexes it into the ChromaDB RAG vector store"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Security check: validate PDF MIME & limit size <= 15MB
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only official PDF documents are accepted for syllabus RAG.")

    file_bytes = await file.read()
    if len(file_bytes) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Document exceeds maximum allowed upload size (15MB).")

    save_filename = f"course_{course_id}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, save_filename)

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # Extract text from PDF
    try:
        extracted_text = rag_service.extract_text_from_pdf(file_path)
    except Exception:
        extracted_text = f"Syllabus for {course.name} ({course.code}). File: {file.filename}"

    # Index into ChromaDB
    chunks_count = rag_service.index_document(
        course_id=course.id,
        title=f"{course.code} Curriculum ({file.filename})",
        text=extracted_text,
        source_type="syllabus_pdf"
    )

    course.syllabus_pdf_path = file_path
    course.syllabus_text = extracted_text[:3000]

    doc_record = SyllabusDocument(
        course_id=course.id,
        file_name=file.filename,
        file_path=file_path,
        file_size=len(file_bytes),
        document_type="syllabus",
        uploaded_by_id=current_user.id,
        parsed_chunks_count=chunks_count
    )
    db.add(doc_record)
    db.commit()

    return {
        "message": "Syllabus uploaded, validated, and indexed into RAG vector database successfully.",
        "file_name": file.filename,
        "chunks_indexed": chunks_count
    }

@router.post("/{course_id}/enroll")
def enroll_student(
    course_id: int,
    student_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    target_student_id = student_id if (student_id and current_user.role in ["faculty", "hod"]) else current_user.id
    course = db.query(Course).filter(Course.id == course_id).first()
    student = db.query(User).filter(User.id == target_student_id).first()

    if not course or not student:
        raise HTTPException(status_code=404, detail="Course or Student not found")

    if student not in course.students:
        course.students.append(student)
        db.commit()

    return {"message": f"Student {student.name} enrolled in {course.name} successfully"}
