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
    login_info = {"username":"dev@plixelated.mozmail.com","password":settings.dev_credentials}
    response = await client.post("/auth/jwt/login", data=login_info)
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_save_study_config(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = await client.post(
        "/config/save",
        headers=headers,
        data={
            "learning.displayDuration" : "1",
            "learning.pauseDuration" : "1",
            "learning.displayMethod" : "sequential",
            "waiting.displayDuration" : "1",
            "experiment.displayDuration" : "1",
            "experiment.pauseDuration" : "1",
            "experiment.displayMethod" : "random",
            "experiment.responseMethod" : "binary",
            "conclusion.showResults": "true",
            "conclusion.survey":"true",
            "survey.questions": ["testing", "testing2"],
        },
        files={
            "configFiles.consentForm" : ("Consent Form", open("tests/assets/Test File.pdf", "rb"), "application/pdf"),
            "configFiles.studyInstructions" : ("Study Instructions", open("tests/assets/Test File.pdf", "rb"), "application/pdf"),     
            "configFiles.learningList" : ("Learning List", open("tests/assets/Test List.csv", "rb"), "application/pdf"),  
            "configFiles.experimentList" : ("Experiment List", open("tests/assets/Test List.csv", "rb"), "application/pdf"), 
            "configFiles.studyDebrief" : ("Study Debrief", open("tests/assets/Test File.pdf", "rb"), "application/pdf"),
        }
    )
    assert response.status_code == 200
    json_data = response.json()
    assert "study_code" in json_data