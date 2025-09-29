from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import delete, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.conclusion_config_model import ConclusionConfiguration
from models.study_model import Study
from models.study_result_model import StudyResults
from models.study_response_model import StudyResponse
from models.study_config_model import StudyConfiguration
from models.survey_answers_model import SurveyAnswer
from models.user_model import User
from schemas.const import TAIL_LEN
from schemas.researcher_dashboard_schema import (
    ResultsExportSchema,
    StudyResponseSchema,
    StudyResultsSchema,
    SurveyAnswerSchema,
)

async def get_config_id(researcher:UUID, studyCode:str, conn:AsyncSession) -> UUID:
    stmt = select(StudyConfiguration.id).join(Study).where(Study.researcher == researcher)
    res = await conn.execute(stmt)
    configs = res.scalars()
    config_id = [str(config) for config in configs if str(config)[-TAIL_LEN:] == studyCode]
    return config_id[0]


async def get_study_codes(conn: AsyncSession, researcher_id: UUID) -> list[str]:
    stmt = (
        select(StudyConfiguration.id)
        .join(Study)
        .where(Study.researcher == researcher_id)
    )
    res = await conn.execute(stmt)
    rows = res.scalars()
    study_codes = [str(config_id)[-TAIL_LEN:] for config_id in rows]
    return study_codes


async def get_study_results_study_id(
    study_id: UUID, researcher_id: UUID, conn: AsyncSession
) -> list[StudyResponseSchema]:
    """Returns a list of study results based off the of the provided Study ID"""
    stmt = (
        select(StudyResults)
        .join(Study)
        .join(StudyConfiguration)
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
                config_id=row.config_id,
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
        .join(StudyConfiguration)
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
                config_id=row.config_id,
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
        .join(StudyConfiguration)
        .where(StudyResults.id == study_results_id, Study.researcher == researcher_id)
    )
    res = await conn.execute(stmt)
    row = res.scalar_one_or_none()
    if not row:
        raise HTTPException(401, detail="Unathorized Access")
    return StudyResultsSchema(
        id=row.id,
        study_id=row.study_id,
        config_id=row.config_id,
        subject_id=row.subject_id,
        submitted=row.submitted,
    )


async def _check_for_survey(study_results_id: UUID, conn: AsyncSession):
    stmt = (
        select(ConclusionConfiguration.has_survey)
        .join(StudyConfiguration)
        .join(Study)
        .join(StudyResults)
        .where(StudyResults.id == study_results_id)
    )
    res = await conn.execute(stmt)
    has_survey = res.scalar_one_or_none()
    if not has_survey:
        raise HTTPException(500, detail="Unable to Find Conclusion Configuration")
    return has_survey


async def _get_demographics(subject_id: UUID, conn: AsyncSession):
    stmt = select(SurveyAnswer).where(SurveyAnswer.subject_id == subject_id)

    res = await conn.execute(stmt)
    demographics = res.scalar_one_or_none()
    if demographics:
        return SurveyAnswerSchema(
            subject_id=demographics.subject_id,
            age=demographics.age,
            sex=demographics.sex,
            race=demographics.race,
        )
    return demographics


async def get_study_response_by_id(
    study_results_id: UUID, researcher_id: UUID, conn: AsyncSession
) -> ResultsExportSchema:
    study_result = await _validate_ownership(study_results_id, researcher_id, conn)
    has_survey = _check_for_survey(study_results_id, conn)

    if has_survey:
        demographics = await _get_demographics(study_result.subject_id, conn)

    if study_result:
        stmt = select(StudyResponse).where(
            StudyResponse.study_results_id == study_result.id
        )
        res = await conn.execute(stmt)
        rows = res.scalars()
        if not rows:
            raise HTTPException(500, detail="Responses not Found")
        study_responses: list[StudyResponseSchema] = []
        for response in rows:
            study_responses.append(
                StudyResponseSchema(
                    image_id=response.image_id,
                    answer=response.answer,
                    response_time=response.response_time,
                )
            )
        if has_survey:
            return ResultsExportSchema(
                results=study_result,
                responses=study_responses,
                demographics=demographics,
            )
        return ResultsExportSchema(results=study_result, responses=study_responses)


async def get_all_study_responses(
    researcher_id: UUID, conn: AsyncSession
) -> list[ResultsExportSchema]:
    # Fetch List of Study Results
    stmt = (
        select(StudyResults)
        .join(Study)
        .where(
            Study.researcher == researcher_id,
        )
    )
    res = await conn.execute(stmt)
    rows = res.scalars()
    export_data = []
    for row in rows:
        export_data.append(await get_study_response_by_id(row.id, researcher_id, conn))
    return export_data


async def delete_study_config(config_id: UUID, researcher: UUID, conn: AsyncSession):
    try:
        _validate = exists().where(
            Study.id == StudyConfiguration.study_id,
            Study.researcher == researcher
        )
        stmt = (
            delete(StudyConfiguration)
            .where(StudyConfiguration.id == config_id,
                _validate)
        )
        await conn.execute(stmt)
        await conn.commit()
    except Exception as e:
        raise HTTPException(500, detail=str(e))


    stmt = select(StudyConfiguration).where(StudyConfiguration.id == config_id)
    res = await conn.execute(stmt)
    row = res.scalar_one_or_none()
    if row is not None:
            raise HTTPException(500, detail="Error Deleting Config")

async def delete_study_result(result_id: UUID, researcher: UUID, conn: AsyncSession):
    try:
        _validate = exists().where(
            Study.id == StudyResults.study_id,
            Study.researcher == researcher
        )
        stmt = (
            delete(StudyResults)
            .where(StudyResults.id == result_id,
                _validate)
        )
        await conn.execute(stmt)
        await conn.commit()
    except Exception as e:
        raise HTTPException(500, detail=str(e))


    stmt = select(StudyConfiguration).where(StudyConfiguration.id == result_id)
    res = await conn.execute(stmt)
    row = res.scalar_one_or_none()
    if row is not None:
            raise HTTPException(500, detail="Error Deleting Results")
    
async def get_researcher_id(email: str, conn: AsyncSession):
    stmt = select(User.id).where(User.email==email)
    res = await conn.execute(stmt)
    user_id = res.scalar_one_or_none()
    return user_id