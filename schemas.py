from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import datetime

# ==================== User & Auth ====================
class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str = "student"
    department: Optional[str] = "Computer Science & Engineering"
    roll_or_emp_id: Optional[str] = None
    avatar_url: Optional[str] = None
    department_id: Optional[int] = None
    batch_id: Optional[int] = None

class UserCreate(BaseModel):
    name: Optional[str] = None
    full_name: Optional[str] = None
    email: EmailStr
    password: str
    role: Optional[str] = "student"
    department: Optional[str] = "Computer Science & Engineering"
    roll_or_emp_id: Optional[str] = None
    roll_number: Optional[str] = None
    semester: Optional[Any] = None
    section: Optional[str] = None
    employee_id: Optional[str] = None
    avatar_url: Optional[str] = None
    department_id: Optional[int] = None
    batch_id: Optional[int] = None

    def get_name(self) -> str:
        return (self.name or self.full_name or "").strip()

    def get_roll_or_emp_id(self) -> Optional[str]:
        return (self.roll_or_emp_id or self.roll_number or self.employee_id or "").strip() or None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    id: int
    created_at: datetime.datetime
    is_online: Optional[bool] = False
    last_active_at: Optional[datetime.datetime] = None
    help_requested: Optional[bool] = False
    help_note: Optional[str] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

# ==================== College & Batch Structures ====================
class CollegeOut(BaseModel):
    id: int
    name: str
    code: str
    address: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class DepartmentOut(BaseModel):
    id: int
    college_id: Optional[int] = None
    name: str
    code: str
    hod_id: Optional[int] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class StudentBatchOut(BaseModel):
    id: int
    name: str
    department_id: Optional[int] = None
    semester_id: Optional[int] = None
    academic_year: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class LabRoomOut(BaseModel):
    id: int
    name: str
    room_number: str
    capacity: int
    department_id: Optional[int] = None
    equipment_summary: Optional[str] = None
    is_active: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class ExperimentScheduleCreate(BaseModel):
    experiment_id: int
    batch_id: Optional[int] = None
    lab_room_id: Optional[int] = None
    faculty_id: Optional[int] = None
    scheduled_date: Optional[datetime.datetime] = None
    start_time: Optional[str] = "09:00 AM"
    end_time: Optional[str] = "12:00 PM"
    submission_deadline: Optional[datetime.datetime] = None
    status: Optional[str] = "scheduled"
    instructions: Optional[str] = None

class ExperimentScheduleOut(BaseModel):
    id: int
    experiment_id: int
    batch_id: Optional[int] = None
    batch_name: Optional[str] = None
    lab_room_id: Optional[int] = None
    lab_room_name: Optional[str] = None
    faculty_id: Optional[int] = None
    faculty_name: Optional[str] = None
    scheduled_date: Optional[datetime.datetime] = None
    start_time: str
    end_time: str
    submission_deadline: Optional[datetime.datetime] = None
    status: str
    instructions: Optional[str] = None
    experiment_title: Optional[str] = None

    class Config:
        from_attributes = True

# ==================== Course ====================
class CourseBase(BaseModel):
    code: str
    name: str
    department: str = "Computer Science & Engineering"
    semester: str = "Semester 5"
    academic_year: str = "2025-2026"
    description: Optional[str] = None
    lab_type: str = "coding"

class CourseCreate(CourseBase):
    syllabus_text: Optional[str] = None
    faculty_id: Optional[int] = None
    batch_ids: Optional[List[int]] = []

class CourseUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    department: Optional[str] = None
    semester: Optional[str] = None
    academic_year: Optional[str] = None
    description: Optional[str] = None
    syllabus_text: Optional[str] = None
    lab_type: Optional[str] = None
    faculty_id: Optional[int] = None

