import uuid
import pytest
from fastapi.testclient import TestClient
from db.client import get_db_session
from services.r2_client import get_r2_client
from services.r2_service import generate_url_list, upload_zip_file
from services.study_retrieval_service import get_image_list, get_study_id_list
from settings import get_settings
from models.enums import ImageListColumn
from models import all_models
from main import app

app_client = TestClient(app)

@pytest.mark.asyncio
async def test_get_generated_urls() -> list[str]:
    settings = get_settings()
    client = get_r2_client()
    conn = get_db_session()
    session = await anext(conn)
    generated_urls = []
    try:
        study_ids = await get_study_id_list(session)
        image_list= await get_image_list(study_ids[0],session,ImageListColumn.LEARNING)
        generated_urls = generate_url_list(client, settings.r2_bucket_name,image_list)
    except Exception as e:
        print(str(e))

    finally:
        await session.aclose()
        assert generated_urls

@pytest.mark.asyncio
async def test_upload_zip():
    settings = get_settings()
    client = get_r2_client()
    conn = get_db_session()
    session = await anext(conn)
    try:
        with open("tests/assets/test.zip", "rb") as fp:
            files = {"zip_file":("test.zip",fp,"application/zip")}
            response = app_client.post(
                "/images/upload_zip",
                params={
                    "prefix":"test/"
                },
                files=files
            )
    except Exception as e:
        print(str(e))
    
    assert response.status_code == 200
    assert response.json()["detail"]

@pytest.mark.asyncio
async def test_delete_file():
    try:
        response = app_client.delete(
            "/images/delete_file",
            params={
                "filename":"test/CFD-IF-623-129-N.jpg"
            },
        )
    except Exception as e:
        print(str(e))
    
    assert response.status_code == 200
    assert response.json()["status"]=="success"

@pytest.mark.asyncio
async def test_get_all_files():
    try:
        response = app_client.get(
            "/images/get_all_file_info",
        )
    except Exception as e:
        print(str(e))
    
    assert response.status_code == 200
    assert response.json()["files"]

@pytest.mark.asyncio
async def test_get_file_page():
    try:
        response = app_client.get(
            "/images/get_file_page",
        )
    except Exception as e:
        print(str(e))
    
    assert response.status_code == 200
    assert response.json()["files"]
        