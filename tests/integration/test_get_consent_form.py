import sys

import pytest
# sys hacks to get imports to work
sys.path.append("./")
from main import app
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_get_consent_form():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        study_response = await client.get("/config/study_list")
        assert study_response.status_code == 200
        study_id = study_response.json()

        response = await client.get(f"/config/get_consent_form/{study_id[0]}")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.headers["content-disposition"].startswith("inline")

        assert response.content[:4] == b"%PDF"  # PDF magic number