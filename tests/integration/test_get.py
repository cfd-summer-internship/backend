import sys
import uuid
import pytest
import json
from db.client import get_db_session

# sys hacks to get imports to work
sys.path.append("./")
from main import app
from httpx import ASGITransport, AsyncClient
from schemas.study_config_response_schema import StudyConfigResponse, SurveyQuestions
from services.study_retrieval_service import get_study_id_list, get_survey_id


@pytest.mark.asyncio
async def test_get_study_config():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        study_response = await client.get("/study/study_ids")
        assert study_response.status_code == 200
        study_id = study_response.json()

        response = await client.get(f"/study/export/{study_id[0]}")
        assert response.status_code == 200
        json_data = response.json()
        parsed = StudyConfigResponse(**json_data)
        assert parsed

@pytest.mark.asyncio
async def test_get_survey_id() -> uuid.UUID:
    client = get_db_session()
    session = await anext(client)

    try:
        study_ids = await get_study_id_list(session)
        result = None
        for id in study_ids:
            result = await get_survey_id(id, session)
            if result:
                break

    except Exception as e:
        print(str(e))

    finally:
        await session.aclose()
        assert result 

@pytest.mark.asyncio
async def test_get_survey_questions():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        study_response = await client.get("/study/study_ids")
        assert study_response.status_code == 200
        study_id = study_response.json()
        
        response = await client.get(f"/study/survey/{study_id[1]}")
        assert response.status_code == 200
        json_data = response.json()
        parsed = SurveyQuestions(**json_data)
        assert parsed    
        
@pytest.mark.asyncio
async def test_get_learning_phase():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        study_response = await client.get("/study/study_ids")
        assert study_response.status_code == 200
        study_id = study_response.json()

        response = await client.get(f"/study/learning_phase/{study_id[0]}")
        assert response.status_code == 200
        json_data = response.json()
        assert "display_duration" in json_data
        assert "pause_duration" in json_data
        assert "display_method" in json_data
        assert "image_urls" in json_data

@pytest.mark.asyncio
async def test_get_waiting_phase():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        study_response = await client.get("/study/study_ids")
        assert study_response.status_code == 200
        study_id = study_response.json()

        response = await client.get(f"/study/waiting_phase/{study_id[0]}")
        assert response.status_code == 200
        json_data = response.json()
        assert "display_duration" in json_data

@pytest.mark.asyncio
async def test_get_experiment_phase():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        study_response = await client.get("/study/study_ids")
        assert study_response.status_code == 200
        study_id = study_response.json()

        response = await client.get(f"/study/experiment_phase/{study_id[0]}")
        assert response.status_code == 200
        json_data = response.json()
        assert "display_duration" in json_data
        assert "pause_duration" in json_data
        assert "display_method" in json_data
        assert "response_method" in json_data
        assert "images" in json_data
