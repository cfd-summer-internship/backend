from typing import List, Dict
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.study_model import Study
from models.study_result_model import StudyResults
from models.study_response_model import StudyResponse
from models.uploaded_files_model import UploadedFiles
from models.study_config_model import StudyConfiguration
from schemas.researcher_dashboard_schema import (
    ResultsExportSchema,
    StudyResponseSchema,
    StudyResultsSchema,
)


async def _expected_items_for_config(conn: AsyncSession, config_id: UUID) -> int:
    row = await conn.execute(
        select(UploadedFiles.experiment_image_list).where(
            UploadedFiles.study_config_id == config_id
        )
    )
    arr = row.scalar_one_or_none()
    return len(arr or [])


async def list_studies_for_researcher(
    conn: AsyncSession, researcher_id: UUID
) -> List[dict]:
    q = (
        select(
            Study.id,
            func.count(StudyResults.id).label("total"),
            func.max(StudyResults.submitted).label("last_submitted"),
        )
        .join(StudyResults, StudyResults.study_id == Study.id, isouter=True)
        .where(Study.researcher == researcher_id)
        .group_by(Study.id)
    )
    res = await conn.execute(q)
    rows = res.all()

    # fetch expected lengths for each configuration
    cfg_ids = [r.configuration_id for r in rows if r.configuration_id]
    exp_map: Dict[UUID, int] = {}
    if cfg_ids:
        f_q = select(
            UploadedFiles.study_config_id, UploadedFiles.experiment_image_list
        ).where(UploadedFiles.study_config_id.in_(cfg_ids))
        for scid, arr in (await conn.execute(f_q)).all():
            exp_map[scid] = len(arr or [])

    items = []
    for r in rows:
        items.append(
            {
                "id": r.id,
                "configuration_id": r.configuration_id,
                "total_submissions": int(r.total or 0),
                "expected_items": int(exp_map.get(r.configuration_id, 0)),
                "last_submission_at": r.last_submitted,
            }
        )
    return items


