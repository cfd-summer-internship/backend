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
        study_response = await client.get("/config/study_list")
        assert study_response.status_code == 200
        study_id = study_response.json()

        response = await client.get(f"/config/retrieve/{study_id[0]}")
        assert response.status_code == 200
        json_data = response.json()
        parsed = StudyConfigResponse(**json_data)
        assert parsed