class CourseOut(CourseBase):
    id: int
    faculty_id: Optional[int] = None
    syllabus_text: Optional[str] = None
    syllabus_pdf_path: Optional[str] = None
    created_at: datetime.datetime
    faculty_name: Optional[str] = None
    total_experiments: Optional[int] = 0
    total_students: Optional[int] = 0

    class Config:
        from_attributes = True

# ==================== Experiment ====================
class VivaQuestion(BaseModel):
    question: str
    answer: str
    difficulty: Optional[str] = "Medium"

class RubricItem(BaseModel):
    criteria: str
    max_marks: float
    description: str

class SourceReference(BaseModel):
    title: str
    source_type: str  # 'syllabus_doc', 'textbook', 'standard_curriculum'
    excerpt: Optional[str] = None

class ExperimentBase(BaseModel):
    course_id: int
    experiment_number: int
    title: str
    syllabus_topic: Optional[str] = None
    equipment_needed: Optional[str] = None
    lab_type: str = "coding"
    programming_language: str = "python"
    deadline: Optional[datetime.datetime] = None
    max_marks: Optional[float] = 25.0
    aim: Optional[str] = None
    learning_objectives: Optional[str] = None
    theory: Optional[str] = None
    algorithm: Optional[str] = None
    procedure: Optional[str] = None
    source_code: Optional[str] = None
    circuit_instructions: Optional[str] = None
    expected_output: Optional[str] = None
    observations: Optional[str] = None
    result: Optional[str] = None
    safety_instructions: Optional[str] = None
    viva_questions: Optional[List[Dict[str, Any]]] = []
    rubric: Optional[List[Dict[str, Any]]] = []
    source_references: Optional[List[Dict[str, Any]]] = []
    is_verified_by_faculty: Optional[bool] = True

class ExperimentCreate(ExperimentBase):
    is_ai_generated: Optional[bool] = False

class ExperimentUpdate(BaseModel):
    title: Optional[str] = None
    syllabus_topic: Optional[str] = None
    equipment_needed: Optional[str] = None
    lab_type: Optional[str] = None
    programming_language: Optional[str] = None
    deadline: Optional[datetime.datetime] = None
    max_marks: Optional[float] = None
    aim: Optional[str] = None
    learning_objectives: Optional[str] = None
    theory: Optional[str] = None
    algorithm: Optional[str] = None
    procedure: Optional[str] = None
    source_code: Optional[str] = None
    circuit_instructions: Optional[str] = None
    expected_output: Optional[str] = None
    observations: Optional[str] = None
    result: Optional[str] = None
    safety_instructions: Optional[str] = None
    viva_questions: Optional[List[Dict[str, Any]]] = None
    rubric: Optional[List[Dict[str, Any]]] = None
    source_references: Optional[List[Dict[str, Any]]] = None
    is_verified_by_faculty: Optional[bool] = None

class ExperimentOut(ExperimentBase):
    id: int
    is_ai_generated: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    course_name: Optional[str] = None
    course_code: Optional[str] = None

    class Config:
        from_attributes = True

# ==================== AI Lab Manual Generator ====================
class ManualGenerateRequest(BaseModel):
    course_id: Optional[int] = None
    course_code: str
    course_name: str
    experiment_title: str
    experiment_number: int
    syllabus_topic: str
    available_equipment: str
    lab_type: str = "coding"
    programming_language: Optional[str] = "python"
    use_rag: bool = True

class ManualGenerateResponse(BaseModel):
    aim: str
    learning_objectives: str
    theory: str
    required_equipment: str
    algorithm: str
    procedure: str
    source_code_or_circuit: str
    expected_output: str
    observations: str
    result: str
    safety_instructions: str
    viva_questions: List[Dict[str, Any]]
    evaluation_rubric: List[Dict[str, Any]]
    source_references: List[Dict[str, Any]]
    is_demo_mode: bool
    model_used: str

# ==================== Online Compiler ====================
class TestCase(BaseModel):
    input: str
    expected_output: str

class TestCaseResult(BaseModel):
    input: str
    expected_output: str
    actual_output: str
    passed: bool

