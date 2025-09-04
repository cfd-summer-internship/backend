import uuid
from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from main import app as fastapi_app

@pytest.fixture
def app():
    return fastapi_app

@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client    

@pytest.mark.asyncio
async def test_store_survey_answer(client):
        payload={
             "subject_id":"a2754263-dd60-40a2-a3d2-567f10c369e3",
             "age":28,
             "sex":"non-binary",
             "race":"mixed",
        }
        response = await client.post(f"/survey/responses", json=payload)
        assert response.status_code == 201
        assert response.json()["message"] == "Survey answers submitted successfully"
