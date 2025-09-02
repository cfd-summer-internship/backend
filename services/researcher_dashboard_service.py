from typing import List, Dict
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.study_model import Study
from models.study_result_model import StudyResults
from models.study_response_model import StudyResponse
from models.uploaded_files_model import UploadedFiles

async def _expected_items_for_config(conn: AsyncSession, config_id: UUID) -> int:
    row = await conn.execute(
        select(UploadedFiles.experiment_image_list).where(
            UploadedFiles.study_config_id == config_id
        )
    )
    arr = row.scalar_one_or_none()
    return len(arr or [])

async def list_studies_for_researcher(conn: AsyncSession, researcher_id: UUID) -> List[dict]:
    q = (
        select(
            Study.id,
            Study.configuration_id,
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
        items.append({
            "id": r.id,
            "configuration_id": r.configuration_id,
            "total_submissions": int(r.total or 0),
            "expected_items": int(exp_map.get(r.configuration_id, 0)),
            "last_submission_at": r.last_submitted,
        })
    return items

async def _ensure_ownership(conn: AsyncSession, study_id: UUID, researcher_id: UUID) -> None:
    ok = await conn.scalar(
        select(Study.id).where(Study.id == study_id, Study.researcher == researcher_id)
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Study not found")

async def summarize_study(conn: AsyncSession, study_id: UUID) -> dict:
    # total submissions + last submitted
    total_q = (
        select(
            func.count(StudyResults.id),
            func.max(StudyResults.submitted)
        ).where(StudyResults.study_id == study_id)
    )
    total_submissions, _ = (await conn.execute(total_q)).first() or (0, None)
    total_submissions = int(total_submissions or 0)

    # expected items
    cfg_id = await conn.scalar(select(Study.configuration_id).where(Study.id == study_id))
    expected_items = await _expected_items_for_config(conn, cfg_id) if cfg_id else 0

    # complete submissions: response count == expected_items
    comp = 0
    if expected_items > 0:
        per_result = (
            select(
                StudyResponse.study_results_id,
                func.count(StudyResponse.id).label("cnt")
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
        select(func.avg(StudyResponse.response_time)).join(
            StudyResults, StudyResults.id == StudyResponse.study_results_id
        ).where(StudyResults.study_id == study_id)
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
    total = await conn.scalar(select(func.count(StudyResults.id)).where(StudyResults.study_id == study_id))
    total = int(total or 0)

    # page
    offset = max(page - 1, 0) * page_size
    base = (
        select(StudyResults.id, StudyResults.subject_id, StudyResults.submitted)
        .where(StudyResults.study_id == study_id)
        .order_by(StudyResults.submitted.desc())
        .limit(page_size).offset(offset)
    )
    result_rows = (await conn.execute(base)).all()
    ids = [r.id for r in result_rows]

    # responses per result
    resp_map: Dict[UUID, list] = {rid: [] for rid in ids}
    if ids:
        resp_rows = await conn.execute(
            select(StudyResponse.study_results_id, StudyResponse.image_id, StudyResponse.answer, StudyResponse.response_time)
            .where(StudyResponse.study_results_id.in_(ids))
            .order_by(StudyResponse.study_results_id)
        )
        for rid, image_id, answer, rt in resp_rows:
            resp_map[rid].append({"image_id": image_id, "answer": int(answer), "response_time": float(rt)})

    items = [
        {
            "study_results_id": r.id,
            "subject_id": r.subject_id,
            "submitted": r.submitted,
            "responses": resp_map.get(r.id, [])
        }
        for r in result_rows
    ]
    return {"items": items, "page": page, "page_size": page_size, "total": total}
