import uuid
from httpx import ASGITransport, AsyncClient
import pytest
from main import app


@pytest.mark.asyncio
async def test_add_study_results():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        study_id = "4ff98d1b-3fdb-43d9-8098-2d89a191e959"
        subject_id = str(uuid.uuid4())
        response = await client.post(f"/results/responses/{study_id}?subject_id={subject_id}",
            json=[{
                    "image_id":"CFD-WM-032-001-N.jpg",
                    "answer":0,
                    "response_time":0.01
            },{
                    "image_id":"CFD-WM-033-025-N.jpg",
                    "answer":2,
                    "response_time":0.1
            },
            ]
        )
        assert response.status_code == 200
        assert response.json()["message"] == "ok"