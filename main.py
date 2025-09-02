from fastapi import FastAPI
from routes.study_config_routes import router as ConfigRouter
from routes.study_retrieval_routes import router as RetrievalRouter
from routes.r2_routes import router as R2Router
from routes.study_results_router import router as StudyResultsRouter
from routes.survey_answer_routes import router as SurveyAnswerRouter
from routes.auth_routes import auth_router as AuthRouter
from routes.user_routes import router as UserRouter
import uvicorn as uv
import models.all_models # noqa

# Initialize FastAPI App
app = FastAPI(
    swagger_ui_parameters={
        "docExpansion":"none"
    }
)
# Connect Router
app.include_router(AuthRouter)
app.include_router(UserRouter)
app.include_router(ConfigRouter)
app.include_router(RetrievalRouter)
app.include_router(R2Router)
app.include_router(StudyResultsRouter)
app.include_router(SurveyAnswerRouter)

@app.get("/")
def hello_world():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uv.run(app, host="0.0.0.0")

