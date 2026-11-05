import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, Table, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base

# Association table for Student course enrollments
course_enrollments = Table(
    'course_enrollments',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('course_id', Integer, ForeignKey('courses.id', ondelete='CASCADE'), primary_key=True)
)

# Association table for Batch course assignments
batch_course_assignments = Table(
    'batch_course_assignments',
    Base.metadata,
    Column('batch_id', Integer, ForeignKey('student_batches.id', ondelete='CASCADE'), primary_key=True),
    Column('course_id', Integer, ForeignKey('courses.id', ondelete='CASCADE'), primary_key=True)
)

class College(Base):
    __tablename__ = "colleges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True, index=True, nullable=False)
    address = Column(String(300), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    departments = relationship("Department", back_populates="college", cascade="all, delete-orphan")

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(150), nullable=False)  # e.g., "Computer Science & Engineering"
    code = Column(String(20), unique=True, index=True, nullable=False)  # e.g., "CSE"
    hod_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    college = relationship("College", back_populates="departments")
    batches = relationship("StudentBatch", back_populates="department")
    lab_rooms = relationship("LabRoom", back_populates="department")
    courses = relationship("Course", back_populates="department_rel")

class AcademicYear(Base):
    __tablename__ = "academic_years"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # e.g., "2025-2026"
    is_current = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    semesters = relationship("Semester", back_populates="academic_year")

class Semester(Base):
    __tablename__ = "semesters"

    id = Column(Integer, primary_key=True, index=True)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(50), nullable=False)  # e.g., "Semester 5"
    code = Column(String(20), nullable=True)   # e.g., "SEM5"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    academic_year = relationship("AcademicYear", back_populates="semesters")
    batches = relationship("StudentBatch", back_populates="semester")

class StudentBatch(Base):
    __tablename__ = "student_batches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # e.g., "CSE-Batch-A-2025"
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=True)
    semester_id = Column(Integer, ForeignKey("semesters.id", ondelete="SET NULL"), nullable=True)
    academic_year = Column(String(50), default="2025-2026")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    department = relationship("Department", back_populates="batches")
    semester = relationship("Semester", back_populates="batches")
    students = relationship("User", back_populates="batch")
    courses = relationship("Course", secondary=batch_course_assignments, back_populates="assigned_batches")
    schedules = relationship("ExperimentSchedule", back_populates="batch")

class LabRoom(Base):
    __tablename__ = "lab_rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)  # e.g., "Lab 301 - High Performance Computing Lab"
    room_number = Column(String(50), nullable=False)  # e.g., "CS-301"
    capacity = Column(Integer, default=60)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=True)
    equipment_summary = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    department = relationship("Department", back_populates="lab_rooms")
    schedules = relationship("ExperimentSchedule", back_populates="lab_room")