class CodeExecutionRequest(BaseModel):
    language: str
    code: str
    stdin: Optional[str] = ""
    test_cases: Optional[List[TestCase]] = []
    experiment_id: Optional[int] = None
    submission_id: Optional[int] = None

class CodeExecutionResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float
    memory_used: float
    status: str  # success, compilation_error, runtime_error, timeout, service_unavailable
    test_case_results: Optional[List[TestCaseResult]] = []
    is_mock_sandbox: bool = False
    runner_engine: str = "Judge0 / Local Sandbox"

# ==================== Virtual Lab: Digital Electronics ====================
class LogicGate(BaseModel):
    id: str
    type: str  # 'AND', 'OR', 'NOT', 'NAND', 'NOR', 'XOR', 'XNOR'
    x: float
    y: float
    inputs: List[str]
    output: str

class InputSwitch(BaseModel):
    id: str
    label: str
    state: int
    x: float
    y: float

class OutputLED(BaseModel):
    id: str
    label: str
    x: float
    y: float

class WireConnection(BaseModel):
    from_node: str
    to_node: str

class CircuitSimulationRequest(BaseModel):
    experiment_id: Optional[int] = None
    switches: List[InputSwitch]
    gates: List[LogicGate]
    leds: List[OutputLED]
    connections: List[WireConnection]
    target_circuit_type: Optional[str] = None

class CircuitSimulationResponse(BaseModel):
    output_states: Dict[str, int]
    wire_signals: Dict[str, int]
    truth_table: List[Dict[str, Any]]
    is_valid: bool
    validation_message: str
    target_verification: Optional[Dict[str, Any]] = None

# ==================== Virtual Lab: Computer Networks ====================
class NetworkSubnetRequest(BaseModel):
    ip_address: str  # e.g., "192.168.1.0"
    cidr_prefix: int  # e.g., 26

class NetworkSubnetResponse(BaseModel):
    ip_address: str
    cidr: int
    subnet_mask: str
    network_address: str
    broadcast_address: str
    total_hosts: int
    usable_hosts: int
    usable_range: str
    binary_mask: str
    ip_class: str

class NetworkPingRequest(BaseModel):
    source_node: str  # e.g., "Host A (192.168.1.10)"
    target_node: str  # e.g., "Host B (10.0.0.5)"
    topology_type: str = "routed_wan"  # 'routed_wan', 'lan_switch', 'star_topology'

class NetworkPingResponse(BaseModel):
    packets_sent: int
    packets_received: int
    packet_loss_percent: float
    average_rtt_ms: float
    hops: List[Dict[str, Any]]
    success: bool
    log_output: str

# ==================== Virtual Lab: DBMS SQL ====================
class SQLExecuteRequest(BaseModel):
    sql: str
    experiment_id: Optional[int] = None
    submission_id: Optional[int] = None

class SQLExecuteResponse(BaseModel):
    columns: List[str]
    rows: List[List[Any]]
    row_count: int
    execution_time: float
    status: str
    message: Optional[str] = None
    schema_tables: Optional[Dict[str, List[str]]] = None

# ==================== AI Lab Copilot ====================
class CopilotRequest(BaseModel):
    prompt: str
    mode: str = "general"  # 'debug', 'concept', 'step_guide', 'compare_output', 'viva_question', 'report_help'
    language: Optional[str] = "python"
    code: Optional[str] = None
    experiment_title: Optional[str] = None
    experiment_context: Optional[str] = None
    error_message: Optional[str] = None
    actual_output: Optional[str] = None
    expected_output: Optional[str] = None
    use_rag: Optional[bool] = True

class CopilotResponse(BaseModel):
    reply: str
    debug_hints: Optional[List[str]] = []
    suggested_fix: Optional[str] = None
    personalized_viva: Optional[List[Dict[str, str]]] = []
    rag_sources: Optional[List[Dict[str, Any]]] = []
    is_demo_mode: bool
    model_used: str

