import sys

from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from sqlalchemy import select

from db.client import get_db_session
from models.conclusion_config_model import ConclusionConfiguration
from models.study_config_model import StudyConfiguration
from models.study_model import Study
from models.study_result_model import StudyResults
from settings import get_settings
# sys hacks to get imports to work
sys.path.append("./")
from fastapi.testclient import TestClient
from main import app as fastapi_app
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def settings():
    return get_settings()

@pytest.fixture
def app():
    return fastapi_app

@pytest_asyncio.fixture
async def session():
    settings = get_settings()
    engine=create_async_engine(settings.connection_string,echo=True)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client    

@pytest_asyncio.fixture
async def auth_token(client, settings):
    login_info = {"username":settings.dev_email,"password":settings.dev_password}
    response = await client.post("/auth/jwt/login", data=login_info)
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_get_study_list(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = await client.get(
        "/researcher/configurations",
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["study_codes"]

@pytest.mark.asyncio
async def test_get_study_result_by_id(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    study_id = "423aecc2-70ba-4c02-b99a-79f49f94567a"
    response = await client.get(
        f'/researcher/results/{study_id}',
        headers=headers
    )
    assert response.status_code == 200
    for study_result in response.json():
        assert "id" in study_result
        assert "study_id" in study_result
        assert "config_id" in study_result
        assert "subject_id" in study_result
        assert "submitted" in study_result

@pytest.mark.asyncio
async def test_get_study_result_subject(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    subject_id = "a2754263-dd60-40a2-a3d2-567f10c369e3"
    response = await client.get(
        f'/researcher/result/{subject_id}',
        headers=headers
    )
    assert response.status_code == 200
    study_result =  response.json()
    assert "id" in study_result
    assert "study_id" in study_result
    assert "config_id" in study_result
    assert "subject_id" in study_result
    assert "submitted" in study_result

@pytest.mark.asyncio
async def test_get_all_results(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = await client.get(
        f'/researcher/results',
        headers=headers
    )
    assert response.status_code == 200
    for study_result in response.json():
        assert "id" in study_result
        assert "study_id" in study_result
        assert "config_id" in study_result
        assert "subject_id" in study_result
        assert "submitted" in study_result

@pytest.mark.asyncio
async def test_export_responses(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    study_results_id = "18b5b754-b08c-48c5-a158-b2e93dd68e25"
    response = await client.get(
        f'/researcher/export/{study_results_id}',
        headers=headers
    )
    assert response.status_code == 200
    assert response.headers.get("content-type") == "text/csv; charset=utf-8"
    #export = response.json()
    # assert "id" in export["results"]
    # assert "study_id" in export["results"]
    # assert "subject_id" in export["results"]
    # assert "submitted" in export["results"]
    # for study_response in export["responses"]:
    #     assert "image_id" in study_response
    #     assert "answer" in study_response
    #     assert "response_time" in study_response

@pytest.mark.asyncio
async def test_export_all(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = await client.get(
        f'/researcher/export_all',
        headers=headers
    )
    assert response.status_code == 200
    assert response.headers.get("content-type") == "text/csv; charset=utf-8"
    # export_data = response.json()
    # for export in export_data:
    #     assert "id" in export["results"]
    #     assert "study_id" in export["results"]
    #     assert "subject_id" in export["results"]
    #     assert "submitted" in export["results"]
    #     for study_response in export["responses"]:
    #         assert "image_id" in study_response
    #         assert "answer" in study_response
    #         assert "response_time" in study_response

@pytest.mark.asyncio
async def test_check_survey(session):
    study_results_id = "18b5b754-b08c-48c5-a158-b2e93dd68e25"
    stmt = (
        select(ConclusionConfiguration.has_survey)
        .join(StudyConfiguration)
        .join(Study)
        .join(StudyResults)
        .where(StudyResults.id == study_results_id)
    )
    res = await session.execute(stmt)
    survey = res.scalar_one_or_none()
    assert survey == True

@pytest.mark.asyncio
async def test_include_config_id(session):
    researcher_id = "786ef119-c7d4-474f-a573-e0d8f6a24476"
    stmt = (
        select(StudyResults)
        .join(Study)
        .join(StudyConfiguration)
        .where(
            Study.researcher == researcher_id,
        )
    )
    res = await session.execute(stmt)
    rows = res.scalars()
    for row in rows:
        assert row.config_id