async def _ensure_ownership(
    conn: AsyncSession, study_id: UUID, researcher_id: UUID
) -> None:
    ok = await conn.scalar(
        select(Study.id).where(Study.id == study_id, Study.researcher == researcher_id)
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Study not found")


async def summarize_study(conn: AsyncSession, study_id: UUID) -> dict:
    # total submissions + last submitted
    total_q = select(
        func.count(StudyResults.id), func.max(StudyResults.submitted)
    ).where(StudyResults.study_id == study_id)
    total_submissions, _ = (await conn.execute(total_q)).first() or (0, None)
    total_submissions = int(total_submissions or 0)

    # expected items
    cfg_id = await conn.scalar(
        select(Study.configuration_id).where(Study.id == study_id)
    )
    expected_items = await _expected_items_for_config(conn, cfg_id) if cfg_id else 0

    # complete submissions: response count == expected_items
    comp = 0
    if expected_items > 0:
        per_result = (
            select(
                StudyResponse.study_results_id,
                func.count(StudyResponse.id).label("cnt"),
            )
            .join(StudyResults, StudyResults.id == StudyResponse.study_results_id)
            .where(StudyResults.study_id == study_id)
            .group_by(StudyResponse.study_results_id)
        )
        for _, cnt in (await conn.execute(per_result)).all():
            if int(cnt or 0) == expected_items:
                comp += 1

    completion_rate = (comp / total_submissions) * 100.0 if total_submissions else 0.0

    # average response time (ms)
    avg_rt = await conn.scalar(
        select(func.avg(StudyResponse.response_time))
        .join(StudyResults, StudyResults.id == StudyResponse.study_results_id)
        .where(StudyResults.study_id == study_id)
    )
    avg_rt = float(avg_rt) if avg_rt is not None else None

    # answer histogram
    hist_rows = await conn.execute(
        select(StudyResponse.answer, func.count())
        .join(StudyResults, StudyResults.id == StudyResponse.study_results_id)
        .where(StudyResults.study_id == study_id)
        .group_by(StudyResponse.answer)
    )
    answer_histogram = {int(a): int(c) for a, c in hist_rows}

    return {
        "study_id": study_id,
        "total_submissions": total_submissions,
        "expected_items": expected_items,
        "complete_submissions": comp,
        "completion_rate": round(completion_rate, 2),
        "avg_response_time_ms": avg_rt,
        "answer_histogram": answer_histogram,
    }


async def paged_results(conn: AsyncSession, study_id: UUID, page: int, page_size: int):
    # total
    total = await conn.scalar(
        select(func.count(StudyResults.id)).where(StudyResults.study_id == study_id)
    )
    total = int(total or 0)

    # page
    offset = max(page - 1, 0) * page_size
    base = (
        select(StudyResults.id, StudyResults.subject_id, StudyResults.submitted)
        .where(StudyResults.study_id == study_id)
        .order_by(StudyResults.submitted.desc())
        .limit(page_size)
        .offset(offset)
    )
    result_rows = (await conn.execute(base)).all()
    ids = [r.id for r in result_rows]

    # responses per result
    resp_map: Dict[UUID, list] = {rid: [] for rid in ids}
    if ids:
        resp_rows = await conn.execute(
            select(
                StudyResponse.study_results_id,
                StudyResponse.image_id,
                StudyResponse.answer,
                StudyResponse.response_time,
            )
            .where(StudyResponse.study_results_id.in_(ids))
            .order_by(StudyResponse.study_results_id)
        )
        for rid, image_id, answer, rt in resp_rows:
            resp_map[rid].append(
                {
                    "image_id": image_id,
                    "answer": int(answer),
                    "response_time": float(rt),
                }
            )

    items = [
        {
            "study_results_id": r.id,
            "subject_id": r.subject_id,
            "submitted": r.submitted,
            "responses": resp_map.get(r.id, []),
        }
        for r in result_rows
    ]
    return {"items": items, "page": page, "page_size": page_size, "total": total}


async def get_study_codes(conn: AsyncSession, researcher_id: UUID) -> list[str]:
    stmt = (
        select(StudyConfiguration.id)
        .join(Study)
        .where(Study.researcher == researcher_id)
    )
    res = await conn.execute(stmt)
    rows = res.scalars()
    study_codes = [str(config_id)[-6:] for config_id in rows]
    return study_codes


async def get_study_results_study_id(
    study_id: UUID, researcher_id: UUID, conn: AsyncSession
) -> list[StudyResponseSchema]:
    """Returns a list of study results based off the of the provided Study ID"""
    stmt = (
        select(StudyResults)
        .join(Study)
        .where(StudyResults.study_id == study_id, Study.researcher == researcher_id)
    )
    res = await conn.execute(stmt)
    rows = res.scalars()
    study_results = []
    for row in rows:
        study_results.append(
            StudyResultsSchema(
                id=row.id,
                study_id=row.study_id,
                subject_id=row.subject_id,
                submitted=row.submitted,
            )
        )
    return study_results


async def get_study_results_subject_id(
    subject_id: UUID, researcher_id: UUID, conn: AsyncSession
) -> StudyResponseSchema:
    stmt = (
        select(StudyResults)
        .join(Study)
        .where(StudyResults.subject_id == subject_id, Study.researcher == researcher_id)
    )
    res = await conn.execute(stmt)
    study_result = res.scalar_one_or_none()
    if not study_result:
        raise HTTPException(500, detail="Study Not Found")
    return study_result


async def get_all_study_results(
    researcher_id: UUID, conn: AsyncSession
) -> list[StudyResultsSchema]:
    stmt = (
        select(StudyResults)
        .join(Study)
        .where(
            Study.researcher == researcher_id,
        )
    )
    res = await conn.execute(stmt)
    rows = res.scalars()
    study_results = []
    for row in rows:
        study_results.append(
            StudyResultsSchema(
                id=row.id,
                study_id=row.study_id,
                subject_id=row.subject_id,
                submitted=row.submitted,
            )
        )
    return study_results


async def _validate_ownership(
    study_results_id: UUID, researcher_id: UUID, conn: AsyncSession
) -> StudyResultsSchema:
    stmt = (
        select(StudyResults)
        .join(Study)
        .where(StudyResults.id == study_results_id, Study.researcher == researcher_id)
    )
    res = await conn.execute(stmt)
    row = res.scalar_one_or_none()
    if not row:
        raise HTTPException(401, detail="Unathorized Access")
    return StudyResultsSchema(
        id=row.id,
        study_id=row.study_id,
        subject_id=row.subject_id,
        submitted=row.submitted,
    )


async def get_study_response_by_id(
    study_results_id: UUID, researcher_id: UUID, conn: AsyncSession
) -> StudyResponseSchema:
    study_result = await _validate_ownership(study_results_id, researcher_id, conn)
    if study_result:
        stmt = select(StudyResponse).where(
            StudyResponse.study_results_id == study_result.id
        )
        res = await conn.execute(stmt)
        rows = res.scalars()
        if not rows:
            raise HTTPException(500, detail="Responses not Found")
        study_responses:list[StudyResponseSchema] = []
        for response in rows:
            study_responses.append(
                StudyResponseSchema(
                    image_id=response.image_id,
                    answer=response.answer,
                    response_time=response.response_time,
                )
            )
        export_data = ResultsExportSchema(results=study_result, responses=study_responses)
        return export_data
