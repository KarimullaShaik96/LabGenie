import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.seed import seed_database
from app.services.compiler_service import compiler_service
from app.services.circuit_service import circuit_simulator
from app.services.watsonx_service import watsonx_service

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db)
    db.close()

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert "watsonx_configured" in response.json()
    assert "mode" in response.json()

def test_auth_register_new_student():
    import uuid
    unique_email = f"student_{uuid.uuid4().hex[:6]}@labgenie.edu"
    response = client.post("/api/auth/register", json={
        "name": "Rohan Deshmukh",
        "email": unique_email,
        "password": "secretpassword",
        "role": "student",
        "department": "Computer Science & Engineering",
        "roll_or_emp_id": "21CS105"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Rohan Deshmukh"
    assert data["email"] == unique_email
    assert data["role"] == "student"

    # Verify student can immediately login
    login_res = client.post("/api/auth/login", json={
        "email": unique_email,
        "password": "secretpassword"
    })
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data
    assert login_data["user"]["name"] == "Rohan Deshmukh"

def test_auth_register_with_frontend_form_fields():
    import uuid
    unique_email = f"student_{uuid.uuid4().hex[:6]}@labgenie.edu"
    response = client.post("/api/auth/register", json={
        "full_name": "Ananya Kulkarni",
        "email": unique_email,
        "password": "secretpassword123",
        "department": "CSE",
        "roll_number": "21CS112",
        "semester": 5,
        "section": "B",
        "role": "student"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Ananya Kulkarni"
    assert data["email"] == unique_email
    assert data["roll_or_emp_id"] == "21CS112"

def test_auth_register_duplicate_email():
    response = client.post("/api/auth/register", json={
        "full_name": "Duplicate User",
        "email": "student@labgenie.edu",
        "password": "password123",
        "department": "CSE"
    })
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()

def test_auth_login_student():
    response = client.post("/api/auth/login", json={
        "email": "student@labgenie.edu",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "student"
    assert data["user"]["name"] == "Aarav Sharma"

def test_auth_login_faculty():
    response = client.post("/api/auth/login", json={
        "email": "faculty@labgenie.edu",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["role"] == "faculty"

def test_auth_login_hod():
    response = client.post("/api/auth/login", json={
        "email": "hod@labgenie.edu",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["role"] == "hod"

def test_courses_list():
    login_res = client.post("/api/auth/login", json={
        "email": "student@labgenie.edu",
        "password": "password123"
    })
    token = login_res.json()["access_token"]
    
    response = client.get("/api/courses", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) >= 3
    codes = [c["code"] for c in courses]
    assert "CS301" in codes
    assert "EC204" in codes

def test_ai_manual_generator_demo_mode():
    login_res = client.post("/api/auth/login", json={
        "email": "faculty@labgenie.edu",
        "password": "password123"
    })
    token = login_res.json()["access_token"]

    response = client.post("/api/manuals/generate", json={
        "course_code": "CS301",
        "course_name": "Data Structures Lab",
        "experiment_title": "Merge Sort Algorithm",
        "experiment_number": 4,
        "syllabus_topic": "Divide and Conquer",
        "available_equipment": "Python 3.12, VS Code",
        "lab_type": "coding",
        "programming_language": "python",
        "use_rag": False
    }, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert "aim" in data
    assert "theory" in data
    assert "procedure" in data
    assert "viva_questions" in data
    assert len(data["viva_questions"]) >= 2
    # Requirement: Clearly indicate demo mode when IBM credentials are not configured
    assert data["is_demo_mode"] is True or ("IBM Granite" in data["model_used"])

def test_compiler_python_execution():
    code = "print(sum([1, 2, 3, 4, 5]))"
    res = compiler_service.execute_code(language="python", code=code)
    assert res["status"] == "success"
    assert "15" in res["stdout"]

def test_compiler_sql_execution():
    sql = """
    CREATE TABLE test_scores (id INT, score INT);
    INSERT INTO test_scores VALUES (1, 95);
    INSERT INTO test_scores VALUES (2, 88);
    SELECT AVG(score) FROM test_scores;
    """
    res = compiler_service.execute_code(language="sql", code=sql)
    assert res["status"] == "success"
    assert "91.5" in res["stdout"]

def test_circuit_simulator_half_adder():
    preset_switches = [
        {"id": "sw_a", "label": "A", "state": 1},
        {"id": "sw_b", "label": "B", "state": 1}
    ]
    preset_gates = [
        {"id": "g_xor", "type": "XOR", "inputs": ["g_xor_in1", "g_xor_in2"], "output": "g_xor_out"},
        {"id": "g_and", "type": "AND", "inputs": ["g_and_in1", "g_and_in2"], "output": "g_and_out"}
    ]
    preset_leds = [
        {"id": "led_sum", "label": "Sum"},
        {"id": "led_carry", "label": "Carry"}
    ]
    preset_conns = [
        {"from_node": "sw_a", "to_node": "g_xor_in1"},
        {"from_node": "sw_b", "to_node": "g_xor_in2"},
        {"from_node": "sw_a", "to_node": "g_and_in1"},
        {"from_node": "sw_b", "to_node": "g_and_in2"},
        {"from_node": "g_xor_out", "to_node": "led_sum"},
        {"from_node": "g_and_out", "to_node": "led_carry"}
    ]

    sim = circuit_simulator.simulate(
        switches=preset_switches,
        gates=preset_gates,
        leds=preset_leds,
        connections=preset_conns,
        target_circuit_type="half_adder"
    )

    # 1 XOR 1 = 0 (Sum), 1 AND 1 = 1 (Carry)
    assert sim["output_states"]["led_sum"] == 0
    assert sim["output_states"]["led_carry"] == 1
    assert sim["is_valid"] is True
    assert len(sim["truth_table"]) == 4

def test_hod_analytics_endpoint():
    login_res = client.post("/api/auth/login", json={
        "email": "hod@labgenie.edu",
        "password": "password123"
    })
    token = login_res.json()["access_token"]

    response = client.get("/api/analytics/hod", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["total_courses"] >= 3
    assert data["lab_utilization_rate"] > 70
    assert len(data["courses_analytics"]) >= 3

def test_networks_subnet_and_ping():
    login_res = client.post("/api/auth/login", json={
        "email": "student@labgenie.edu",
        "password": "password123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test subnet calculator
    sub_res = client.post("/api/virtuallab/networks/subnet", json={
        "ip_address": "192.168.10.45",
        "cidr_prefix": 26
    }, headers=headers)
    assert sub_res.status_code == 200
    sub_data = sub_res.json()
    assert sub_data["network_address"] == "192.168.10.0"
    assert sub_data["total_hosts"] == 64
    assert sub_data["usable_hosts"] == 62
    assert sub_data["subnet_mask"] == "255.255.255.192"

    # Test ping simulation
    ping_res = client.post("/api/virtuallab/networks/ping", json={
        "source_node": "Host A (192.168.1.10)",
        "target_node": "Host B (10.0.0.5)",
        "topology_type": "routed_wan"
    }, headers=headers)
    assert ping_res.status_code == 200
    ping_data = ping_res.json()
    assert ping_data["packets_sent"] >= 1
    assert ping_data["success"] is True
    assert len(ping_data["hops"]) >= 2

def test_dbms_schema_and_query():
    login_res = client.post("/api/auth/login", json={
        "email": "student@labgenie.edu",
        "password": "password123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get Schema
    schema_res = client.get("/api/virtuallab/dbms/schema", headers=headers)
    assert schema_res.status_code == 200
    schema_data = schema_res.json()
    assert "students" in schema_data
    assert "courses" in schema_data

    # Execute query
    query_res = client.post("/api/virtuallab/dbms/execute", json={
        "sql": "SELECT name, gpa FROM students WHERE gpa >= 9.0"
    }, headers=headers)
    assert query_res.status_code == 200
    q_data = query_res.json()
    assert q_data["status"] == "success"
    assert q_data["row_count"] >= 1
    assert "name" in q_data["columns"]

def test_experiment_schedules():
    login_res = client.post("/api/auth/login", json={
        "email": "faculty@labgenie.edu",
        "password": "password123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/courses/schedules", headers=headers)
    assert response.status_code == 200
    schedules = response.json()
    assert len(schedules) >= 1
    assert schedules[0]["start_time"] is not None

def test_viva_assessment_flow():
    # Login student
    login_res = client.post("/api/auth/login", json={
        "email": "student@labgenie.edu",
        "password": "password123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get existing submission 1 viva
    viva_res = client.get("/api/submissions/1/viva", headers=headers)
    assert viva_res.status_code == 200
    viva_data = viva_res.json()
    assert "total_score" in viva_data
    assert viva_data["total_score"] > 0

def test_realtime_monitoring_telemetry():
    # Send student heartbeat
    s_login = client.post("/api/auth/login", json={
        "email": "student@labgenie.edu",
        "password": "password123"
    })
    s_token = s_login.json()["access_token"]
    hb_res = client.post("/api/monitoring/heartbeat", json={
        "experiment_id": 1,
        "active_tab": "compiler",
        "compilation_attempt": True,
        "run_success": True
    }, headers={"Authorization": f"Bearer {s_token}"})
    assert hb_res.status_code == 200

    # View live telemetry as faculty
    f_login = client.post("/api/auth/login", json={
        "email": "faculty@labgenie.edu",
        "password": "password123"
    })
    f_token = f_login.json()["access_token"]
    live_res = client.get("/api/monitoring/live", headers={"Authorization": f"Bearer {f_token}"})
    assert live_res.status_code == 200
    telemetry = live_res.json()
    assert isinstance(telemetry, list)
    assert len(telemetry) >= 1

def test_analytics_csv_export():
    login_res = client.post("/api/auth/login", json={
        "email": "hod@labgenie.edu",
        "password": "password123"
    })
    token = login_res.json()["access_token"]
    response = client.get("/api/analytics/export/csv", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "")
    assert "Course Code,Course Name" in response.text

def test_course_lab_record_pdf():
    login_res = client.post("/api/auth/login", json={
        "email": "student@labgenie.edu",
        "password": "password123"
    })
    token = login_res.json()["access_token"]
    # CS301 has ID 1
    response = client.get("/api/pdf/course-record/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/pdf"
    assert len(response.content) > 1000


