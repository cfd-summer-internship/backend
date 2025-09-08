from uuid import UUID
from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io
import csv

from db.client import get_db_session
from models.user_model import User
from models.enums import UserRole
from auth.user_manager import require_role
from services.researcher_dashboard_service import (
    delete_study_config,
    get_all_study_responses,
    get_config_id,
    get_study_response_by_id,
    get_study_codes,
    get_study_results_subject_id,
    get_study_results_study_id,
    get_all_study_results,
)
from schemas.researcher_dashboard_schema import (
    ConfigDeleteRequest,
    ResultsExportSchema,
    StudyResultsSchema,
)

router = APIRouter(prefix="/researcher", tags=["Researcher"])


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

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_config(
    payload: ConfigDeleteRequest,
    user: User = Depends(require_role(UserRole.RESEARCHER)),
    conn: AsyncSession = Depends(get_db_session)
):
    config_id = await get_config_id(user.id, payload.study_code, conn)
    return await delete_study_config(config_id, user.id, conn)

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
            "Age",
            "Sex",
            "Race",
        ]
    )
    for response in export_data.responses:
        row_data = [
            export_data.results.study_id,
            export_data.results.subject_id,
            export_data.results.submitted,
            response.image_id,
            response.answer,
            response.response_time,
        ]
        if export_data.demographics:
            row_data.extend(
                [
                    export_data.demographics.age,
                    export_data.demographics.sex,
                    export_data.demographics.race,
                ]
            )
        doc.writerow(row_data)
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
            "Age",
            "Sex",
            "Race",
        ]
    )
    for data in export_data:
        for response in data.responses:
            row_data = [
                data.results.study_id,
                data.results.subject_id,
                data.results.submitted,
                response.image_id,
                response.answer,
                response.response_time,
            ]
            if data.demographics:
                row_data.extend(
                    [
                        data.demographics.age,
                        data.demographics.sex,
                        data.demographics.race,
                    ]
                )
            doc.writerow(row_data)
    buffer.seek(0)
    headers = {
        "Content-Disposition": f"attachment; filename={str(user.id)}-results.csv; filename*=UTF-8''{str(user.id)}-results.csv"
    }
    return StreamingResponse(
        iter([buffer.getvalue()]), media_type="text/csv", headers=headers
    )
