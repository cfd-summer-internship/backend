
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from auth.user_manager import require_role
from db.client import get_db_session
from models.enums import UserRole
from models.user_model import User
from schemas.researcher_dashboard_schema import StudyResultsSchema
from services.researcher_dashboard_service import get_all_study_results, get_researcher_id, get_study_codes


router = APIRouter(prefix="/staff", tags=["Staff"])
# STAFF
@router.get("/search")
async def get_researcher_by_email(
    email: str,
    user: User = Depends(require_role(UserRole.STAFF)),
    conn: AsyncSession = Depends(get_db_session),
):
    return await get_researcher_id(email, conn)


@router.get("/search/configs")
async def get_researcher_configs(
    email: str,
    user: User = Depends(require_role(UserRole.STAFF)),
    conn: AsyncSession = Depends(get_db_session),
):
    researcher_id = await get_researcher_id(email, conn)
    study_codes = await get_study_codes(conn, researcher_id)
    return {"study_codes": study_codes}


@router.get("/search/results")
async def get_researcher_results(
    email: str,
    user: User = Depends(require_role(UserRole.STAFF)),
    conn: AsyncSession = Depends(get_db_session),
) -> list[StudyResultsSchema]:
    researcher_id = await get_researcher_id(email, conn)
    return await get_all_study_results(researcher_id, conn)