class ExperimentSchedule(Base):
    __tablename__ = "experiment_schedules"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False)
    batch_id = Column(Integer, ForeignKey("student_batches.id", ondelete="CASCADE"), nullable=True)
    lab_room_id = Column(Integer, ForeignKey("lab_rooms.id", ondelete="SET NULL"), nullable=True)
    faculty_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    scheduled_date = Column(DateTime, nullable=True)
    start_time = Column(String(20), default="09:00 AM")
    end_time = Column(String(20), default="12:00 PM")
    submission_deadline = Column(DateTime, nullable=True)
    status = Column(String(30), default="scheduled")  # scheduled, in_progress, completed
    instructions = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    experiment = relationship("Experiment", back_populates="schedules")
    batch = relationship("StudentBatch", back_populates="schedules")
    lab_room = relationship("LabRoom", back_populates="schedules")
    faculty = relationship("User", foreign_keys=[faculty_id])

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    role = Column(String(20), nullable=False, default="student")  # 'student', 'faculty', 'hod'
    department = Column(String(100), default="Computer Science & Engineering")
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    batch_id = Column(Integer, ForeignKey("student_batches.id", ondelete="SET NULL"), nullable=True)
    roll_or_emp_id = Column(String(50), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    
    # Real-time monitoring telemetry (Module 8)
    is_online = Column(Boolean, default=False)
    last_active_at = Column(DateTime, nullable=True)
    current_experiment_id = Column(Integer, nullable=True)
    help_requested = Column(Boolean, default=False)
    help_note = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    batch = relationship("StudentBatch", back_populates="students", foreign_keys=[batch_id])
    taught_courses = relationship("Course", back_populates="faculty", foreign_keys="Course.faculty_id")
    enrolled_courses = relationship("Course", secondary=course_enrollments, back_populates="students")
    submissions = relationship("Submission", back_populates="student", foreign_keys="Submission.student_id")
    executions = relationship("ExecutionHistory", back_populates="student")
    viva_assessments = relationship("VivaAssessment", back_populates="student", foreign_keys="VivaAssessment.student_id")
    live_activities = relationship("LiveLabActivity", back_populates="student")

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)  # e.g., CS301
    name = Column(String(150), nullable=False)                         # e.g., Data Structures & Algorithms Lab
    department = Column(String(100), default="Computer Science & Engineering")
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    semester = Column(String(20), default="Semester 5")
    academic_year = Column(String(20), default="2025-2026")
    description = Column(Text, nullable=True)
    syllabus_text = Column(Text, nullable=True)
    syllabus_pdf_path = Column(String(255), nullable=True)
    lab_type = Column(String(50), default="coding")  # 'coding', 'digital_electronics', 'networks', 'dbms'
    faculty_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    faculty = relationship("User", back_populates="taught_courses", foreign_keys=[faculty_id])
    department_rel = relationship("Department", back_populates="courses", foreign_keys=[department_id])
    students = relationship("User", secondary=course_enrollments, back_populates="enrolled_courses")
    assigned_batches = relationship("StudentBatch", secondary=batch_course_assignments, back_populates="courses")
    experiments = relationship("Experiment", back_populates="course", cascade="all, delete-orphan")
    documents = relationship("SyllabusDocument", back_populates="course", cascade="all, delete-orphan")

