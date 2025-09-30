import sys
import uuid
import pytest
import json

import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from db.client import get_db_session
from models.study_config_model import StudyConfiguration
from models.study_model import Study
from models.study_result_model import StudyResults

# sys hacks to get imports to work
sys.path.append("./")
from main import app as fastapi_app
from httpx import ASGITransport, AsyncClient
from schemas.study_config_response_schema import StudyConfigResponse
from services.study_retrieval_service import get_study_id_list, get_survey_id

@pytest.fixture
def app():
    return fastapi_app

@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client 

@pytest_asyncio.fixture
async def session():
    client = get_db_session()
    return await anext(client)

@pytest_asyncio.fixture
async def study_config(client):
    study_response = await client.get("/study/study_ids")
    study_id = study_response.json()

    return await client.get(f"/study/experiment_phase/{study_id[0]}")

@pytest.mark.asyncio
async def test_get_study_config(client):
    study_response = await client.get("/study/study_ids")
    assert study_response.status_code == 200
    study_id = study_response.json()

    response = await client.get(f"/study/export/{study_id[0]}")
    assert response.status_code == 200
    json_data = response.json()
    parsed = StudyConfigResponse(**json_data)
    assert parsed

@pytest.mark.asyncio
async def test_get_survey_id(session) -> uuid.UUID:
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

# @pytest.mark.asyncio
# async def test_get_survey_questions(client):
#     study_response = await client.get("/study/study_ids")
#     assert study_response.status_code == 200
#     study_id = study_response.json()
    
#     response = await client.get(f"/study/survey/{study_id[0]}")
#     assert response.status_code == 200
#     json_data = response.json()
#     parsed = SurveyQuestions(**json_data)
#     assert parsed    
        
@pytest.mark.asyncio
async def test_get_learning_phase(study_config):
    assert study_config.status_code == 200
    json_data = study_config.json()
    assert "display_duration" in json_data
    assert "pause_duration" in json_data
    assert "display_method" in json_data
    assert "images" in json_data
    assert "image_ids" in json_data

@pytest.mark.asyncio
async def test_get_waiting_phase(study_config):
    assert study_config.status_code == 200
    json_data = study_config.json()
    assert "display_duration" in json_data

@pytest.mark.asyncio
async def test_get_experiment_phase(study_config):
    assert study_config.status_code == 200
    json_data = study_config.json()
    assert "display_duration" in json_data
    assert "pause_duration" in json_data
    assert "display_method" in json_data
    assert "response_method" in json_data
    assert "images" in json_data
    assert "image_ids" in json_data

@pytest.mark.asyncio
async def test_get_consent_form(client):
    study_response = await client.get("/study/study_ids")
    assert study_response.status_code == 200
    study_id = study_response.json()

    response = await client.get(f"/study/consent_form/{study_id[0]}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"].startswith("inline")

    assert response.content[:4] == b"%PDF"  # PDF magic number

@pytest.mark.asyncio
async def test_get_study_id_from_config_service(session):
 try:
    config_id="acf1c8cc-5040-4266-bba4-226589f156f4"
    stmt=select(StudyConfiguration.study_id).where(StudyConfiguration.id==config_id)
    results = await session.execute(stmt)
    study_id = results.scalars().one_or_none()
    assert str(study_id) == "423aecc2-70ba-4c02-b99a-79f49f94567a"
 except Exception as e:
    raise e
 
@pytest.mark.asyncio
async def test_get_study_id_from_config_endpoint(client):
 try:
    config_id="acf1c8cc-5040-4266-bba4-226589f156f4"
    response = await client.get(f'/study/study_id_from_config/{config_id}')
    assert response.status_code == 200
    assert response.json() == "423aecc2-70ba-4c02-b99a-79f49f94567a"
 except Exception as e:
    raise e