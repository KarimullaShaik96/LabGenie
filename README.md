# LabGenie AI – IBM Granite-Powered Intelligent Laboratory Ecosystem

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-blue.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-blue.svg)](https://www.typescriptlang.org/)
[![IBM Granite](https://img.shields.io/badge/IBM_Granite-3--8B--Instruct-indigo.svg)](https://www.ibm.com/granite)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-v4-38B2AC.svg)](https://tailwindcss.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

**LabGenie AI** is a modern, production-ready, full-stack laboratory management ecosystem designed specifically for engineering colleges and autonomous universities. The platform unites **AI-powered lab manual generation**, **multi-language online code compilation**, **interactive virtual simulations** (Digital Electronics, Computer Networks, DBMS SQL), **real-time faculty laboratory telemetry**, **AI-assisted student assessment**, **automated Viva Voce evaluation**, and **accreditation analytics** (NBA / NAAC / AICTE compliance) into one cohesive SaaS platform.

---

## 🌟 Complete 17-Module System Architecture

```mermaid
graph TD
    subgraph Frontend ["Frontend (React 19 + TypeScript + Vite + Tailwind CSS)"]
        SD["Student Dashboard & 8-Tab Workspace"]
        FD["Faculty Dashboard & Verification Queue"]
        HD["HOD Executive Analytics & Lab Utilization"]
        LTM["Live Telemetry Monitor (5s Polling)"]
        VL["Virtual Lab Suite (Digital, Networks, DBMS)"]
    end

    subgraph Backend ["Backend API (FastAPI + Python 3.12)"]
        Auth["JWT Authentication & RBAC"]
        CourseSvc["Course & Schedule Manager"]
        CompilerSvc["Judge0 & Sandboxed Execution Engine"]
        RAG["ChromaDB Vector Retrieval Engine"]
        WatsonX["IBM watsonx.ai Client (Granite 3-8B)"]
        LiveMon["Live Lab Activity Telemetry Hub"]
        PDFGen["ReportLab Course Record PDF Engine"]
    end

    subgraph DataStore ["Persistence Layer"]
        Postgres[(PostgreSQL / SQLite Database)]
        ChromaStore[(ChromaDB Vector Embeddings)]
        DiskStore["Generated PDFs & Syllabus Storage"]
    end

    SD -->|REST API| Auth
    FD -->|REST API| CourseSvc
    HD -->|REST API| LiveMon
    LTM -->|Heartbeat & Telemetry| LiveMon

    CourseSvc --> Postgres
    CompilerSvc -->|Isolated Run| Backend
    RAG --> ChromaStore
    WatsonX -->|Inference & Prompts| Backend
    PDFGen --> DiskStore
```

---

## 📋 Comprehensive Module Breakdown

### Module 1: College Lab Management Hierarchy
- Models: `College`, `Department`, `AcademicYear`, `Semester`, `StudentBatch`, `LabRoom`, and `ExperimentSchedule`.
- Scoped role-based access control: Students only access assigned batches and enrolled courses; faculty only manage assigned laboratories; HODs exercise department-wide oversight.

### Module 2: Student Dashboard & 8-Tab Experiment Workspace
The workspace provides a unified 8-tab workflow:
1. **Experiment Manual**: Aim, learning objectives, procedure, required equipment, and safety precautions.
2. **Theory & Concepts**: Mathematical equations, algorithmic background, and textbook citations.
3. **Online Compiler**: Monaco editor supporting 8 languages with standard input (stdin) and output terminal.
4. **Virtual Lab**: Real-time simulation testing.
5. **Observations**: Interactive observation table with trial rows, runtimes, and student conclusions.
6. **AI Lab Copilot**: IBM Granite-powered debugging hints, concept breakdowns, and output comparisons.
7. **Submission**: Pre-submission checklist with academic integrity declaration.
8. **Feedback & Viva Voce**: Faculty marks breakdown, comments, and interactive Viva Voce questionnaire.

### Module 3: Advanced Online Compiler
- **8 Supported Languages**: Python 3.12, C (GCC), C++ (G++), Java 17, SQL (SQLite/PostgreSQL), JavaScript (Node.js), and HTML/CSS.
- **Judge0 Cloud Execution**: Seamless integration when API keys are configured.
- **Isolated Local Sandboxing**: Subprocess boundaries with 5.0s timeouts, memory limits, and sanitized environments. Untrusted student code is never executed directly on the main application server process.
- **Execution Tracking**: Full execution history recorded with execution duration, memory consumption, exit codes, and output logs.

### Module 4: IBM Granite + RAG Architecture
- **Mandatory AI Model**: Powered by **IBM Granite 3-8B Instruct** (`ibm/granite-3-8b-instruct`) via `ibm-watsonx-ai`.
- **Syllabus RAG**: Uploaded course syllabus PDFs are ingested, tokenized, and embedded into **ChromaDB**. AI-generated experiment manuals cite exact syllabus units and textbooks.
- **Transparent Fallback**: When API credentials are not set, LabGenie AI operates in an explicit **Demo Simulation Mode** with realistic Granite-styled algorithmic responses.

### Module 5: AI Lab Copilot
- Context-aware student assistant grounded in the active experiment.
- Diagnostic modes: Error explanation, debugging hints, conceptual explanations, output pattern comparison, and custom prompt queries.

### Module 6: Advanced Virtual Labs Suite
1. **Digital Electronics Lab**:
   - Gates: AND, OR, NOT, NAND, NOR, XOR, XNOR.
   - Interactive binary toggle switches (0 and 1) and glowing LED indicators.
   - Dynamic truth table generator computing all $2^n$ logic states.
   - Circuit verification (e.g., Half Adder: $\text{Sum} = A \oplus B$, $\text{Carry} = A \cdot B$).
2. **Computer Networks Lab**:
   - IPv4 Subnet Calculator: Network ID, Broadcast ID, total hosts, usable range, and 32-bit binary mask.
   - Multi-hop Packet Router & ICMP Ping Simulator: Hop-by-hop latency simulation across Routed WAN, Gigabit LAN, and Hub-and-Spoke Star topologies.
3. **DBMS SQL Lab**:
   - Preloaded university database schema viewer (`departments`, `students`, `courses`, `enrollments`).
   - Interactive SQL query editor with tabular query result set rendering.

### Module 7: Faculty Dashboard
- Laboratory course management and syllabus PDF upload.
- Batch scheduling with assigned laboratory rooms, dates, time windows, and submission deadlines.
- Rubric configuration with criteria weights and point allocation.

### Module 8: Real-Time Laboratory Telemetry Monitoring
- Faculty telemetry dashboard auto-refreshing every 5 seconds.
- Displays active students in current lab sessions, their active workspace tab, compilation attempt counts, success/failure ratios, and last heartbeat timestamps.
- One-click **Needs Assistance** flag resolution for students asking for instructor help.

### Module 9: HOD Executive Analytics & Accreditation Audit
- Department-wide KPI metrics: Total students, faculty, enrolled courses, completion rate, average marks, and hardware utilization.
- Multi-level filtering: Academic Year, Semester, and Laboratory Course.
- Export formats: **CSV Raw Audit Dataset** and **Official Academic Audit Report PDF**.

### Module 10: AI Preliminary Evaluation & Marks Assistance
- IBM Granite evaluates submitted code, syntax quality, and execution output before faculty verification.
- Provides preliminary marks (out of 25), confidence scores, positive highlights, and suggested comments with a 1-click **Apply AI Suggestions** button.

### Module 11: Practical Skill Verification (Viva Voce)
- Automated Viva Voce test containing technical conceptual questions.
- Students type written answers directly in the workspace.
- IBM Granite evaluates student comprehension, assigns point scores, generates constructive feedback, and classifies understanding into *Excellent*, *Good*, or *Needs Improvement*.

### Module 12: Automatic Lab Record Generator (PDF)
- **Individual Experiment Lab Record PDF**: Includes title, aim, theory, procedure, source code, output log, observations, and faculty signature block.
- **Complete Course Lab Record Book PDF**: Comprehensive publication-ready record book with an official College Cover Page, Bonafide Certificate, Index Sheet with awarded marks, and all experiment chapters.

### Modules 13-17: Production Readiness, Security, Testing & Docker
- Strict JWT authentication with PBKDF2/Bcrypt password hashing and role-based permissions.
- Responsive dark navy SaaS design system with blue/violet accents.
- Automated pytest test suite covering all services and endpoints.
- Multi-stage Dockerization (`Dockerfile`, `docker-compose.yml`) for PostgreSQL, FastAPI, and Vite/Nginx.

---

## 🚀 Getting Started

### Prerequisites
- **Python**: 3.10+ (tested on Python 3.12)
- **Node.js**: v18+ (tested on Node v20/v22)
- **npm**: v9+
- **Docker & Docker Compose** (optional for containerized setup)

---

### Method A: Local Development Setup

#### 1. Backend Setup
```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server (SQLite database is seeded automatically)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation is available at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

#### 2. Frontend Setup
```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite dev server
npm run dev
```
Open your browser at **[http://localhost:5173](http://localhost:5173)**.

---

### Method B: Production Docker Compose Setup

Run the entire full-stack application (PostgreSQL + FastAPI backend + Nginx React frontend) with a single command:

```bash
docker-compose up --build -d
```
- Frontend: [http://localhost](http://localhost) (or [http://localhost:5173](http://localhost:5173))
- Backend API: [http://localhost:8000](http://localhost:8000)
- PostgreSQL Database: Port `5432`

---

## 👥 Seeded Demo Accounts

You can test all user roles using the 1-click switcher in the top navigation bar or log in with the following credentials:

| Role | Email | Password | Name | Department / Roll |
| :--- | :--- | :--- | :--- | :--- |
| **Student** | `student@labgenie.edu` | `password123` | Aarav Sharma | CSE • Roll: 21CS042 |
| **Student 2** | `priya@labgenie.edu` | `password123` | Priya Patel | CSE • Roll: 21CS089 |
| **Faculty** | `faculty@labgenie.edu` | `password123` | Dr. Rajesh Sharma | CSE • Emp: FAC-CSE-104 |
| **HOD** | `hod@labgenie.edu` | `password123` | Dr. Sunita Deshmukh | CSE • Emp: HOD-CSE-01 |

---

## 🧪 Automated Testing

### 1. Backend Automated Tests (Pytest)
Run the full backend test suite covering Authentication, Courses, AI Manuals, Compilers, Virtual Labs, Telemetry, and PDF Generation:

```bash
cd backend
python -m pytest -v
```
*Current test suite: **18 passing tests**.*

### 2. Frontend Production Build Verification
Verify TypeScript type-checking and bundling:

```bash
cd frontend
npm run build
```
*Produces optimized bundle in `frontend/dist` with 0 build errors.*

---

## ⚙️ Environment Variables Reference

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./labgenie.db` (or `postgresql://user:pass@host:5432/db`) |
| `SECRET_KEY` | JWT signing secret key | `labgenie_super_secret_jwt_key_2026` |
| `WATSONX_APIKEY` | IBM Cloud API key for watsonx.ai | `""` *(Enables explicit demo mode if empty)* |
| `WATSONX_PROJECT_ID` | IBM watsonx.ai Project ID | `""` |
| `WATSONX_URL` | IBM watsonx.ai endpoint | `https://us-south.ml.cloud.ibm.com` |
| `WATSONX_MODEL_ID` | Mandatory IBM Granite model | `ibm/granite-3-8b-instruct` |
| `JUDGE0_API_URL` | Judge0 Execution API endpoint | `https://judge0-ce.p.rapidapi.com` |
| `JUDGE0_API_KEY` | RapidAPI / Judge0 Key | `""` *(Uses secure sandboxing if empty)* |
| `VITE_API_URL` | Frontend API Base URL | `http://localhost:8000/api` |

---

## 📜 License
Developed for engineering institutions, autonomous technical universities, and academic computer laboratories.
All rights reserved © 2026 LabGenie AI.
