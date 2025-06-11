from fastapi import FastAPI
from services.study import router as ConfigRouter
import uvicorn as uv

#Initialize FastAPI App
app = FastAPI()
#Connect Router
app.include_router(ConfigRouter)

@app.get("/")
def hello_world():
    return "Hello World"

if __name__ == "__main__":
    uv.run(app, host="0.0.0.0")