class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    experiment_number = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    syllabus_topic = Column(String(200), nullable=True)
    equipment_needed = Column(Text, nullable=True)
    lab_type = Column(String(50), default="coding")  # 'coding', 'digital_electronics', 'networks', 'dbms'
    programming_language = Column(String(50), default="python")  # 'c', 'cpp', 'python', 'java', 'sql', 'javascript', 'html'
    deadline = Column(DateTime, nullable=True)
    max_marks = Column(Float, default=25.0)

    # Lab Manual Sections
    aim = Column(Text, nullable=True)
    learning_objectives = Column(Text, nullable=True)
    theory = Column(Text, nullable=True)
    algorithm = Column(Text, nullable=True)
    procedure = Column(Text, nullable=True)
    source_code = Column(Text, nullable=True)
    circuit_instructions = Column(Text, nullable=True)
    expected_output = Column(Text, nullable=True)
    observations = Column(Text, nullable=True)
    result = Column(Text, nullable=True)
    safety_instructions = Column(Text, nullable=True)
    viva_questions = Column(JSON, default=list)        # list of {question, answer, difficulty}
    rubric = Column(JSON, default=list)                # list of {criteria, max_marks, description}
    source_references = Column(JSON, default=list)     # list of references / citations from RAG
    
    # Metadata
    is_ai_generated = Column(Boolean, default=False)
    is_verified_by_faculty = Column(Boolean, default=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    course = relationship("Course", back_populates="experiments")
    submissions = relationship("Submission", back_populates="experiment", cascade="all, delete-orphan")
    schedules = relationship("ExperimentSchedule", back_populates="experiment", cascade="all, delete-orphan")
    viva_assessments = relationship("VivaAssessment", back_populates="experiment", cascade="all, delete-orphan")

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Status: 'not_started', 'in_progress', 'submitted', 'under_verification', 'correction_required', 'verified'
    status = Column(String(30), default="in_progress")
    
    submitted_code = Column(Text, nullable=True)
    submitted_circuit_data = Column(JSON, nullable=True)  # Logic circuit nodes or Network simulation data
    input_data = Column(Text, nullable=True)
    output_data = Column(Text, nullable=True)
    observations = Column(Text, nullable=True)
    result = Column(Text, nullable=True)
    
    # Verification & Evaluation
    faculty_comments = Column(Text, nullable=True)
    faculty_marks = Column(Float, nullable=True)
    rubric_scores = Column(JSON, default=dict)           # e.g., {"Code Correctness": 8, "Viva": 5}
    ai_evaluation = Column(JSON, nullable=True)          # AI preliminary evaluation suggestions
    verified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    submitted_at = Column(DateTime, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    experiment = relationship("Experiment", back_populates="submissions")
    student = relationship("User", back_populates="submissions", foreign_keys=[student_id])
    verified_by = relationship("User", foreign_keys=[verified_by_id])
    execution_history = relationship("ExecutionHistory", back_populates="submission", cascade="all, delete-orphan")
    viva_assessment = relationship("VivaAssessment", back_populates="submission", uselist=False, cascade="all, delete-orphan")

class ExecutionHistory(Base):
    __tablename__ = "execution_history"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id", ondelete="SET NULL"), nullable=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    experiment_id = Column(Integer, ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False)
    language = Column(String(50), nullable=False)
    code = Column(Text, nullable=False)
    stdin = Column(Text, nullable=True)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    exit_code = Column(Integer, default=0)
    execution_time = Column(Float, default=0.0)
    memory_used = Column(Float, default=0.0)
    status = Column(String(50), default="success")  # success, compilation_error, runtime_error, timeout
    execution_engine = Column(String(100), default="Sandboxed Container")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    student = relationship("User", back_populates="executions")
    submission = relationship("Submission", back_populates="execution_history")

class SyllabusDocument(Base):
    __tablename__ = "syllabus_documents"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0)
    document_type = Column(String(50), default="syllabus")  # syllabus, manual, protocol, assessment_guideline
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    parsed_chunks_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    course = relationship("Course", back_populates="documents")

class VivaAssessment(Base):
    __tablename__ = "viva_assessments"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    experiment_id = Column(Integer, ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False)
    
    # JSON list of {question_id: 1, question: "...", answer: "...", student_answer: "...", score: 3.5, max_score: 5.0, ai_feedback: "..."}
    qa_records = Column(JSON, default=list)
    total_score = Column(Float, default=0.0)
    max_score = Column(Float, default=10.0)
    overall_understanding = Column(String(50), default="Good")  # Excellent, Good, Average, Needs Improvement
    ai_summary = Column(Text, nullable=True)
    faculty_reviewed = Column(Boolean, default=False)
    faculty_remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    submission = relationship("Submission", back_populates="viva_assessment")
    student = relationship("User", back_populates="viva_assessments", foreign_keys=[student_id])
    experiment = relationship("Experiment", back_populates="viva_assessments")

class LiveLabActivity(Base):
    __tablename__ = "live_lab_activities"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    experiment_id = Column(Integer, ForeignKey("experiments.id", ondelete="CASCADE"), nullable=True)
    active_tab = Column(String(50), default="compiler")  # manual, theory, compiler, virtuallab, observations, copilot
    last_heartbeat = Column(DateTime, default=datetime.datetime.utcnow)
    compilation_attempts = Column(Integer, default=0)
    successful_runs = Column(Integer, default=0)
    failed_runs = Column(Integer, default=0)
    needs_assistance = Column(Boolean, default=False)
    assistance_note = Column(String(255), nullable=True)

    # Relationships
    student = relationship("User", back_populates="live_activities")
