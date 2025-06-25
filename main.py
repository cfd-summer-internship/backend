from fastapi import FastAPI
from routers.study_config_routes import router as ConfigRouter
import uvicorn as uv
import models

#Initialize FastAPI App
app = FastAPI()
#Connect Router
app.include_router(ConfigRouter)

@app.get("/")
def hello_world():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uv.run(app, host="0.0.0.0")

