import sqlite3
import time
from typing import Dict, Any, List, Optional

class DBMSService:
    """
    Virtual Laboratory Service for Database Management Systems (Module 6).
    Provides isolated SQL workspace preloaded with university schema, table explorer, and query execution.
    """

    def _get_seeded_connection(self) -> sqlite3.Connection:
        """Creates an in-memory SQLite database preloaded with realistic university tables"""
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()

        # Seed university tables
        cursor.executescript("""
        CREATE TABLE departments (
            dept_id INTEGER PRIMARY KEY,
            dept_name TEXT NOT NULL,
            dept_code TEXT UNIQUE NOT NULL
        );

        INSERT INTO departments VALUES (1, 'Computer Science & Engineering', 'CSE');
        INSERT INTO departments VALUES (2, 'Electronics & Communication', 'ECE');
        INSERT INTO departments VALUES (3, 'Artificial Intelligence & ML', 'AI&ML');

        CREATE TABLE students (
            student_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            dept_id INTEGER,
            gpa REAL,
            semester INTEGER,
            FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
        );

        INSERT INTO students VALUES (101, 'Aarav Sharma', 1, 9.15, 5);
        INSERT INTO students VALUES (102, 'Priya Patel', 1, 8.85, 5);
        INSERT INTO students VALUES (103, 'Rohan Verma', 2, 7.90, 3);
        INSERT INTO students VALUES (104, 'Ananya Roy', 3, 9.42, 5);
        INSERT INTO students VALUES (105, 'Kavya Nair', 1, 8.60, 5);

        CREATE TABLE courses (
            course_id INTEGER PRIMARY KEY,
            course_code TEXT UNIQUE NOT NULL,
            course_title TEXT NOT NULL,
            credits INTEGER
        );

        INSERT INTO courses VALUES (1, 'CS301', 'Data Structures & Algorithms', 4);
        INSERT INTO courses VALUES (2, 'EC204', 'Digital Electronics', 3);
        INSERT INTO courses VALUES (3, 'CS402', 'Database Management Systems', 4);

        CREATE TABLE enrollments (
            enrollment_id INTEGER PRIMARY KEY,
            student_id INTEGER,
            course_id INTEGER,
            grade TEXT,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (course_id) REFERENCES courses(course_id)
        );

        INSERT INTO enrollments VALUES (1, 101, 1, 'A+');
        INSERT INTO enrollments VALUES (2, 101, 3, 'A');
        INSERT INTO enrollments VALUES (3, 102, 1, 'A');
        INSERT INTO enrollments VALUES (4, 103, 2, 'B+');
        INSERT INTO enrollments VALUES (5, 104, 3, 'A+');
        """)
        conn.commit()
        return conn

    def get_schema_summary(self) -> Dict[str, List[str]]:
        """Returns map of table names to column lists"""
        conn = self._get_seeded_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [r[0] for r in cursor.fetchall()]

        schema_map = {}
        for tbl in tables:
            cursor.execute(f"PRAGMA table_info({tbl});")
            cols = [f"{r[1]} ({r[2]})" for r in cursor.fetchall()]
            schema_map[tbl] = cols

        conn.close()
        return schema_map

    def execute_sql_query(self, sql: str) -> Dict[str, Any]:
        """Executes student SQL query in the isolated university database"""
        start_time = time.time()
        conn = self._get_seeded_connection()
        cursor = conn.cursor()

        try:
            statements = [s.strip() for s in sql.split(";") if s.strip()]
            if not statements:
                return {
                    "columns": [],
                    "rows": [],
                    "row_count": 0,
                    "execution_time": 0.0,
                    "status": "empty",
                    "message": "No SQL statement provided."
                }

            last_cursor = None
            for stmt in statements:
                last_cursor = cursor.execute(stmt)

            duration = round(time.time() - start_time, 4)

            # Check if last statement produced a result set (SELECT / PRAGMA)
            if last_cursor.description:
                columns = [col[0] for col in last_cursor.description]
                rows = last_cursor.fetchall()
                schema_tables = self.get_schema_summary()
                return {
                    "columns": columns,
                    "rows": rows,
                    "row_count": len(rows),
                    "execution_time": duration,
                    "status": "success",
                    "message": f"{len(rows)} row(s) returned successfully.",
                    "schema_tables": schema_tables
                }
            else:
                conn.commit()
                rowcount = last_cursor.rowcount if last_cursor.rowcount != -1 else 0
                schema_tables = self.get_schema_summary()
                return {
                    "columns": ["Result"],
                    "rows": [[f"Statement executed successfully. {rowcount} row(s) affected."]],
                    "row_count": rowcount,
                    "execution_time": duration,
                    "status": "success",
                    "message": f"Query OK, {rowcount} rows affected.",
                    "schema_tables": schema_tables
                }
        except Exception as e:
            duration = round(time.time() - start_time, 4)
            return {
                "columns": ["Error"],
                "rows": [[str(e)]],
                "row_count": 0,
                "execution_time": duration,
                "status": "error",
                "message": f"SQL Execution Error: {str(e)}",
                "schema_tables": self.get_schema_summary()
            }
        finally:
            conn.close()

dbms_service = DBMSService()

