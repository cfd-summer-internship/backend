from uuid import UUID
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io, csv

from db.client import get_db_session
from models.user_model import User
from models.enums import UserRole
from auth.user_manager import require_role
from services.researcher_dashboard_service import (
    list_studies_for_researcher,
    summarize_study,
    paged_results,
    _ensure_ownership,
)
from schemas.researcher_dashboard_schema import (
    StudyListResponse, StudyListItem, StudySummary, PagedResults
)

router = APIRouter(prefix="/researcher", tags=["Researcher"])

@router.get("/me")
async def me(user: User = Depends(require_role(UserRole.RESEARCHER))):
    # minimal payload for header display
    return {"id": user.id, "email": user.email, "roles": user.role}

@router.get("/studies", response_model=StudyListResponse)
async def get_my_studies(
    user: User = Depends(require_role(UserRole.RESEARCHER)),
    conn: AsyncSession = Depends(get_db_session),
):
    items = await list_studies_for_researcher(conn, user.id)
    return {"items": [StudyListItem(**it) for it in items]}

@router.get("/studies/{study_id}/summary", response_model=StudySummary)
async def get_study_summary(
    study_id: UUID,
    user: User = Depends(require_role(UserRole.RESEARCHER)),
    conn: AsyncSession = Depends(get_db_session),
):
    await _ensure_ownership(conn, study_id, user.id)
    return await summarize_study(conn, study_id)

@router.get("/studies/{study_id}/results", response_model=PagedResults)
async def get_study_results(
    study_id: UUID,
    page: int = 1,
    page_size: int = 10,
    user: User = Depends(require_role(UserRole.RESEARCHER)),
    conn: AsyncSession = Depends(get_db_session),
):
    await _ensure_ownership(conn, study_id, user.id)
    return await paged_results(conn, study_id, page, page_size)

@router.get("/studies/{study_id}/export.csv")
async def export_results_csv(
    study_id: UUID,
    user: User = Depends(require_role(UserRole.RESEARCHER)),
    conn: AsyncSession = Depends(get_db_session),
):
    await _ensure_ownership(conn, study_id, user.id)

    # dump flat rows for Excel/Sheets
    rows = await paged_results(conn, study_id, page=1, page_size=10_000_000)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["study_results_id", "subject_id", "submitted", "image_id", "answer", "response_time"])
    for r in rows["items"]:
        for resp in r["responses"]:
            w.writerow([
                r["study_results_id"], r["subject_id"], r["submitted"],
                resp["image_id"], resp["answer"], resp["response_time"]
            ])
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv")
