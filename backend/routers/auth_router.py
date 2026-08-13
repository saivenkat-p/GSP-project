from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
import models
import schemas
import auth

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class DemoLoginRequest(BaseModel):
    role: str # "citizen", "partner", "admin"

@router.post("/register", response_model=schemas.TokenResponse)
def register(user_in: schemas.UserRegister, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    hashed_pw = auth.get_password_hash(user_in.password)
    user = models.User(
        name=user_in.name,
        email=user_in.email,
        password_hash=hashed_pw,
        role=user_in.role,
        phone=user_in.phone,
        district=user_in.district or "NTR / Vijayawada",
        state=user_in.state or "Andhra Pradesh"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # If registering as partner, create partner record
    if user.role == "partner":
        partner = models.Partner(
            user_id=user.id,
            business_name=f"{user.name} MeeSeva Center",
            center_type="Authorized Service Facilitator",
            verification_status="verified",
            phone=user.phone or "+91 90000 00000",
            address="Vijayawada Main Road, NTR District",
            district=user.district or "NTR / Vijayawada",
            state=user.state or "Andhra Pradesh",
            supported_service_ids=["ap-income-certificate", "ap-caste-certificate", "ap-encumbrance-certificate"]
        )
        db.add(partner)
        db.commit()

    token = auth.create_access_token({"sub": user.id, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "district": user.district,
            "state": user.state
        }
    }

@router.post("/login", response_model=schemas.TokenResponse)
def login(login_in: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == login_in.email).first()
    if not user or not auth.verify_password(login_in.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = auth.create_access_token({"sub": user.id, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "district": user.district,
            "state": user.state
        }
    }

@router.post("/demo-switch", response_model=schemas.TokenResponse)
def demo_login_switch(req: DemoLoginRequest, db: Session = Depends(get_db)):
    """One-click instant login switcher for testing Citizen, Partner, and Admin roles."""
    user = db.query(models.User).filter(models.User.role == req.role).first()
    if not user:
        # Fallback to creating quick demo user
        if req.role == "partner":
            user = models.User(name="Demo Verified Partner", email="demo_partner@govnav.in", password_hash=auth.get_password_hash("password123"), role="partner")
        elif req.role == "admin":
            user = models.User(name="Demo System Admin", email="demo_admin@govnav.in", password_hash=auth.get_password_hash("password123"), role="admin")
        else:
            user = models.User(name="Demo Citizen", email="demo_citizen@govnav.in", password_hash=auth.get_password_hash("password123"), role="citizen")
        db.add(user)
        db.commit()
        db.refresh(user)

    token = auth.create_access_token({"sub": user.id, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "district": user.district or "NTR / Vijayawada",
            "state": user.state or "Andhra Pradesh"
        }
    }

@router.get("/me")
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "district": current_user.district,
        "state": current_user.state,
        "phone": current_user.phone
    }
