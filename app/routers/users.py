

from fastapi import APIRouter, Depends, HTTPException, status,Request
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..utility.utils import hash_password, create_access_token, verify_password
from fastapi import FastAPI, Depends, HTTPException, status
from ..utility.auth import get_current_user
from fastapi.responses import JSONResponse
from typing import List
from fastapi.encoders import jsonable_encoder

app = FastAPI()
router = APIRouter()





@router.post("/register/", response_model=schemas.UserResponse,tags=["public"])
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if  db_user :
        return JSONResponse(content=jsonable_encoder(
            {
            "status":False,
            "data" : {},
            "message" : "email already in use"
        }))

    
    hashed_password = hash_password(user.password)

    db_user = models.User(
        email = user.email,
        name = user.name,
        password = hashed_password,
        limit = user.limit,
        window_seconds = user.window_seconds,
        )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login/")
def login(user: schemas.LoginUserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/customer/", response_model=schemas.CustomerResponse, status_code=status.HTTP_201_CREATED)
def customers(skip: int = 0, limit: int = 100,
                  current_user: str = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    customers = db.query(models.Customer).all()
    return JSONResponse(content=jsonable_encoder(
        {
        "status":True,
        "data" : customers,
        "message" : "Customers fetched successfully"
    }))



@router.post("/customer/", 
             response_model=schemas.CustomerResponse, status_code=status.HTTP_201_CREATED)
def customer(customer: schemas.CustomerResponse, db: Session = Depends(get_db),
             current_user: str = Depends(get_current_user),):
    new_customer = models.Customer(
         name=customer.name)
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    customer_response = schemas.CustomerResponse.from_orm(new_customer)
    return JSONResponse(content=jsonable_encoder(
        {
        "status":True,
        "data" : customer_response,
        "message" : "Customer created successfully"
    }))


@router.get("/customer/{customer_id}", response_model=schemas.CustomerResponse)
def customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not db_customer:
        return JSONResponse(content=jsonable_encoder({
                "status":False,
                "data" : {},
                "message" : "invalid customer_id"
            }), status_code=404)
       
    customer_response = schemas.CustomerResponse.from_orm(db_customer)
    return JSONResponse(content=jsonable_encoder(
        {
        "status":True,
        "data" : customer_response,
        "message" : "Customer fetched successfully"
    }))



@router.get("/user/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return JSONResponse(content=jsonable_encoder({
                "status":False,
                "data" : {},
                "message" : "invalid user_id"
            }), status_code=404)
       
    user_response = schemas.UserResponse.from_orm(db_user)
    return JSONResponse(content=jsonable_encoder(
        {
        "status":True,
        "data" : user_response,
        "message" : "User fetched successfully"
    }))




@router.get("/users/", response_model=List[schemas.UserResponse])
def get_all_users(skip: int = 0, limit: int = 100,
                  current_user: str = Depends(get_current_user),
                  db: Session = Depends(get_db)):


    users = db.query(models.User).offset(skip).limit(limit).all()
    return JSONResponse(content=jsonable_encoder(
        {
        "status":True,
        "data" : users,
        "message" : "User fetched successfully"
    }))






@app.on_event("shutdown")
async def shutdown_event():
    await app.state.redis.close()