import uuid
import pytest
from db.client import get_db_session
from services.r2_client import get_r2_client
from services.r2_service import generate_url_list
from services.study_retrieval_service import get_image_list, get_study_id_list
from settings import get_settings
from models.enums import ImageListColumn
from models import all_models

@pytest.mark.asyncio
async def test_get_survey_id() -> uuid.UUID:
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