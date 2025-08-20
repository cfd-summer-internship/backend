from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from routes.study_config_routes import router as ConfigRouter
from routes.study_retrieval_routes import router as RetrievalRouter
from routes.r2_routes import router as R2Router
from routes.study_results_router import router as StudyResultsRouter
from routes.auth_routes import auth_router as AuthRouter
from routes.user_routes import router as UserRouter
import uvicorn as uv
from fastapi.middleware.cors import CORSMiddleware
import models.all_models # noqa

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
    allow_origins=["http://localhost:3000", "http://frontend:3000", "http://plixel.tail8d155b.ts.net:3000"],
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
app.include_router(StudyResultsRouter)

@app.post("/")
async def echo(payload:dict):
    return {"received":payload}

@app.get("/")
def hello_world():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uv.run(app, host="0.0.0.0")

