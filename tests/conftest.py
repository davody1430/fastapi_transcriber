import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base
from app.core.config import settings

@pytest.fixture(scope="session")
def test_db():
    # ایجاد دیتابیس تست در حافظه
    engine = create_engine(settings.TEST_DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # ایجاد جداول
    Base.metadata.create_all(bind=engine)
    
    yield TestingSessionLocal()
    
    # پاکسازی
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def test_client(test_db):
    # کلاینت تست FastAPI
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client