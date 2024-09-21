import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, SessionLocal
from app.models import Base, User
from app.utility.utils import hash_password


@pytest.fixture(scope="module")
def test_app():
    Base.metadata.create_all(bind=SessionLocal().bind)
    yield TestClient(app)  
    Base.metadata.drop_all(bind=SessionLocal().bind)

@pytest.fixture
def create_test_user():
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "password": "testpassword",
        "limit": 5,
        "window_seconds": 60,
    }
    db = next(get_db())
    user = User(
        email=user_data["email"],
        name=user_data["name"],
        password=hash_password(user_data["password"]),
        limit=user_data["limit"],
        window_seconds=user_data["window_seconds"],
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    yield user  

    db.delete(user)
    db.commit()

def test_register(test_app):
    response = test_app.post("/register/", json={
        "email": "newuser@example.com",
        "name": "New User",
        "password": "newpassword",
        "limit": 10,
        "window_seconds": 60,
    })
    assert response.status_code == 200
    assert response.json()["data"]["email"] == "newuser@example.com"

def test_login(test_app, create_test_user):
    response = test_app.post("/login/", json={
        "email": create_test_user.email,
        "password": "testpassword",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_get_user(test_app, create_test_user):
    response = test_app.get(f"/user/{create_test_user.id}")
    assert response.status_code == 200
    assert response.json()["data"]["email"] == create_test_user.email

def test_get_all_users(test_app):
    response = test_app.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)

def test_invalid_user_id(test_app):
    response = test_app.get("/user/99999")  
    assert response.status_code == 404
    #assert response.json()["message"] == "invalid user_id"