# ==================== Submission ====================
class SubmissionBase(BaseModel):
    experiment_id: int
    submitted_code: Optional[str] = None
    submitted_circuit_data: Optional[Dict[str, Any]] = None
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    observations: Optional[str] = None
    result: Optional[str] = None
    status: Optional[str] = "in_progress"

class SubmissionCreate(SubmissionBase):
    pass

class SubmissionUpdate(BaseModel):
    submitted_code: Optional[str] = None
    submitted_circuit_data: Optional[Dict[str, Any]] = None
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    observations: Optional[str] = None
    result: Optional[str] = None
    status: Optional[str] = None

class FacultyVerifyRequest(BaseModel):
    status: str  # 'verified' or 'correction_required'
    faculty_comments: Optional[str] = None
    faculty_marks: Optional[float] = None
    rubric_scores: Optional[Dict[str, float]] = None

class SubmissionOut(SubmissionBase):
    id: int
    student_id: int
    student_name: Optional[str] = None
    student_roll: Optional[str] = None
    experiment_title: Optional[str] = None
    experiment_number: Optional[int] = None
    course_name: Optional[str] = None
    course_code: Optional[str] = None
    faculty_comments: Optional[str] = None
    faculty_marks: Optional[float] = None
    rubric_scores: Optional[Dict[str, Any]] = None
    ai_evaluation: Optional[Dict[str, Any]] = None
    verified_by_name: Optional[str] = None
    submitted_at: Optional[datetime.datetime] = None
    verified_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    deadline: Optional[datetime.datetime] = None
    is_overdue: Optional[bool] = False

    class Config:
        from_attributes = True

# ==================== Viva Voce Practical Assessment (Module 11) ====================
class VivaAnswerItem(BaseModel):
    question_id: int
    question: str
    student_answer: str

class VivaSubmitRequest(BaseModel):
    submission_id: int
    answers: List[VivaAnswerItem]

class VivaAssessmentOut(BaseModel):
    id: int
    submission_id: int
    student_id: int
    experiment_id: int
    qa_records: List[Dict[str, Any]]
    total_score: float
    max_score: float
    overall_understanding: str
    ai_summary: Optional[str] = None
    faculty_reviewed: bool
    faculty_remarks: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# ==================== Real-Time Lab Monitoring (Module 8) ====================
class LiveHeartbeatRequest(BaseModel):
    experiment_id: Optional[int] = None
    active_tab: Optional[str] = "compiler"
    compilation_attempt: Optional[bool] = False
    run_success: Optional[bool] = False
    needs_assistance: Optional[bool] = False
    assistance_note: Optional[str] = None

class LiveStudentActivityOut(BaseModel):
    student_id: int
    student_name: str
    student_roll: Optional[str] = None
    experiment_id: Optional[int] = None
    experiment_title: Optional[str] = None
    course_code: Optional[str] = None
    active_tab: str
    last_heartbeat: datetime.datetime
    is_active: bool
    compilation_attempts: int
    successful_runs: int
    failed_runs: int
    submission_status: str
    needs_assistance: bool
    assistance_note: Optional[str] = None

# ==================== Analytics ====================
class CourseAnalytics(BaseModel):
    course_id: int
    course_code: str
    course_name: str
    total_experiments: int
    enrolled_students: int
    total_submissions: int
    verified_submissions: int
    pending_submissions: int
    completion_rate: float
    average_marks: float

class HODDepartmentAnalytics(BaseModel):
    department: str
    total_students: int
    total_faculty: int
    total_courses: int
    total_experiments: int
    total_submissions: int
    verified_submissions: int
    pending_submissions: int
    overall_completion_rate: float
    average_department_marks: float
    lab_utilization_rate: float
    courses_analytics: List[CourseAnalytics]
    status_distribution: Dict[str, int]
    weekly_activity: List[Dict[str, Any]]
