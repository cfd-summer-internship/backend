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
async def test_add_study_results(client):
        payload={
            "identity":{
                "config_id":"507e3ff7-812c-40c4-8565-6823a4359dc6",
                "subject_id":str(uuid.uuid4()),
            },
            "responses":[
                {"image_id":"CFD-WM-032-001-N.jpg","answer":0,"response_time":0.01},
                {"image_id":"CFD-WM-033-025-N.jpg", "answer":2,"response_time":0.1}
                ],
            }
        
        response = await client.post(f"/results/responses", json=payload)
        assert response.status_code == 201
        assert response.json()["message"] == "Results Submitted Successfully"