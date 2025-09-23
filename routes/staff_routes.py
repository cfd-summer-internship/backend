
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from auth.user_manager import require_role
from db.client import get_db_session
from models.enums import UserRole
from models.user_model import User
from schemas.researcher_dashboard_schema import StudyResultsSchema
from schemas.staff_schemas import SearchRequest
from services.researcher_dashboard_service import get_all_study_results, get_researcher_id, get_study_codes


router = APIRouter(prefix="/staff", tags=["Staff"])
# STAFF
@router.post("/search")
async def get_researcher_by_email(
    payload : SearchRequest,
    user: User = Depends(require_role(UserRole.STAFF)),
    conn: AsyncSession = Depends(get_db_session),
):
    return await get_researcher_id(payload.email, conn)


@router.post("/search/configs")
async def get_researcher_configs(
    payload : SearchRequest,
    user: User = Depends(require_role(UserRole.STAFF)),
    conn: AsyncSession = Depends(get_db_session),
):
    researcher_id = await get_researcher_id(payload.email, conn)
    study_codes = await get_study_codes(conn, researcher_id)
    return {"study_codes": study_codes}


@router.post("/search/results")
async def get_researcher_results(
    payload : SearchRequest,
    user: User = Depends(require_role(UserRole.STAFF)),
    conn: AsyncSession = Depends(get_db_session),
) -> list[StudyResultsSchema]:
    researcher_id = await get_researcher_id(payload.email, conn)
    return await get_all_study_results(researcher_id, conn)
