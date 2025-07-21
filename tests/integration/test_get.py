import sys
import pytest
# sys hacks to get imports to work
sys.path.append("./")
from main import app
from httpx import ASGITransport, AsyncClient
from schemas.study_config_response_schema import StudyConfigResponse


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