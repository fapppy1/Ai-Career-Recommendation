import pytest
from app import create_app
from database import db

@pytest.fixture
def app():
    app = create_app()
    app.config.update({"TESTING": True, "JWT_SECRET_KEY": "test-secret"})
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    # Register & login test user
    client.post('/auth/register', json={"email": "test@eval.ac.uk", "password": "Test123!", "full_name": "Eval User"})
    login = client.post('/auth/login', json={"email": "test@eval.ac.uk", "password": "Test123!"}).get_json()
    return {"Authorization": f"Bearer {login['access_token']}"}