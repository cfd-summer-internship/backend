import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from main import app

@pytest.mark.asyncio
async def test_store_survey_answer():
    survey_config_id = "f0d7d4c6-cf05-4e2d-a1e0-8eafd9ac4ec3"
    survey_question_id = 1

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "survey_config_id": survey_config_id,
            "survey_question_id": survey_question_id,
            "text": "This is my test answer."
        }
        response = await client.post("/survey-answer/", json=payload)
        
        assert response.status_code in [201, 409]
