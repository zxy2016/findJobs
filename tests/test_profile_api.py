import io
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
import pytest
from sqlalchemy.orm import Session

from app.main import app
from app.services.llm_client import LLMClient, get_llm_client
from app.db.session import get_db

# A minimal valid PDF file content (version 1.4)
MINIMAL_PDF = b'''
%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 55 >>
stream
BT
/F1 12 Tf
100 100 Td
(This is a test resume.) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000063 00000 n 
0000000117 00000 n 
0000000204 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
300
%%EOF
'''

# A minimal valid DOCX file is complex, so we'll just mock the parsing logic for it.
# For a real test, we would use a tiny pre-generated docx file.

@pytest.fixture
def mock_llm_client():
    mock_client = AsyncMock(spec=LLMClient)
    mock_client.analyze.return_value = {"name": "test user", "skills": ["python"]}
    return mock_client

@pytest.fixture
def override_get_db(mocker):
    # This is a simplified in-memory SQLite setup for testing
    from sqlalchemy import create_engine
    from app.db.base_class import Base

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = Session(autocommit=False, autoflush=False, bind=engine)

    def _override():
        try:
            db = TestingSessionLocal
            yield db
        finally:
            db.close()
    
    return _override


def test_upload_pdf_resume_success(
    mocker,
    mock_llm_client,
    override_get_db
):
    app.dependency_overrides[get_llm_client] = lambda: mock_llm_client
    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    file_content = MINIMAL_PDF
    file = ("test_resume.pdf", io.BytesIO(file_content), "application/pdf")

    response = client.post("/api/v1/profile/upload", files={"file": file})

    assert response.status_code == 200
    data = response.json()
    assert "This is a test resume." in data["raw_content"]
    assert data["structured_profile"] == {"name": "test user", "skills": ["python"]}
    
    # Verify LLM client was called
    mock_llm_client.analyze.assert_called_once()

    # Cleanup overrides
    app.dependency_overrides = {}

def test_upload_unsupported_file_type(
    mocker,
    mock_llm_client,
    override_get_db
):
    app.dependency_overrides[get_llm_client] = lambda: mock_llm_client
    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)
    file = ("test.txt", io.BytesIO(b"some text"), "text/plain")

    response = client.post("/api/v1/profile/upload", files={"file": file})

    assert response.status_code == 400
    assert "不支持的文件类型" in response.json()["detail"]

    # Cleanup overrides
    app.dependency_overrides = {}
