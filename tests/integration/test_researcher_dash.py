import sys

from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio

from settings import get_settings
# sys hacks to get imports to work
sys.path.append("./")
from fastapi.testclient import TestClient
from main import app as fastapi_app

@pytest.fixture
def settings():
    return get_settings()

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
        assert "subject_id" in study_result
        assert "submitted" in study_result

@pytest.mark.asyncio
async def test_get_study_result_subject(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    subject_id = "1b907c57-2a92-4948-af52-433410aa0bdb"
    response = await client.get(
        f'/researcher/result/{subject_id}',
        headers=headers
    )
    assert response.status_code == 200
    study_result =  response.json()
    assert "id" in study_result
    assert "study_id" in study_result
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
        assert "subject_id" in study_result
        assert "submitted" in study_result

@pytest.mark.asyncio
async def test_get_study_responses(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    study_results_id = "0ec8dca6-e226-4031-9e07-195ea8aed94c"
    response = await client.get(
        f'/researcher/export/{study_results_id}',
        headers=headers
    )
    assert response.status_code == 200
    export = response.json()
    assert "id" in export["results"]
    assert "study_id" in export["results"]
    assert "subject_id" in export["results"]
    assert "submitted" in export["results"]
    for study_response in export["responses"]:
        assert "image_id" in study_response
        assert "answer" in study_response
        assert "response_time" in study_response
