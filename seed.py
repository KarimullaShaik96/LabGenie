import datetime
from sqlalchemy.orm import Session
from app.models import (
    User, Course, Experiment, Submission, ExecutionHistory, course_enrollments,
    College, Department, AcademicYear, Semester, StudentBatch, LabRoom,
    ExperimentSchedule, VivaAssessment, LiveLabActivity
)
from app.auth import get_password_hash
from app.services.rag_service import rag_service

def seed_database(db: Session):
    # Check if completely seeded
    if (
        db.query(College).first() and
        db.query(User).first() and
        db.query(Course).first() and
        db.query(Experiment).first() and
        db.query(ExperimentSchedule).first() and
        db.query(VivaAssessment).first()
    ):
        return

    print("Seeding LabGenie AI database with realistic engineering college ecosystem data...")

    # ================= 1. College & Department Hierarchy =================
    college = db.query(College).first()
    if not college:
        college = College(
            name="National Institute of Engineering & Technology",
            code="NIET",
            address="Knowledge Corridor, Tech Campus, Bengaluru, Karnataka 560064"
        )
        db.add(college)
        db.commit()
        db.refresh(college)

    dept = db.query(Department).first()
    if not dept:
        dept = Department(
            college_id=college.id,
            name="Computer Science & Engineering",
            code="CSE"
        )
        db.add(dept)
        db.commit()
        db.refresh(dept)

    # ================= 2. Academic Year & Semesters =================
    ay = db.query(AcademicYear).first()
    if not ay:
        ay = AcademicYear(name="2025-2026", is_current=True)
        db.add(ay)
        db.commit()
        db.refresh(ay)

    sem5 = db.query(Semester).filter(Semester.name == "Semester 5").first()
    if not sem5:
        sem5 = Semester(academic_year_id=ay.id, name="Semester 5", code="SEM5", is_active=True)
        sem3 = Semester(academic_year_id=ay.id, name="Semester 3", code="SEM3", is_active=False)
        sem4 = Semester(academic_year_id=ay.id, name="Semester 4", code="SEM4", is_active=False)
        db.add_all([sem5, sem3, sem4])
        db.commit()
        db.refresh(sem5)

    # ================= 3. Student Batches =================
    batch_a = db.query(StudentBatch).filter(StudentBatch.name == "CSE-Batch-A-2025").first()
    if not batch_a:
        batch_a = StudentBatch(
            name="CSE-Batch-A-2025",
            department_id=dept.id,
            semester_id=sem5.id,
            academic_year="2025-2026"
        )
        batch_b = StudentBatch(
            name="CSE-Batch-B-2025",
            department_id=dept.id,
            semester_id=sem5.id,
            academic_year="2025-2026"
        )
        db.add_all([batch_a, batch_b])
        db.commit()
        db.refresh(batch_a)

    # ================= 4. Physical Lab Rooms =================
    lab_room1 = db.query(LabRoom).filter(LabRoom.room_number == "CS-301").first()
    if not lab_room1:
        lab_room1 = LabRoom(
            name="Lab 301 - High Performance Computing Lab",
            room_number="CS-301",
            capacity=60,
            department_id=dept.id,
            equipment_summary="60x Intel Core i7 32GB RAM Workstations, Dual 27' Monitors, Gigabit LAN, 10Gbps Core Switch, Ubuntu 22.04 LTS dual boot.",
            is_active=True
        )
        db.add(lab_room1)
        db.commit()
        db.refresh(lab_room1)

    lab_room2 = db.query(LabRoom).filter(LabRoom.room_number == "CS-204").first()
    if not lab_room2:
        lab_room2 = LabRoom(
            name="Lab 204 - Hardware & Logic Simulation Lab",
            room_number="CS-204",
            capacity=40,
            department_id=dept.id,
            equipment_summary="40x Digital IC Trainer Kits, Xilinx FPGA Boards, Dual-Channel 50MHz Digital Storage Oscilloscopes, Function Generators.",
            is_active=True
        )
        db.add(lab_room2)
        db.commit()
        db.refresh(lab_room2)

    # ================= 5. Users =================
    pwd_hash = get_password_hash("password123")

    hod_user = db.query(User).filter(User.email == "hod@labgenie.edu").first()
    if not hod_user:
        hod_user = User(
            name="Dr. Sunita Deshmukh",
            email="hod@labgenie.edu",
            hashed_password=pwd_hash,
            role="hod",
            department="Computer Science & Engineering",
            department_id=dept.id,
            roll_or_emp_id="HOD-CSE-01",
            is_online=True,
            last_active_at=datetime.datetime.utcnow()
        )
        db.add(hod_user)
        db.commit()
        db.refresh(hod_user)
        # Update department HOD link
        dept.hod_id = hod_user.id
        db.commit()

    faculty_user = db.query(User).filter(User.email == "faculty@labgenie.edu").first()
    if not faculty_user:
        faculty_user = User(
            name="Dr. Rajesh Sharma",
            email="faculty@labgenie.edu",
            hashed_password=pwd_hash,
            role="faculty",
            department="Computer Science & Engineering",
            department_id=dept.id,
            roll_or_emp_id="FAC-CSE-104",
            is_online=True,
            last_active_at=datetime.datetime.utcnow()
        )
        db.add(faculty_user)
        db.commit()
        db.refresh(faculty_user)

    student_user = db.query(User).filter(User.email == "student@labgenie.edu").first()
    if not student_user:
        student_user = User(
            name="Aarav Sharma",
            email="student@labgenie.edu",
            hashed_password=pwd_hash,
            role="student",
            department="Computer Science & Engineering",
            department_id=dept.id,
            batch_id=batch_a.id,
            roll_or_emp_id="21CS042",
            is_online=True,
            last_active_at=datetime.datetime.utcnow()
        )
        db.add(student_user)
        db.commit()
        db.refresh(student_user)

    student2 = db.query(User).filter(User.email == "priya@labgenie.edu").first()
    if not student2:
        student2 = User(
            name="Priya Patel",
            email="priya@labgenie.edu",
            hashed_password=pwd_hash,
            role="student",
            department="Computer Science & Engineering",
            department_id=dept.id,
            batch_id=batch_a.id,
            roll_or_emp_id="21CS089",
            is_online=True,
            last_active_at=datetime.datetime.utcnow()
        )
        db.add(student2)
        db.commit()
        db.refresh(student2)

    # ================= 6. Courses =================
    c1 = db.query(Course).filter(Course.code == "CS301").first()
    if not c1:
        c1 = Course(
            code="CS301",
            name="Data Structures & Algorithms Laboratory",
            department="Computer Science & Engineering",
            department_id=dept.id,
            semester="Semester 5",
            academic_year="2025-2026",
            description="Comprehensive algorithmic laboratory covering sorting, balanced trees, graph traversal, dynamic programming, and asymptotic runtime analysis.",
            lab_type="coding",
            faculty_id=faculty_user.id,
            syllabus_text=(
                "Unit 1: Divide and Conquer Algorithms - QuickSort, MergeSort, runtime recurrences.\n"
                "Unit 2: Non-linear Data Structures - Binary Search Trees, AVL Trees, Heap priority queues.\n"
                "Unit 3: Graph Algorithms - BFS, DFS, Dijkstra's Single Source Shortest Path, Kruskal's MST.\n"
                "Unit 4: Dynamic Programming - 0/1 Knapsack, Longest Common Subsequence."
            )
        )
        c1.assigned_batches.append(batch_a)
        db.add(c1)

    c2 = db.query(Course).filter(Course.code == "EC204").first()
    if not c2:
        c2 = Course(
            code="EC204",
            name="Digital Electronics & Logic Design Lab",
            department="Computer Science & Engineering",
            department_id=dept.id,
            semester="Semester 3",
            academic_year="2025-2026",
            description="Hands-on laboratory simulation of Boolean algebra, fundamental and universal gates, combinational adder/subtractor logic, multiplexers, and flip-flops.",
            lab_type="digital_electronics",
            faculty_id=faculty_user.id,
            syllabus_text=(
                "Unit 1: Logic Gates & Boolean Algebra - AND, OR, NOT, NAND, NOR, XOR, XNOR truth tables.\n"
                "Unit 2: Combinational Logic Circuits - Half Adder, Full Adder, Ripple Carry Adders.\n"
                "Unit 3: Universal Logic - Realization of Boolean expressions using solely NAND/NOR gates.\n"
                "Unit 4: Data Selectors - 2:1 and 4:1 Multiplexers, Decoders, Encoders."
            )
        )
        c2.assigned_batches.append(batch_a)
        db.add(c2)

    c3 = db.query(Course).filter(Course.code == "CS402").first()
    if not c3:
        c3 = Course(
            code="CS402",
            name="Database Management Systems Lab",
            department="Computer Science & Engineering",
            department_id=dept.id,
            semester="Semester 4",
            academic_year="2025-2026",
            description="Practical relational database design, SQL DDL/DML, multi-table joins, nested aggregate queries, integrity constraints, and transaction processing.",
            lab_type="coding",
            faculty_id=faculty_user.id,
            syllabus_text=(
                "Unit 1: Relational Schema Design & DDL - CREATE, ALTER, DROP, primary/foreign keys.\n"
                "Unit 2: Data Manipulation (DML) - INSERT, UPDATE, DELETE, pattern matching with LIKE.\n"
                "Unit 3: Relational Joins & Aggregates - INNER, LEFT, RIGHT JOIN, GROUP BY, HAVING, ORDER BY.\n"
                "Unit 4: Subqueries and Views - Correlated subqueries, IN, EXISTS, CREATE VIEW."
            )
        )
        c3.assigned_batches.append(batch_a)
        db.add(c3)

    db.commit()
    db.refresh(c1)
    db.refresh(c2)
    db.refresh(c3)

    # Enroll students
    if student_user not in c1.students:
        c1.students.extend([student_user, student2])
    if student_user not in c2.students:
        c2.students.extend([student_user, student2])
    if student_user not in c3.students:
        c3.students.extend([student_user, student2])
    db.commit()

    # Index course syllabi into RAG
    rag_service.index_document(c1.id, f"{c1.code} Official Syllabus", c1.syllabus_text, "syllabus_text")
    rag_service.index_document(c2.id, f"{c2.code} Official Syllabus", c2.syllabus_text, "syllabus_text")
    rag_service.index_document(c3.id, f"{c3.code} Official Syllabus", c3.syllabus_text, "syllabus_text")

    # ================= 7. Experiments =================
    exp1 = db.query(Experiment).filter(Experiment.course_id == c1.id, Experiment.experiment_number == 1).first()
    if not exp1:
        exp1 = Experiment(
            course_id=c1.id,
            experiment_number=1,
            title="Implementation of QuickSort Algorithm and Time Complexity Analysis",
            syllabus_topic="Divide and Conquer Sorting Algorithms",
            equipment_needed="Python 3.12+ / GCC compiler, Monaco Web IDE, terminal",
            lab_type="coding",
            programming_language="python",
            aim="To implement the QuickSort divide-and-conquer algorithm in Python and analyze its average and worst case time complexity.",
            learning_objectives="1. Understand partition algorithms (Lomuto and Hoare).\n2. Implement recursive sorting.\n3. Verify O(n log n) average time complexity.",
            theory=(
                "QuickSort is an efficient in-place divide-and-conquer sorting algorithm. "
                "It works by selecting a 'pivot' element from the array and partitioning the other elements "
                "into two sub-arrays, according to whether they are less than or greater than the pivot. "
                "The sub-arrays are then sorted recursively."
            ),
            algorithm=(
                "1. If low < high:\n"
                "2.   pi = partition(arr, low, high)\n"
                "3.   quickSort(arr, low, pi - 1)\n"
                "4.   quickSort(arr, pi + 1, high)\n"
                "5. Partition chooses last element as pivot and places it in correct sorted position."
            ),
            procedure=(
                "1. Define the partition function choosing the pivot element.\n"
                "2. Rearrange the array elements smaller than pivot to left, greater to right.\n"
                "3. Recursively call quick_sort on left and right partitions.\n"
                "4. Test against standard test arrays and measure execution time."
            ),
            source_code=(
                "import sys\n\n"
                "def partition(arr, low, high):\n"
                "    pivot = arr[high]\n"
                "    i = low - 1\n"
                "    for j in range(low, high):\n"
                "        if arr[j] <= pivot:\n"
                "            i += 1\n"
                "            arr[i], arr[j] = arr[j], arr[i]\n"
                "    arr[i + 1], arr[high] = arr[high], arr[i + 1]\n"
                "    return i + 1\n\n"
                "def quick_sort(arr, low, high):\n"
                "    if low < high:\n"
                "        pi = partition(arr, low, high)\n"
                "        quick_sort(arr, low, pi - 1)\n"
                "        quick_sort(arr, pi + 1, high)\n\n"
                "if __name__ == '__main__':\n"
                "    raw = sys.stdin.read().strip()\n"
                "    data = [int(x) for x in raw.split()] if raw else [64, 34, 25, 12, 22, 11, 90]\n"
                "    print('Original Array:', data)\n"
                "    quick_sort(data, 0, len(data) - 1)\n"
                "    print('Sorted Array:  ', data)\n"
            ),
            expected_output=(
                "Original Array: [64, 34, 25, 12, 22, 11, 90]\n"
                "Sorted Array:   [11, 12, 22, 25, 34, 64, 90]"
            ),
            observations="Tested with 7 elements. Sorted in 0.04 ms. In-place auxiliary space O(log n) stack frames.",
            result="QuickSort algorithm was successfully implemented and verified with O(n log n) expected performance.",
            safety_instructions="Handle edge cases such as already sorted arrays to avoid O(n^2) stack overflow.",
            viva_questions=[
                {"question": "What is the worst-case time complexity of QuickSort?", "answer": "O(n^2), which happens when pivot is consistently the smallest or largest element (e.g. sorted array without random pivot).", "difficulty": "Medium"},
                {"question": "Is QuickSort a stable sorting algorithm?", "answer": "Standard QuickSort is not stable because swapping elements over long distances can alter relative order of duplicates.", "difficulty": "Medium"}
            ],
            rubric=[
                {"criteria": "Algorithm Design & Syntax", "max_marks": 10, "description": "Accurate partition logic and recursion"},
                {"criteria": "Execution & Test Cases", "max_marks": 10, "description": "Successful test runs on normal and boundary arrays"},
                {"criteria": "Viva Voce & Record", "max_marks": 5, "description": "Clear conceptual answers and timely submission"}
            ],
            source_references=[
                {"title": "CS301 Curriculum Unit 1", "source_type": "syllabus_doc", "excerpt": "Divide and conquer sorting algorithms."},
                {"title": "Introduction to Algorithms (CLRS 4th Ed.)", "source_type": "textbook", "excerpt": "Chapter 7: Quicksort and probabilistic analysis."}
            ],
            max_marks=25.0,
            deadline=datetime.datetime.utcnow() + datetime.timedelta(days=7),
            is_ai_generated=False,
            is_verified_by_faculty=True,
            created_by_id=faculty_user.id
        )
        db.add(exp1)

    exp2 = db.query(Experiment).filter(Experiment.course_id == c2.id, Experiment.experiment_number == 1).first()
    if not exp2:
        exp2 = Experiment(
            course_id=c2.id,
            experiment_number=1,
            title="Design and Realization of Half Adder & Full Adder using Logic Gates",
            syllabus_topic="Combinational Arithmetic Circuits",
            equipment_needed="Virtual Digital Electronics Simulator, IC 7486 (XOR), IC 7408 (AND), IC 7432 (OR)",
            lab_type="digital_electronics",
            programming_language="javascript",
            aim="To design, construct and verify the truth table of Half Adder and Full Adder circuits using digital logic gates.",
            learning_objectives="1. Deduce Boolean expressions for Sum and Carry.\n2. Wire XOR and AND gates in virtual lab.\n3. Validate output truth table.",
            theory=(
                "A Half Adder is a combinational circuit that performs binary addition of two 1-bit inputs (A and B). "
                "It produces two outputs: Sum (S = A XOR B) and Carry (C = A AND B). "
                "A Full Adder adds three 1-bit binary numbers (A, B, and Cin) with Sum = A XOR B XOR Cin "
                "and Carry = (A AND B) OR (Cin AND (A XOR B))."
            ),
            algorithm=(
                "1. Connect Input Switches A and B to XOR Gate 1.\n"
                "2. Connect XOR Gate 1 Output to LED Sum.\n"
                "3. Connect Input Switches A and B to AND Gate 1.\n"
                "4. Connect AND Gate 1 Output to LED Carry.\n"
                "5. Cycle through input binary combinations (00, 01, 10, 11) and record LED states."
            ),
            procedure=(
                "1. In the LabGenie Virtual Lab canvas, place Switch A and Switch B.\n"
                "2. Add a XOR gate and an AND gate from the component toolbar.\n"
                "3. Connect wires from switches to gate inputs.\n"
                "4. Route gate outputs to LED indicators for Sum and Carry.\n"
                "5. Click 'Run Simulation' to observe live propagation."
            ),
            circuit_instructions="Switch A -> XOR in1; Switch B -> XOR in2; XOR out -> LED Sum; Switch A -> AND in1; Switch B -> AND in2; AND out -> LED Carry.",
            expected_output=(
                "Truth Table:\n"
                "A | B | Sum | Carry\n"
                "0 | 0 |  0  |   0\n"
                "0 | 1 |  1  |   0\n"
                "1 | 0 |  1  |   0\n"
                "1 | 1 |  0  |   1"
            ),
            observations="All four input states matched the theoretical truth table. LEDs illuminated as expected.",
            result="The Half Adder circuit was successfully wired and verified in the virtual simulator.",
            safety_instructions="Ensure no floating input pins when translating to physical IC hardware.",
            viva_questions=[
                {"question": "Why cannot a half adder add three bits?", "answer": "A half adder only has two inputs and cannot accept a carry-in bit from a preceding lower-order stage.", "difficulty": "Easy"},
                {"question": "How many NAND gates are required to construct a Half Adder?", "answer": "5 two-input NAND gates are required to realize both Sum and Carry.", "difficulty": "Medium"}
            ],
            rubric=[
                {"criteria": "Circuit Topology & Wiring", "max_marks": 10, "description": "Accurate connections without floating pins"},
                {"criteria": "Truth Table Validation", "max_marks": 10, "description": "100% match on all 4 binary states"},
                {"criteria": "Viva Voce", "max_marks": 5, "description": "Understanding of combinational arithmetic"}
            ],
            source_references=[
                {"title": "EC204 Digital Design Lab Manual", "source_type": "syllabus_doc", "excerpt": "Unit 2: Combinational circuits"}
            ],
            max_marks=25.0,
            deadline=datetime.datetime.utcnow() + datetime.timedelta(days=10),
            is_ai_generated=False,
            is_verified_by_faculty=True,
            created_by_id=faculty_user.id
        )
        db.add(exp2)

    exp3 = db.query(Experiment).filter(Experiment.course_id == c3.id, Experiment.experiment_number == 1).first()
    if not exp3:
        exp3 = Experiment(
            course_id=c3.id,
            experiment_number=1,
            title="DDL and DML Operations on University Student Database",
            syllabus_topic="Relational Schema Design & SQL Queries",
            equipment_needed="Monaco SQL Workspace, SQLite / PostgreSQL engine",
            lab_type="coding",
            programming_language="sql",
            aim="To create relational tables with primary and foreign key constraints, insert sample student records, and execute DML queries.",
            learning_objectives="1. Write valid SQL DDL statements.\n2. Populate records with DML.\n3. Query data using conditions and ordering.",
            theory=(
                "Structured Query Language (SQL) is the standard language for relational databases. "
                "Data Definition Language (DDL) manages schema structures (CREATE, ALTER, DROP), "
                "while Data Manipulation Language (DML) manages data instances (INSERT, UPDATE, DELETE, SELECT)."
            ),
            algorithm=(
                "1. Define Students table with columns (id, name, department, gpa).\n"
                "2. Enforce PRIMARY KEY constraint on student id.\n"
                "3. Insert 4 records across multiple departments.\n"
                "4. Query students with GPA >= 8.5 ordered by name."
            ),
            procedure=(
                "1. Enter CREATE TABLE statement in SQL editor.\n"
                "2. Enter INSERT INTO statements.\n"
                "3. Enter SELECT query with WHERE and ORDER BY clauses.\n"
                "4. Click Run to view tabular output."
            ),
            source_code=(
                "CREATE TABLE students (\n"
                "    id INTEGER PRIMARY KEY,\n"
                "    name TEXT NOT NULL,\n"
                "    department TEXT NOT NULL,\n"
                "    gpa REAL\n"
                ");\n\n"
                "INSERT INTO students VALUES (1, 'Aarav Sharma', 'CSE', 9.1);\n"
                "INSERT INTO students VALUES (2, 'Priya Patel', 'CSE', 8.8);\n"
                "INSERT INTO students VALUES (3, 'Rohan Verma', 'ECE', 7.9);\n"
                "INSERT INTO students VALUES (4, 'Ananya Roy', 'AI&ML', 9.4);\n\n"
                "SELECT name, department, gpa FROM students WHERE gpa >= 8.5 ORDER BY gpa DESC;\n"
            ),
            expected_output=(
                "name | department | gpa\n"
                "-------------------------\n"
                "Ananya Roy | AI&ML | 9.4\n"
                "Aarav Sharma | CSE | 9.1\n"
                "Priya Patel | CSE | 8.8\n"
                "(3 rows returned)"
            ),
            observations="All 4 records inserted cleanly. SQL query filtered GPA >= 8.5 in descending order.",
            result="DDL table creation and DML relational queries executed and verified successfully.",
            safety_instructions="Always specify WHERE clauses on UPDATE and DELETE to prevent inadvertent data loss.",
            viva_questions=[
                {"question": "What is the difference between DROP, TRUNCATE, and DELETE?", "answer": "DROP removes table structure and data; TRUNCATE removes all rows without logging individual row deletes; DELETE removes specific rows according to a WHERE clause.", "difficulty": "Medium"}
            ],
            rubric=[
                {"criteria": "Schema Constraints", "max_marks": 10, "description": "Proper key definitions and data types"},
                {"criteria": "Query Correctness", "max_marks": 10, "description": "Correct rows filtered and sorted"},
                {"criteria": "Viva Voce", "max_marks": 5, "description": "Knowledge of ACID properties and relational algebra"}
            ],
            source_references=[
                {"title": "CS402 DBMS Lab Syllabus", "source_type": "syllabus_doc", "excerpt": "Unit 1: Schema definition"}
            ],
            max_marks=25.0,
            deadline=datetime.datetime.utcnow() + datetime.timedelta(days=14),
            is_ai_generated=False,
            is_verified_by_faculty=True,
            created_by_id=faculty_user.id
        )
        db.add(exp3)

    db.commit()
    db.refresh(exp1)
    db.refresh(exp2)
    db.refresh(exp3)

    # ================= 8. Experiment Schedules (Module 1 & 7) =================
    sch1 = db.query(ExperimentSchedule).filter(ExperimentSchedule.experiment_id == exp1.id).first()
    if not sch1:
        sch1 = ExperimentSchedule(
            experiment_id=exp1.id,
            batch_id=batch_a.id,
            lab_room_id=lab_room1.id,
            faculty_id=faculty_user.id,
            scheduled_date=datetime.datetime.utcnow() + datetime.timedelta(days=2),
            start_time="09:00 AM",
            end_time="12:00 PM",
            submission_deadline=datetime.datetime.utcnow() + datetime.timedelta(days=7),
            status="scheduled",
            instructions="Bring prepared algorithmic pseudo-code and test with boundary values (reversed arrays, duplicate keys)."
        )
        sch2 = ExperimentSchedule(
            experiment_id=exp2.id,
            batch_id=batch_a.id,
            lab_room_id=lab_room2.id,
            faculty_id=faculty_user.id,
            scheduled_date=datetime.datetime.utcnow() + datetime.timedelta(days=5),
            start_time="01:30 PM",
            end_time="04:30 PM",
            submission_deadline=datetime.datetime.utcnow() + datetime.timedelta(days=10),
            status="scheduled",
            instructions="Review XOR truth tables. Ensure LED current limiting resistors are understood conceptually."
        )
        db.add_all([sch1, sch2])
        db.commit()

    # ================= 9. Submissions =================
    sub1 = db.query(Submission).filter(Submission.experiment_id == exp1.id, Submission.student_id == student_user.id).first()
    if not sub1:
        sub1 = Submission(
            experiment_id=exp1.id,
            student_id=student_user.id,
            status="verified",
            submitted_code=exp1.source_code,
            input_data="64 34 25 12 22 11 90",
            output_data=exp1.expected_output,
            observations="QuickSort executed with Lomuto partitioning. Input array of 7 elements sorted in 0.042 ms.",
            result="Algorithm verified successfully against all test cases with O(n log n) runtime.",
            faculty_comments="Excellent code structure and clean recursion. Viva answers demonstrated thorough understanding of partition bounds.",
            faculty_marks=24.5,
            rubric_scores={"Algorithm Design & Syntax": 10.0, "Execution & Test Cases": 9.5, "Viva Voce & Record": 5.0},
            ai_evaluation={
                "preliminary_score": 24.0,
                "confidence_score": 0.94,
                "rubric_breakdown": {"Algorithm Design & Syntax": 10.0, "Execution & Test Cases": 9.5, "Viva Voce & Record": 4.5},
                "positive_highlights": ["Clean recursive base conditions", "Lomuto partition implemented without off-by-one errors"],
                "potential_issues": [],
                "suggested_comments": "Exceptional implementation. Pivot selection is well structured."
            },
            verified_by_id=faculty_user.id,
            submitted_at=datetime.datetime.utcnow() - datetime.timedelta(days=3),
            verified_at=datetime.datetime.utcnow() - datetime.timedelta(days=2)
        )
        db.add(sub1)

    sub2 = db.query(Submission).filter(Submission.experiment_id == exp2.id, Submission.student_id == student_user.id).first()
    if not sub2:
        sub2 = Submission(
            experiment_id=exp2.id,
            student_id=student_user.id,
            status="under_verification",
            submitted_code=exp2.circuit_instructions,
            submitted_circuit_data={
                "switches": [
                    {"id": "sw_a", "label": "Input A", "state": 1, "x": 60, "y": 80},
                    {"id": "sw_b", "label": "Input B", "state": 1, "x": 60, "y": 200}
                ],
                "gates": [
                    {"id": "g_xor", "type": "XOR", "x": 260, "y": 70, "inputs": ["g_xor_in1", "g_xor_in2"], "output": "g_xor_out"},
                    {"id": "g_and", "type": "AND", "x": 260, "y": 190, "inputs": ["g_and_in1", "g_and_in2"], "output": "g_and_out"}
                ],
                "leds": [
                    {"id": "led_sum", "label": "Sum (S)", "x": 480, "y": 75},
                    {"id": "led_carry", "label": "Carry (C)", "x": 480, "y": 195}
                ],
                "connections": [
                    {"from_node": "sw_a_out", "to_node": "g_xor_in1"},
                    {"from_node": "sw_b_out", "to_node": "g_xor_in2"},
                    {"from_node": "sw_a_out", "to_node": "g_and_in1"},
                    {"from_node": "sw_b_out", "to_node": "g_and_in2"},
                    {"from_node": "g_xor_out", "to_node": "led_sum_in"},
                    {"from_node": "g_and_out", "to_node": "led_carry_in"}
                ]
            },
            output_data="Truth Table Verified: (0,0)->(0,0), (0,1)->(1,0), (1,0)->(1,0), (1,1)->(0,1)",
            observations="Switch A and B set to 1 resulted in Sum=0 and Carry=1. Simulation validated against truth table.",
            result="Half Adder successfully realized using virtual gates.",
            ai_evaluation={
                "preliminary_score": 23.5,
                "confidence_score": 0.92,
                "rubric_breakdown": {"Circuit Topology & Wiring": 9.5, "Truth Table Validation": 10.0, "Viva Voce": 4.0},
                "positive_highlights": ["All 4 truth table states matched correctly", "Clear gate topology"],
                "potential_issues": [],
                "suggested_comments": "Circuit topology verified and tested with zero dangling connections."
            },
            submitted_at=datetime.datetime.utcnow() - datetime.timedelta(hours=6)
        )
        db.add(sub2)

    sub3 = db.query(Submission).filter(Submission.experiment_id == exp3.id, Submission.student_id == student_user.id).first()
    if not sub3:
        sub3 = Submission(
            experiment_id=exp3.id,
            student_id=student_user.id,
            status="in_progress",
            submitted_code=exp3.source_code,
            output_data=exp3.expected_output,
            observations="Drafting student schema and testing relational filters."
        )
        db.add(sub3)

    sub4 = db.query(Submission).filter(Submission.experiment_id == exp1.id, Submission.student_id == student2.id).first()
    if not sub4:
        sub4 = Submission(
            experiment_id=exp1.id,
            student_id=student2.id,
            status="verified",
            submitted_code=exp1.source_code,
            input_data="10 50 30 20 40",
            output_data="Sorted Array: [10, 20, 30, 40, 50]",
            observations="QuickSort executed on 5 values.",
            result="Sorted correctly.",
            faculty_comments="Good job, clean code.",
            faculty_marks=23.0,
            rubric_scores={"Algorithm Design & Syntax": 9.0, "Execution & Test Cases": 9.5, "Viva Voce & Record": 4.5},
            verified_by_id=faculty_user.id,
            submitted_at=datetime.datetime.utcnow() - datetime.timedelta(days=4),
            verified_at=datetime.datetime.utcnow() - datetime.timedelta(days=3)
        )
        db.add(sub4)

    db.commit()
    db.refresh(sub1)
    db.refresh(sub2)

    # ================= 10. Execution History =================
    h1 = db.query(ExecutionHistory).filter(ExecutionHistory.student_id == student_user.id).first()
    if not h1:
        h1 = ExecutionHistory(
            submission_id=sub1.id,
            student_id=student_user.id,
            experiment_id=exp1.id,
            language="python",
            code=exp1.source_code,
            stdin="64 34 25 12 22 11 90",
            stdout=exp1.expected_output,
            stderr="",
            exit_code=0,
            execution_time=0.042,
            memory_used=14.5,
            status="success"
        )
        db.add(h1)
        db.commit()

    # ================= 11. Viva Assessment (Module 11) =================
    va1 = db.query(VivaAssessment).filter(VivaAssessment.submission_id == sub1.id).first()
    if not va1:
        va1 = VivaAssessment(
            submission_id=sub1.id,
            student_id=student_user.id,
            experiment_id=exp1.id,
            qa_records=[
                {
                    "question_id": 1,
                    "question": "What is the worst-case time complexity of QuickSort?",
                    "student_answer": "The worst-case time complexity is O(n^2), occurring when the pivot picked is always the smallest or largest element.",
                    "score": 5.0,
                    "max_score": 5.0,
                    "ai_feedback": "Accurate explanation of quadratic complexity when partition splits become maximally unbalanced."
                },
                {
                    "question": "Is QuickSort a stable sorting algorithm?",
                    "student_answer": "QuickSort is not stable by default because long-range element swaps may invert relative order of duplicate items.",
                    "score": 4.5,
                    "max_score": 5.0,
                    "ai_feedback": "Very good understanding of stability caveats."
                }
            ],
            total_score=9.5,
            max_score=10.0,
            overall_understanding="Excellent",
            ai_summary="Student possesses solid conceptual mastery of asymptotic bounds, partitioning trade-offs, and in-place stability.",
            faculty_reviewed=True,
            faculty_remarks="Verified. Excellent grasp of partition bounds."
        )
        db.add(va1)
        db.commit()

    # ================= 12. Real-Time Telemetry Activities (Module 8) =================
    act1 = db.query(LiveLabActivity).filter(LiveLabActivity.student_id == student_user.id).first()
    if not act1:
        act1 = LiveLabActivity(
            student_id=student_user.id,
            experiment_id=exp1.id,
            active_tab="compiler",
            last_heartbeat=datetime.datetime.utcnow(),
            compilation_attempts=5,
            successful_runs=4,
            failed_runs=1,
            needs_assistance=False,
            assistance_note=None
        )
        act2 = LiveLabActivity(
            student_id=student2.id,
            experiment_id=exp2.id,
            active_tab="virtuallab",
            last_heartbeat=datetime.datetime.utcnow() - datetime.timedelta(minutes=1),
            compilation_attempts=3,
            successful_runs=2,
            failed_runs=1,
            needs_assistance=True,
            assistance_note="Clarification needed on XOR propagation delay."
        )
        db.add_all([act1, act2])
        db.commit()

    print("Database seeding completed successfully with all 17 Module entities.")
