from io import BytesIO
import uuid
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.study_config_model import StudyConfiguration
from models.uploaded_files_model import UploadedFiles


async def get_study_id_list(conn: AsyncSession):
    try:
        stmt = select(StudyConfiguration).execution_options(populate_existing=True)
        result = await conn.execute(stmt)
        ids: list[uuid.UUUID] = []
        rows = result.scalars().all()
        for study in rows:
            ids.append(study.id)
        return ids
    except Exception:
        raise HTTPException(404)
    

async def get_study_id(study_code:str,conn: AsyncSession):
    try:
        stmt = select(StudyConfiguration).execution_options(populate_existing=True)
        result = await conn.execute(stmt)
        rows = result.scalars().all()
        for study in rows:
            if study.id.hex[-6:] == study_code:
                return study.id
    except Exception:
        raise HTTPException(404)
    
async def get_consent_form(study_id: uuid.UUID, conn: AsyncSession):
    try:
        stmt = (
            select(UploadedFiles.consent_form, UploadedFiles.consent_form_bytes)
            .where(UploadedFiles.study_config_id == study_id)
            .execution_options(populate_existing=True)
        )
        result = await conn.execute(stmt)
        file = result.first()

        if not file:
            raise HTTPException(status_code=404, detail="Consent form not found")

        return StreamingResponse(
            BytesIO(file[1]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="{file[0]}"'
            },
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=e)