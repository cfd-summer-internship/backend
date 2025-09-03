from uuid import UUID
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io
import csv

from db.client import get_db_session
from models.user_model import User
from models.enums import UserRole
from auth.user_manager import require_role
from services.researcher_dashboard_service import (
    get_all_study_responses,
    get_study_response_by_id,
    list_studies_for_researcher,
    summarize_study,
    paged_results,
    _ensure_ownership,
    get_study_codes,
    get_study_results_subject_id,
    get_study_results_study_id,
    get_all_study_results,
)
from schemas.researcher_dashboard_schema import (
    ResultsExportSchema,
    StudyListResponse,
    StudyListItem,
    StudyResultsSchema,
    StudySummary,
    PagedResults,
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
    w.writerow(
        [
            "study_results_id",
            "subject_id",
            "submitted",
            "image_id",
            "answer",
            "response_time",
        ]
    )
    for r in rows["items"]:
        for resp in r["responses"]:
            w.writerow(
                [
                    r["study_results_id"],
                    r["subject_id"],
                    r["submitted"],
                    resp["image_id"],
                    resp["answer"],
                    resp["response_time"],
                ]
            )
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv")


@router.get("/configurations")
async def get_config_list(
    user: User = Depends(require_role(UserRole.RESEARCHER)),
    conn: AsyncSession = Depends(get_db_session),
):
    study_codes = await get_study_codes(conn, user.id)
    return {"study_codes": study_codes}


@router.get("/results/{study_id}", response_model=list[StudyResultsSchema])
async def get_study_results_by_id(
    study_id: UUID,
    user: User = Depends(require_role(UserRole.RESEARCHER)),
    conn: AsyncSession = Depends(get_db_session),
) -> list[StudyResultsSchema]:
    return await get_study_results_study_id(study_id, user.id, conn)


@router.get("/result/{subject_id}", response_model=StudyResultsSchema)
async def get_study_results_by_subject(
    subject_id: UUID,
    user: User = Depends(require_role(UserRole.RESEARCHER)),
    conn: AsyncSession = Depends(get_db_session),
) -> StudyResultsSchema:
    return await get_study_results_subject_id(subject_id, user.id, conn)


@router.get("/results", response_model=list[StudyResultsSchema])
async def get_all(
    user: User = Depends(require_role(UserRole.RESEARCHER)),
    conn: AsyncSession = Depends(get_db_session),
) -> list[StudyResultsSchema]:
    return await get_all_study_results(user.id, conn)


@router.get("/export/{study_results_id}", response_model=ResultsExportSchema)
async def export_study_results_by_id(
    study_results_id: UUID,
    user: User = Depends(require_role(UserRole.RESEARCHER)),
    conn: AsyncSession = Depends(get_db_session),
):
    export_data = await get_study_response_by_id(study_results_id, user.id, conn)
    buffer = io.StringIO()
    doc = csv.writer(buffer)
    doc.writerow(
        [
            "Study ID",
            "Subject ID",
            "Submission",
            "CFD Image ID",
            "Answer",
            "Response time (ms)",
        ]
    )
    for response in export_data.responses:
        doc.writerow(
            [
                export_data.results.study_id,
                export_data.results.subject_id,
                export_data.results.submitted,
                response.image_id,
                response.answer,
                response.response_time,
            ]
        )
    buffer.seek(0)
    headers = {
        "Content-Disposition": f"attachment; filename={str(export_data.results.study_id)[-6:]}-results.csv; filename*=UTF-8''{str(export_data.results.study_id)[-6:]}-results.csv"
    }
    return StreamingResponse(
        iter([buffer.getvalue()]), media_type="text/csv", headers=headers
    )


@router.get("/export_all", response_model=list[ResultsExportSchema])
async def export_all(
    user: User = Depends(require_role(UserRole.RESEARCHER)),
    conn: AsyncSession = Depends(get_db_session),
) -> list[ResultsExportSchema]:
    export_data = await get_all_study_responses(user.id, conn)
    buffer = io.StringIO()
    doc = csv.writer(buffer)
    doc.writerow(
        [
            "Study ID",
            "Subject ID",
            "Submission",
            "CFD Image ID",
            "Answer",
            "Response time (ms)",
        ]
    )
    for data in export_data:
        for response in data.responses:
            doc.writerow(
                [
                    data.results.study_id,
                    data.results.subject_id,
                    data.results.submitted,
                    response.image_id,
                    response.answer,
                    response.response_time,
                ]
            )
    buffer.seek(0)
    headers = {
        "Content-Disposition": f"attachment; filename={str(user.id)}-results.csv; filename*=UTF-8''{str(user.id)}-results.csv"
    }
    return StreamingResponse(
        iter([buffer.getvalue()]), media_type="text/csv", headers=headers
    )
