from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Department, StudentBatch, Course
from app.schemas import UserCreate, UserLogin, UserOut, Token
from app.auth import verify_password, get_password_hash, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserOut)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    final_name = user_data.get_name()
    if not final_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Name is required."
        )

    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    # Resolve Department if found
    dept_name = user_data.department or "Computer Science & Engineering"
    dept_obj = db.query(Department).filter(
        (Department.name.ilike(f"%{dept_name}%")) | 
        (Department.code.ilike(f"%{dept_name}%"))
    ).first()
    dept_id = dept_obj.id if dept_obj else None

    # Resolve StudentBatch if student
    batch_id = user_data.batch_id
    if not batch_id and (user_data.role or "student") == "student":
        batch_obj = db.query(StudentBatch).first()
        batch_id = batch_obj.id if batch_obj else None

    new_user = User(
        name=final_name,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role or "student",
        department=dept_name,
        department_id=dept_id,
        batch_id=batch_id,
        roll_or_emp_id=user_data.get_roll_or_emp_id()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Auto-enroll student into available courses so workspace is populated
    if new_user.role == "student":
        courses = db.query(Course).all()
        for course in courses:
            if new_user not in course.students:
                course.students.append(new_user)
        db.commit()

    return new_user

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/demo-users")
def get_demo_users(db: Session = Depends(get_db)):
    """Provides instant role switching for demonstration"""
    roles = ["student", "faculty", "hod"]
    users = []
    for r in roles:
        u = db.query(User).filter(User.role == r).first()
        if u:
            users.append({
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "role": u.role,
                "roll_or_emp_id": u.roll_or_emp_id,
                "department": u.department
            })
    return users

