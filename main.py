from fastapi import FastAPI
from routes.study_config_routes import router as ConfigRouter
from routes.study_retrieval_routes import router as RetrievalRouter
from routes.r2_routes import router as R2Router
from routes.study_results_router import router as StudyResultsRouter
from routes.survey_answer_routes import router as SurveyAnswerRouter
from routes.auth_routes import auth_router as AuthRouter
from routes.user_routes import router as UserRouter
from routes.researcher_routes import router as ResearcherRouter
from routes.staff_routes import router as StaffRouter
import uvicorn as uv
from fastapi.middleware.cors import CORSMiddleware
from settings import get_settings
import models.all_models  # noqa: F401

settings = get_settings()

# Initialize FastAPI App
app = FastAPI(
    root_path="/api",
    swagger_ui_parameters={
        "docExpansion":"none"
    }
)

app.router.redirect_slashes = False 

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_credentials=True,
    allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"],
    allow_headers=["Authorization","Content-Type"]
)

# Connect Router
app.include_router(AuthRouter)
app.include_router(UserRouter)
app.include_router(ConfigRouter)
app.include_router(RetrievalRouter)
app.include_router(R2Router)
app.include_router(ResearcherRouter)
app.include_router(StaffRouter)
app.include_router(StudyResultsRouter)
app.include_router(SurveyAnswerRouter)

@app.post("/")
async def echo(payload:dict):
    return {"received":payload}

@app.get("/")
def hello_world():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uv.run(app, host="0.0.0.0")

