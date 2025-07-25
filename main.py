from fastapi import FastAPI
from routes.study_config_routes import router as ConfigRouter
from routes.study_retrieval_routes import router as RetrievalRouter
from routes.r2_routes import router as R2Router
import uvicorn as uv
import models.all_models # noqa

# Initialize FastAPI App
app = FastAPI()
# Connect Router
app.include_router(ConfigRouter)
app.include_router(RetrievalRouter)
app.include_router(R2Router)

@app.get("/")
def hello_world():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uv.run(app, host="0.0.0.0")

